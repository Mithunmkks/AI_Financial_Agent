# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
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


# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================





# # Main function to use externally
# def analyze_stock_news(stock_name: str, max_results=3):
#     query = f"{stock_name} stock news"
#     news_items = fetch_clean_news(query=query, max_results=max_results)

#     results = []
#     for news in news_items:
#         result = get_sentiment_and_impact(news)
#         results.append(result)

#     # Sort by impact score descending
#     results.sort(key=lambda x: x.get("impact_score", 0), reverse=True)

#     return results




# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================

# ### ----------------------------- Imports ----------------------------- ###
# from .tools.roe import roe
# from .tools.roic import roic
# from .tools.get_prices import get_prices as get_prices
# from .tools.web_search import search_web
# from .tools.owner_earnings import owner_earnings
# from .tools.intrinsic_value import intrinsic_value
# from .tools.percentage_change import percentage_change
# from .tools.SearchLineItems import search_line_items
# from .tools.forecast_tool import forecast_prices

# from langgraph.prebuilt import ToolNode
# from langchain_community.tools import IncomeStatements, BalanceSheets, CashFlowStatements
# from langchain_community.utilities.financial_datasets import FinancialDatasetsAPIWrapper
# import datetime
# import json

# from typing import TypedDict, Annotated, Sequence
# import operator
# from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
# from langchain_openai.chat_models import ChatOpenAI
# from typing import Literal
# from langgraph.graph import END, StateGraph, MessagesState


# ### ----------------------------- Tool Setup ----------------------------- ###
# api_wrapper = FinancialDatasetsAPIWrapper()

# integration_tools = [
#     IncomeStatements(api_wrapper=api_wrapper),
#     BalanceSheets(api_wrapper=api_wrapper),
#     CashFlowStatements(api_wrapper=api_wrapper),
# ]

# local_tools = [
#     intrinsic_value, roe, roic, owner_earnings,
#     get_prices, percentage_change, search_line_items, search_web , forecast_prices
# ]

# tools = integration_tools + local_tools

# tool_node = ToolNode(tools)


# ### ----------------------------- Model & Prompt Setup ----------------------------- ###
# llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

# portfolio_prompt = f"""
# You are a portfolio recommendation assistant. The user will give you a list of stocks with their buy prices and quantities.

# For each stock:
# - Evaluate its performance using the tools provided (e.g., ROE, ROIC, intrinsic value, etc.)
# - Use current price data and financial fundamentals.
# - Recommend: BUY more, HOLD, or SELL.
# - Justify each recommendation in 1–2 lines.

# Also return:
# - Total portfolio value (based on current prices)
# - Total number of stocks

# Use precise numbers when available.
# Today's date is {datetime.date.today().strftime("%Y-%m-%d")}.
# """


# ### ----------------------------- Graph State ----------------------------- ###
# class AgentState(TypedDict):
#     messages: Annotated[Sequence[BaseMessage], operator.add]

# def should_continue(state: MessagesState) -> Literal["tools", "END"]:
#     messages = state["messages"]
#     last_message = messages[-1]

#     print("\n🔍 [DEBUG] Checking for tool calls...")
#     print("🔎 Last message content:", last_message.content)
#     print("🔎 Tool calls present?", hasattr(last_message, "tool_calls"), "→", last_message.tool_calls if hasattr(last_message, "tool_calls") else None)

#     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#         return "tools"
#     return END



# def call_portfolio_agent(state: MessagesState):
#     prompt = SystemMessage(content=portfolio_prompt)
#     messages = state["messages"]

#     if messages and messages[0].content != portfolio_prompt:
#         messages.insert(0, prompt)

#     print("\n🧠 [DEBUG] Calling LLM with:")
#     for m in messages:
#         print("👤" if isinstance(m, HumanMessage) else "📎", m.content)

#     llm_response = llm.invoke(messages)

