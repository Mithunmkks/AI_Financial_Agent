### ----------------------------- Imports ----------------------------- ###
from .tools.roe import roe
from .tools.roic import roic
from .tools.get_prices import get_prices
from .tools.web_search import search_web
from .tools.owner_earnings import owner_earnings
from .tools.intrinsic_value import intrinsic_value
from .tools.percentage_change import percentage_change
from .tools.SearchLineItems import search_line_items


from langgraph.prebuilt import ToolNode
from langchain_community.tools import IncomeStatements, BalanceSheets, CashFlowStatements
from langchain_community.utilities.financial_datasets import FinancialDatasetsAPIWrapper
from langchain.tools.render import format_tool_to_openai_function
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.graph import END, StateGraph, MessagesState

from typing import TypedDict, Annotated, Sequence, Literal
import operator
import datetime


### ----------------------------- Tool Setup ----------------------------- ###
# Wrap external financial dataset API
api_wrapper = FinancialDatasetsAPIWrapper()

# External data tools
integration_tools = [
    IncomeStatements(api_wrapper=api_wrapper),
    BalanceSheets(api_wrapper=api_wrapper),
    CashFlowStatements(api_wrapper=api_wrapper),
]

# Local tools
local_tools = [
    intrinsic_value, roe, roic, owner_earnings,
    get_prices, percentage_change, search_line_items, search_web
]

# Combine tools
tools = integration_tools + local_tools

# Tool handler node for LangGraph
tool_node = ToolNode(tools)


### ----------------------------- Model & Prompt Setup ----------------------------- ###
# Configure the OpenAI GPT-4 model
llm = ChatOpenAI(model="gpt-4.1", temperature=0).bind_tools(tools)

# System prompt for financial analysis
system_prompt = f"""
You are an AI financial agent with expertise in analyzing businesses using methods similar to those of Warren Buffett.
Your task is to provide short, accurate, and concise answers to questions about company financials and performance.

You use financial tools to answer the questions. The tools give you access to data sources like income statements, stock prices, etc.

Examples:
Q: What was NVDA's net income for the fiscal year 2023?
A: The net income for NVDA in 2023 was $2.8 billion.

Q: How did NVDA's gross profit in 2023 compare to 2022?
A: In 2023, NVDA's gross profit increased by 12% compared to 2022.

Q: What was NVDA's revenue for Q1 2024?
A: NVDA's revenue for the first quarter of 2024 was $5.6 billion.

Guidelines:
1. Provide accurate financial data.
2. Use specific figures and percentages.
3. Compare time periods when relevant.
4. Keep answers short and to the point.

The current date is {datetime.date.today().strftime("%Y-%m-%d")}.
"""


### ----------------------------- Graph State ----------------------------- ###
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


def should_continue(state: MessagesState) -> Literal["tools", "END"]:
    last_message = state['messages'][-1]
    route = "tools" if last_message.tool_calls else "END"
    print(f"\n🔀 should_continue routing to: {route}")
    return route

def call_agent(state: MessagesState):
    print("\n🧠 call_agent invoked")
    messages = state['messages']
    if not messages or messages[0].content != system_prompt:
        messages.insert(0, SystemMessage(content=system_prompt))
    response = llm.invoke(messages)
    print("🔍 LLM Response:", response)
    return {"messages": [response]}

def call_output(state: MessagesState):
    print("\n✅ call_output invoked")
    messages = state['messages']
    if not messages or messages[0].content != system_prompt:
        messages.insert(0, SystemMessage(content=system_prompt))
    response = llm.invoke(messages)
    print("📤 Final Output:", response)
    return {"messages": [response]}

### ----------------------------- Build the LangGraph Workflow ----------------------------- ###
workflow = StateGraph(MessagesState)

# Nodes
workflow.add_node("agent", call_agent)
workflow.add_node("tools", tool_node)
workflow.add_node("output", call_output)

# Entry point
workflow.set_entry_point("agent")

# Routing logic
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "output")

# Compile the workflow
app = workflow.compile()


### ----------------------------- Run the Workflow ----------------------------- ###
def ask_agent(question: str):
    print("\n==============================")
    print(f"🤔 Question: {question}")
    print("==============================")
    
    state = app.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": 42}}
    )
    
    response = state["messages"][-1].content
    print("\n📬 Response:", ' '.join(response.split()))
    return ' '.join(response.split())
 

# Example queries
ask_agent("What is the current price  for AAPL?")





