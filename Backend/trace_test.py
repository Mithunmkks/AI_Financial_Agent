from dotenv import load_dotenv
load_dotenv()  # Load .env variables
from langchain_openai import ChatOpenAI
llm = ChatOpenAI()
llm.invoke("Hello, world!")


# this is test file for langsmith tracing Testing 
# it means that the environment variables are set up correctly and the OpenAI API is accessible.
## To run this test, execute the following command in the terminal:
# python trace_test.py