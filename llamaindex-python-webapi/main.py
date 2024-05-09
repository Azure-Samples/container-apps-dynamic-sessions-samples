from datetime import datetime, timedelta, timezone
import os
from azure.identity import DefaultAzureCredential
from fastapi import FastAPI
import dotenv
from fastapi.responses import RedirectResponse
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.tools.azure_code_interpreter import AzureCodeInterpreterToolSpec
from llama_index.core.agent import ReActAgent

dotenv.load_dotenv()

app = FastAPI()

pool_management_endpoint = os.getenv("POOL_MANAGEMENT_ENDPOINT")


@app.get("/")
async def root():
    return RedirectResponse("/docs")


@app.get("/chat")
async def chat(message: str):
    cached_token = None
    credential = DefaultAzureCredential()
    def azure_ad_token_provider():
        nonlocal cached_token
        if not cached_token or datetime.fromtimestamp(cached_token.expires_on, timezone.utc) < (datetime.now(timezone.utc) + timedelta(minutes=5)):
            cached_token = credential.get_token("https://cognitiveservices.azure.com/.default")
        return cached_token.token

    llm = AzureOpenAI(
        model="gpt-35-turbo",
        deployment_name="gpt-35-turbo",
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version="2024-02-01",
        azure_ad_token_provider=azure_ad_token_provider,
        use_azure_ad=True,
    )

    code_interpreter_tool = AzureCodeInterpreterToolSpec(
        pool_managment_endpoint=pool_management_endpoint,
    )
    agent = ReActAgent.from_tools(code_interpreter_tool.to_tool_list(), llm=llm, verbose=True)
    chat_response = agent.chat(message)

    response = {
        "output": chat_response.response,
    }

    return response
