import datetime
import json
import operator
from typing import Literal, Sequence, TypedDict
from typing import Annotated

from langgraph.prebuilt import ToolNode
from langchain_community.tools import IncomeStatements, BalanceSheets, CashFlowStatements
from langchain_community.utilities.financial_datasets import FinancialDatasetsAPIWrapper
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.tools import Tool
from langgraph.graph import END, StateGraph

# Import custom tools
from .tools.forecast_tool import forecast_prices
from .tools.get_prices import get_prices
from .tools.intrinsic_value import intrinsic_value
from .tools.owner_earnings import owner_earnings
from .tools.percentage_change import percentage_change
from .tools.roe import roe
from .tools.roic import roic
from .tools.SearchLineItems import search_line_items
from .tools.web_search import search_web

# Tool registry (ensure each tool has name and description)
def wrap_tool(t):
    return Tool.from_function(func=t, name=getattr(t, "__name__", "custom_tool"), description=t.__doc__ or f"Tool for {getattr(t, '__name__', 'custom_tool')}")

wrapped_local_tools = [
    wrap_tool(t) for t in [
        intrinsic_value,
        roe,
        roic,
        owner_earnings,
        get_prices,
        percentage_change,
        search_line_items,
        search_web,
        forecast_prices
    ]
]

api_wrapper = FinancialDatasetsAPIWrapper()
integration_tools = [
    IncomeStatements(api_wrapper=api_wrapper),
    BalanceSheets(api_wrapper=api_wrapper),
    CashFlowStatements(api_wrapper=api_wrapper),
]

all_tools = integration_tools + wrapped_local_tools
tool_node = ToolNode(all_tools)

# LLM Setup
llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(all_tools)

# System prompt
portfolio_prompt = f"""
# **System Persona and Objective**
You are a sophisticated AI-powered Portfolio Recommendation Agent. Your primary objective is to provide expert financial analysis and actionable recommendations for a user's stock portfolio. You must be precise, data-driven, and adhere strictly to the output format specified below.

# **User Input Format**
A JSON object:
{{
  "portfolio": [
    {{"ticker": "STOCK_TICKER", "buy_price": 175.50, "quantity": 30}},
    ...
  ]
}}

# **Core Task**
For each stock:
1. Fetch `current_price`, `roe`, `roic`, `intrinsic_value`, `pe_ratio`.
2. Recommend: "BUY", "HOLD", or "SELL".
3. Justify using at least two metrics.

# **Output Format**
[
  {{
    "ticker": "STOCK_TICKER",
    "recommendation": "BUY|HOLD|SELL|INVALID_TICKER",
    "justification": "Reasoning",
    "metrics": {{
      "current_price": 180.00,
      "target_price": 200.00,
      "roe": 35.2,
      "pe_ratio": 28.5
    }}
  }}
]

# **Errors**
- If a ticker is invalid, return "INVALID_TICKER" with justification.
- Nullify any missing metric.
- No extra text.

# Critical Output Instructions:
- Your response MUST be pure JSON only
- Do NOT include any markdown syntax (```json or ```)
- Do NOT add any explanatory text
- The first and last characters of your response must be [ and ]

Current date: {datetime.date.today().strftime("%Y-%m-%d")}
"""

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    output: list  # Add this to store the parsed output

def should_continue(state: AgentState) -> Literal["tools", "output"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # If no tool calls, it means the LLM has generated its final response
    # or it's the initial call and no tools were needed.
    # In either case, we want to proceed to the 'output' node to process the final message.
    return "output"


def call_portfolio_agent(state: AgentState):
    messages = state["messages"]
    # Ensure the system prompt is always the first message
    if not messages or not isinstance(messages[0], SystemMessage) or messages[0].content != portfolio_prompt:
        messages.insert(0, SystemMessage(content=portfolio_prompt))
    response = llm.invoke(messages)
    return {"messages": [response]}


def call_output(state: AgentState):
    messages = state["messages"]
    
    # The goal of this function is to get the final JSON output from the LLM.
    # We need to pass the full conversation history, including tool outputs, to the LLM.
    # The LLM should then generate the final JSON based on the `portfolio_prompt`.

    # Filter out any duplicate system messages that might have been added by previous nodes
    # and ensure the system prompt is at the very beginning for the final LLM call.
    final_messages = [SystemMessage(content=portfolio_prompt)] + \
                     [m for m in messages if not isinstance(m, SystemMessage) or m.content != portfolio_prompt]

    print(f"\n✅ [DEBUG] Calling LLM for final output with {len(final_messages)} messages:")
    for m in final_messages:
        print(f"💬 {type(m).__name__}: {m.content}")

    llm_response = llm.invoke(final_messages)
    content = llm_response.content
    
    print(f"\n✅ [DEBUG] Raw LLM Final Answer: {content}")
    
    # Clean and parse the JSON output
    try:
        # Remove markdown code block wrappers if present
        if content.strip().startswith("```json"):
            content = content.strip()[len("```json"):].rsplit("```", 1)[0].strip()
        elif content.strip().startswith("```"):
            content = content.strip()[len("```"):].rsplit("```", 1)[0].strip()
        
        parsed = json.loads(content)
        return {"messages": [llm_response], "output": parsed}
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] Failed to parse LLM output. Error: {e}. Raw content:\n{content}")
        # If parsing fails, return an empty list for output and log the error
        return {"messages": [llm_response], "output": []}

portfolio_graph = StateGraph(AgentState)
portfolio_graph.add_node("portfolio_agent", call_portfolio_agent)
portfolio_graph.add_node("tools", tool_node)
portfolio_graph.add_node("output", call_output)
portfolio_graph.set_entry_point("portfolio_agent")
# Modified conditional edge to always go to 'output' if not calling tools
portfolio_graph.add_conditional_edges("portfolio_agent", should_continue, {"tools": "tools", "output": "output"})
portfolio_graph.add_edge("tools", "output")
portfolio_app = portfolio_graph.compile()

def ask_portfolio_agent(portfolio_json: dict):
    input_msg = HumanMessage(content=json.dumps(portfolio_json))
    final_state = portfolio_app.invoke(
        {"messages": [input_msg], "output": []},
        config={"configurable": {"thread_id": 99}}
    )
    
    if not final_state["output"]:
        print("\n[ERROR] No valid output generated. Last message content:")
        print(final_state["messages"][-1].content)
    
    return final_state["output"]

if __name__ == "__main__":
    portfolio = {
        "portfolio": [
            {"ticker": "AAPL", "buy_price": 175.50, "quantity": 30},
            {"ticker": "TSLA", "buy_price": 205.80, "quantity": 12},
            {"ticker": "JPM",  "buy_price": 155.30, "quantity": 16}
        ]
    }
    result = ask_portfolio_agent(portfolio)
    print("\n===== Final Recommendation =====")
    print(json.dumps(result, indent=2))