#     print("🤖 [DEBUG] LLM Response:", llm_response.content)
#     print("🔧 Tool Calls:", getattr(llm_response, 'tool_calls', None))

#     return {"messages": [llm_response]}


# from langchain_core.messages import ToolMessage

# def call_output(state: MessagesState):
#     prompt = SystemMessage(content=portfolio_prompt)
#     messages = state["messages"]

#     tool_calls = None
#     updated_messages = []

#     # First extract the last AI message with tool calls
#     for m in messages:
#         if hasattr(m, "tool_calls") and m.tool_calls:
#             tool_calls = m.tool_calls
#             updated_messages.append(m)
#         elif m.type == "tool":
#             # Ensure tool_calls are present
#             if not tool_calls:
#                 raise ValueError("Tool call ID not found for tool message.")

#             # Try to find the matching tool call by tool name
#             tool_name = m.content.get("name") if isinstance(m.content, dict) and "name" in m.content else None
#             if not tool_name:
#                 # Fallback: extract from earlier tool_call
#                 tool_call = tool_calls.pop(0)
#                 tool_call_id = tool_call["id"]
#             else:
#                 tool_call_id = next((tc["id"] for tc in tool_calls if tc["name"] == tool_name), None)
#                 if not tool_call_id:
#                     raise ValueError(f"No matching tool_call found for tool '{tool_name}'")

#             # Append tool message with correct tool_call_id
#             updated_messages.append(ToolMessage(
#                 tool_call_id=tool_call_id,
#                 content=m.content if isinstance(m.content, str) else str(m.content)
#             ))
#         else:
#             updated_messages.append(m)

#     if updated_messages and updated_messages[0].content != portfolio_prompt:
#         updated_messages.insert(0, prompt)

#     # Final call to LLM with tools resolved
#     llm_response = llm.invoke(updated_messages)
#     print("✅ [DEBUG] Final LLM Answer:", llm_response.content)

#     return {"messages": [llm_response]}


# ### ----------------------------- Build the LangGraph Workflow ----------------------------- ###
# portfolio_workflow = StateGraph(MessagesState)
# portfolio_workflow.add_node("portfolio_agent", call_portfolio_agent)
# portfolio_workflow.add_node("tools", tool_node)
# portfolio_workflow.add_node("output", call_output)

# portfolio_workflow.set_entry_point("portfolio_agent")
# portfolio_workflow.add_conditional_edges("portfolio_agent", should_continue, {"tools": "tools", END: END})
# portfolio_workflow.add_edge("tools", "output")

# portfolio_app = portfolio_workflow.compile()


# ### ----------------------------- Run the Workflow ----------------------------- ###
# def ask_portfolio_agent(portfolio_json: dict) -> str:
#     portfolio_text = (
#     "Evaluate this portfolio:\n"
#     + "\n".join([
#         f"- {stock['ticker']}: {stock['quantity']} shares bought at ${stock['buy_price']}"
#         for stock in portfolio_json["portfolio"]
#     ])
# )

#     final_state = portfolio_app.invoke(
#         {"messages": [HumanMessage(content=portfolio_text)]},
#         config={"configurable": {"thread_id": 99}}
#     )

#     output = final_state["messages"][-1].content
#     print("\n=== RAW PORTFOLIO RESPONSE ===")
#     print(output)  # <-- 🔍 Check what the LLM actually returns
#     print("LLM Final Response:", output)
#     return output.strip()




# ### ----------------------------- Test Block ----------------------------- ###
# if __name__ == "__main__":
#     sample_portfolio = {
#         "portfolio": [
#             {"ticker": "AAPL", "buy_price": 175.50, "quantity": 30},
#             {"ticker": "TSLA", "buy_price": 205.80, "quantity": 12},
#             {"ticker": "JPM",  "buy_price": 155.30, "quantity": 16}
#         ]
#     }

#     result = ask_portfolio_agent(sample_portfolio)
#     print("\n===== Recommendation Output =====")
#     print(result)

# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================
