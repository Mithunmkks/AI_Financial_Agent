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
from langgraph.graph import END, StateGraph

# Assuming these tools are available in your .tools directory
from .tools.forecast_tool import forecast_prices
from .tools.get_prices import get_prices
from .tools.intrinsic_value import intrinsic_value
from .tools.owner_earnings import owner_earnings
from .tools.percentage_change import percentage_change
from .tools.roe import roe
from .tools.roic import roic
from .tools.SearchLineItems import search_line_items
from .tools.web_search import search_web

### ----------------------------- Tool Setup ----------------------------- ###
api_wrapper = FinancialDatasetsAPIWrapper()

integration_tools = [
    IncomeStatements(api_wrapper=api_wrapper),
    BalanceSheets(api_wrapper=api_wrapper),
    CashFlowStatements(api_wrapper=api_wrapper),
]

local_tools = [
    intrinsic_value, roe, roic, owner_earnings,
    get_prices, percentage_change, search_line_items, search_web, forecast_prices
]

tools = integration_tools + local_tools

tool_node = ToolNode(tools)


### ----------------------------- Model & Prompt Setup ----------------------------- ###
llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

# Improved LLM Prompt for Portfolio Recommendation
portfolio_prompt = f"""
# **System Persona and Objective**
You are a sophisticated AI-powered Portfolio Recommendation Agent. Your primary objective is to provide expert financial analysis and actionable recommendations for a user's stock portfolio. You must be precise, data-driven, and adhere strictly to the output format specified below.

# **User Input Format**
You will receive a user's portfolio as a JSON object with the following structure:
```json
{{
  "portfolio": [
    {{"ticker": "STOCK_TICKER", "buy_price": 175.50, "quantity": 30}},
    ...
  ]
}}
```

# **Core Task: Portfolio Analysis and Recommendation**
For each stock in the user's portfolio, you must perform the following steps:

1.  **Data Retrieval:** Use the provided financial analysis tools to gather the following key metrics:
    -   `current_price`: Use the `get_prices` tool.
    -   `roe` (Return on Equity): Use the `roe` tool.
    -   `roic` (Return on Invested Capital): Use the `roic` tool.
    -   `intrinsic_value`: Use the `intrinsic_value` tool.
    -   `pe_ratio`: Search for the P/E ratio using the `search_web` tool if not available directly.

2.  **Recommendation Generation:** Based on your analysis of the retrieved metrics, formulate a recommendation for each stock. The recommendation must be one of the following: `"BUY"`, `"HOLD"`, or `"SELL"`.

3.  **Justification:** Provide a concise, data-driven justification for your recommendation in 1-2 sentences. Your justification should reference at least two of the key metrics you retrieved.

# **Output Format: Strict JSON Structure**
Your final output MUST be a single, valid JSON array of objects. Each object in the array represents a recommendation for a single stock and must conform to the following structure:

```json
[
  {{
    "ticker": "STOCK_TICKER",
    "recommendation": "BUY|HOLD|SELL",
    "justification": "Your concise, data-driven justification for the recommendation.",
    "metrics": {{
      "current_price": 180.00,
      "target_price": 200.00, // You can use intrinsic_value as a proxy for target_price
      "roe": 35.2,
      "pe_ratio": 28.5
    }}
  }}
]
```

# **Error Handling and Edge Cases**
-   If you cannot find information for a specific stock ticker, you must still include it in your response but with a `recommendation` of `"INVALID_TICKER"` and a `justification` explaining that the ticker could not be found.
-   If a specific metric cannot be retrieved for a valid ticker, represent its value as `null` in the `metrics` object.

# **Important Constraints**
-   Do not include any introductory or concluding text outside of the JSON array.
-   Ensure all numerical values are represented as numbers, not strings.
-   The current date is: **{datetime.date.today().strftime("%Y-%m-%d")}**.

"""


### ----------------------------- Graph State ----------------------------- ###
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def should_continue(state: AgentState) -> Literal["tools", "END"]:
    messages = state["messages"]
    last_message = messages[-1]

    print("\n🔍 [DEBUG] Checking for tool calls...")
    print("🔎 Last message content:", last_message.content)
    print("🔎 Tool calls present?", hasattr(last_message, "tool_calls"), "→", last_message.tool_calls if hasattr(last_message, "tool_calls") else None)

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END



