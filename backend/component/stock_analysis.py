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
import datetime

from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from langchain_openai.chat_models import ChatOpenAI
from typing import Literal
from langgraph.graph import END, StateGraph, MessagesState
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage


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
llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

# System prompt for financial analysis
system_prompt = f"""
You are an AI financial agent with expertise in analyzing businesses using methods similar to those of Warren Buffett...
The current date is {datetime.date.today().strftime("%Y-%m-%d")}
"""

### ----------------------------- Graph State ----------------------------- ###
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# Define the function that determines whether to continue or not
def should_continue(state: MessagesState) -> Literal["tools", "END"]:
    messages = state['messages']
    last_message = messages[-1]

    # Debug: Show what the model decided
    print("\n--- LLM Decision ---")
    print("Last LLM message:", last_message)
    
    if last_message.tool_calls:
        print("LLM decided to call a tool.")
        return "tools"
    
    print("LLM provided a final answer. Ending workflow.")
    return END

# Define the function that calls the model
def call_agent(state: MessagesState):
    prompt = SystemMessage(content=system_prompt)
    messages = state['messages']

    # Debug: Visualizing agent thinking
    print("\n--- Calling LLM Agent ---")
    for m in messages:
        if isinstance(m, HumanMessage):
            print("Human:", m.content)
        else:
            print("Previous Message:", m.content)

    if messages and messages[0].content != system_prompt:
        messages.insert(0, prompt)

    # Call the model
    llm_response = llm.invoke(messages)

    # Debug: Show LLM response
    print("LLM Response:", llm_response.content)
    if llm_response.tool_calls:
        print("Tool Calls:", llm_response.tool_calls)

    return {"messages": [llm_response]}

# Define a function that runs after tool execution
def call_output(state: MessagesState):
    prompt = SystemMessage(content=system_prompt)
    messages = state['messages']

    # Debug: Visualizing post-tool LLM reasoning
    print("\n--- Calling LLM for Final Output After Tool ---")
    for m in messages:
        if isinstance(m, HumanMessage):
            print("Human:", m.content)
        elif hasattr(m, 'tool_call_id'):
            print("Tool Output:", m.content)
        else:
            print("Message:", m.content)

    if messages and messages[0].content != system_prompt:
        messages.insert(0, prompt)

    llm_response = llm.invoke(messages)

    # Debug: Show LLM final output
    print("Final LLM Answer:", llm_response.content)

    return {"messages": [llm_response]}

### ----------------------------- Build the LangGraph Workflow ----------------------------- ###
workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_agent)
workflow.add_node("tools", tool_node)
workflow.add_node("output", call_output)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", END: END}
)

workflow.add_edge("tools", "output")

app = workflow.compile()

### ----------------------------- Run the Workflow ----------------------------- ###
def ask_agent(question: str) -> str:
    """
    Sends a question to the LangGraph app and returns the final response.
    """
    print("\n==========================")
    print("New Question Asked:", question)
    print("==========================")

    final_state = app.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": 42}}
    )

    output = final_state["messages"][-1].content
    return ' '.join(output.split())







# ### ----------------------------- Imports ----------------------------- ###
# from .tools.roe import roe
# from .tools.roic import roic
# from .tools.get_prices import get_prices
# from .tools.web_search import search_web
# from .tools.owner_earnings import owner_earnings
# from .tools.intrinsic_value import intrinsic_value
# from .tools.percentage_change import percentage_change
# from .tools.SearchLineItems import search_line_items


# from langgraph.prebuilt import ToolNode
# from langchain_community.tools import IncomeStatements, BalanceSheets, CashFlowStatements
# from langchain_community.utilities.financial_datasets import FinancialDatasetsAPIWrapper
# import datetime

# from typing import TypedDict, Annotated, Sequence
# import operator
# from langchain_core.messages import BaseMessage
# from langchain_openai.chat_models import ChatOpenAI
# from typing import Literal
# from langgraph.graph import END, StateGraph, MessagesState
# from langchain_core.messages import SystemMessage
# from langchain_core.messages import HumanMessage



# ### ----------------------------- Tool Setup ----------------------------- ###
# # Wrap external financial dataset API
# api_wrapper = FinancialDatasetsAPIWrapper()

# # External data tools
# integration_tools = [
#     IncomeStatements(api_wrapper=api_wrapper),
#     BalanceSheets(api_wrapper=api_wrapper),
#     CashFlowStatements(api_wrapper=api_wrapper),
# ]

# # Local tools
# local_tools = [
#     intrinsic_value, roe, roic, owner_earnings,
#     get_prices, percentage_change, search_line_items, search_web
# ]

