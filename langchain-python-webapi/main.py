import os
from azure.identity import DefaultAzureCredential
from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
from langchain_openai import AzureChatOpenAI
from langchain import agents, hub
from fastapi import FastAPI
import dotenv
from fastapi.responses import RedirectResponse

dotenv.load_dotenv()

app = FastAPI()

credential = DefaultAzureCredential()
os.environ["OPENAI_API_TYPE"] = "azure_ad"
os.environ["OPENAI_API_KEY"] = credential.get_token("https://cognitiveservices.azure.com/.default").token
pool_management_endpoint = os.getenv("POOL_MANAGEMENT_ENDPOINT")

@app.get("/")
async def root():
    return RedirectResponse("/chat?message=what is the current date and time?")

@app.get("/chat")
async def chat(message: str):
    llm = AzureChatOpenAI(
        azure_deployment="gpt-35-turbo",
        openai_api_version="2024-02-01",
        streaming=True,
        temperature=0,
    )

    repl = SessionsPythonREPLTool(
        pool_management_endpoint=pool_management_endpoint,
    )

    tools = [repl]
    react_agent = agents.create_react_agent(
        llm=llm,
        tools=tools,
        prompt=hub.pull("hwchase17/react"),
    )

    react_agent_executor = agents.AgentExecutor(
        agent=react_agent, tools=tools, verbose=True, handle_parsing_errors=True
    )

    response = react_agent_executor.invoke({"input": message})

    return response