def call_portfolio_agent(state: AgentState):
    prompt = SystemMessage(content=portfolio_prompt)
    messages = state["messages"]

    if messages and messages[0].content != portfolio_prompt:
        messages.insert(0, prompt)

    print("\n🧠 [DEBUG] Calling LLM with:")
    for m in messages:
        print("👤" if isinstance(m, HumanMessage) else "📎", m.content)

    llm_response = llm.invoke(messages)

    print("🤖 [DEBUG] LLM Response:", llm_response.content)
    print("🔧 Tool Calls:", getattr(llm_response, 'tool_calls', None))

    return {"messages": [llm_response]}



def call_output(state: AgentState):
    prompt = SystemMessage(content=portfolio_prompt)
    messages = state["messages"]

    tool_calls = None
    updated_messages = []

    # First extract the last AI message with tool calls
    for m in messages:
        if hasattr(m, "tool_calls") and m.tool_calls:
            tool_calls = m.tool_calls
            updated_messages.append(m)
        elif m.type == "tool":
            # Ensure tool_calls are present
            if not tool_calls:
                raise ValueError("Tool call ID not found for tool message.")

            # Try to find the matching tool call by tool name
            tool_name = m.content.get("name") if isinstance(m.content, dict) and "name" in m.content else None
            if not tool_name:
                # Fallback: extract from earlier tool_call
                tool_call = tool_calls.pop(0)
                tool_call_id = tool_call["id"]
            else:
                tool_call_id = next((tc["id"] for tc in tool_calls if tc["name"] == tool_name), None)
                if not tool_call_id:
                    raise ValueError(f"No matching tool_call found for tool \'{tool_name}\'")

            # Append tool message with correct tool_call_id
            updated_messages.append(ToolMessage(
                tool_call_id=tool_call_id,
                content=m.content if isinstance(m.content, str) else str(m.content)
            ))
        else:
            updated_messages.append(m)

    if updated_messages and updated_messages[0].content != portfolio_prompt:
        updated_messages.insert(0, prompt)

    # Final call to LLM with tools resolved
    llm_response = llm.invoke(updated_messages)
    print("✅ [DEBUG] Final LLM Answer:", llm_response.content)

    return {"messages": [llm_response]}


### ----------------------------- Build the LangGraph Workflow ----------------------------- ###
portfolio_workflow = StateGraph(AgentState)
portfolio_workflow.add_node("portfolio_agent", call_portfolio_agent)
portfolio_workflow.add_node("tools", tool_node)
portfolio_workflow.add_node("output", call_output)

portfolio_workflow.set_entry_point("portfolio_agent")
portfolio_workflow.add_conditional_edges("portfolio_agent", should_continue, {"tools": "tools", END: END})
portfolio_workflow.add_edge("tools", "output")

portfolio_app = portfolio_workflow.compile()


### ----------------------------- Run the Workflow ----------------------------- ###
def ask_portfolio_agent(portfolio_json: dict) -> str:
    portfolio_text = portfolio_text = json.dumps(portfolio_json)



    final_state = portfolio_app.invoke(
        {"messages": [HumanMessage(content=portfolio_text)]},
        config={"configurable": {"thread_id": 99}}
    )

    output = final_state["messages"][-1].content
    print("\n=== RAW PORTFOLIO RESPONSE ===")
    print(output)  # <-- 🔍 Check what the LLM actually returns

    try:
        # Attempt to parse the LLM's string output as JSON
        parsed_output = json.loads(output)
        # You might want to add validation here to ensure the structure matches expectations
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from LLM: {e}")
        print(f"LLM output that caused error: {output}")
        # Return an empty list or a specific error structure if JSON parsing fails
        parsed_output = [] 

    print("LLM Final Response (Parsed):", parsed_output)
    return parsed_output




### ----------------------------- Test Block ----------------------------- ###
if __name__ == "__main__":
    sample_portfolio = {
        "portfolio": [
            {"ticker": "AAPL", "buy_price": 175.50, "quantity": 30},
            {"ticker": "TSLA", "buy_price": 205.80, "quantity": 12},
            {"ticker": "JPM",  "buy_price": 155.30, "quantity": 16}
        ]
    }

    result = ask_portfolio_agent(sample_portfolio)
    print("\n===== Recommendation Output =====")
    print(result)