# # Combine tools
# tools = integration_tools + local_tools

# # Tool handler node for LangGraph
# tool_node = ToolNode(tools)


# ### ----------------------------- Model & Prompt Setup ----------------------------- ###
# # Configure the OpenAI GPT-4 model
# llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

# # System prompt for financial analysis

# system_prompt = f"""
# You are an AI financial agent with expertise in analyzing businesses using methods similar to those of Warren Buffett. Your task is to provide short, accurate, and concise answers to questions about company financials and performance.

# You use financial tools to answer the questions.  The tools give you access to data sources like income statements, stock prices, etc.

# Here are a few example questions and answers:

# # Example 1:
# question: What was NVDA's net income for the fiscal year 2023?
# answer: The net income for NVDA in 2023 was $2.8 billion.

# # Example 2:
# question: How did NVDA's gross profit in 2023 compare to its gross profit in 2022?
# answer: In 2023, NVDA's gross profit increased by 12% compared to 2022.

# # Example 3:
# question: What was NVDA's revenue for the first quarter of 2024?,
# answer: NVDA's revenue for the first quarter of 2024 was $5.6 billion.

# Analyze these examples carefully. Notice how the answers are concise, specific, and directly address the questions asked. They provide precise financial figures and, when applicable, comparative analysis.

# When answering questions:
# 1. Focus on providing accurate financial data and insights.
# 2. Use specific numbers and percentages when available.
# 3. Make comparisons between different time periods if relevant.
# 4. Keep your answers short, concise, and to the point.

# Important: You must be short and concise with your answers.

# The current date is {datetime.date.today().strftime("%Y-%m-%d")}
# """

# ### ----------------------------- Graph State ----------------------------- ###
# class AgentState(TypedDict):
#     messages: Annotated[Sequence[BaseMessage], operator.add]


# # Define the function that determines whether to continue or not
# def should_continue(state: MessagesState) -> Literal["tools", "END"]:
#     messages = state['messages']
#     last_message = messages[-1]
#     # If the LLM makes a tool call, then we route to the "tools" node
#     if last_message.tool_calls:
#         return "tools"
#     # Otherwise, we stop (reply to the user)
#     return END

# # Define the function that calls the model
# def call_agent(state: MessagesState):
#     prompt = SystemMessage(
#         content=system_prompt
#     )
#     # Get the messages
#     messages = state['messages']

#     # Check if first message in messages is the prompt
#     if messages and messages[0].content != system_prompt:
#         # Add the prompt to the start of the message
#         messages.insert(0, prompt)

#     # We return a list, because this will get added to the existing list
#     return {"messages": [llm.invoke(messages)]}

# def call_output(state: MessagesState):
#     prompt = SystemMessage(
#         content=system_prompt
#     )
#     # Get the messages
#     messages = state['messages']

#     # Check if first message in messages is the prompt
#     if messages and messages[0].content != system_prompt:
#         # Add the prompt to the start of the message
#         messages.insert(0, prompt)
#     return {"messages": [llm.invoke(messages)]}

# ### ----------------------------- Build the LangGraph Workflow ----------------------------- ###
# workflow = StateGraph(MessagesState)

# # Define the two nodes we will cycle between
# workflow.add_node("agent", call_agent)
# workflow.add_node("tools", tool_node)
# workflow.add_node("output", call_output)

# # Set the entrypoint as agent
# # This means that this node is the first one called
# workflow.set_entry_point("agent")

# # We now add a conditional edge
# workflow.add_conditional_edges(
#     # First, we define the start node. We use agent.
#     # This means these are the edges taken after the agent node is called.
#     "agent",
#     # Next, we pass in the function that will determine which node is called next.
#     should_continue,
#     {"tools": "tools", END: END}
# )

# # We now add a normal edge from tools to agent.
# # This means that after tools is called, agent node is called next.
# workflow.add_edge("tools", "output")

# # Finally, we compile it!
# # This compiles it into a LangChain Runnable,
# # meaning you can use it as you would any other runnable.
# # Note that we're (optionally) passing the memory when compiling the graph
# app = workflow.compile()

# ### ----------------------------- Run the Workflow ----------------------------- ###
# # Use the Runnable
# def ask_agent(question: str) -> str:
#     """
#     Sends a question to the LangGraph app and returns the final response.
    
#     Args:
#         question (str): The user's input or query.
    
#     Returns:
#         str: The AI agent's final response.
#     """
#     final_state = app.invoke(
#         {"messages": [HumanMessage(content=question)]},
#         config={"configurable": {"thread_id": 42}}
#     )
    
#     output = final_state["messages"][-1].content
#     return ' '.join(output.split())


