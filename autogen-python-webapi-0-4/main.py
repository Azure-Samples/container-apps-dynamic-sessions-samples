import os
import re
import tempfile

import dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.code_executors.azure import ACADynamicSessionsCodeExecutor
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

dotenv.load_dotenv()

app = FastAPI()

aca_pool_management_endpoint = os.getenv("POOL_MANAGEMENT_ENDPOINT")
openai_endpoint = os.getenv("OPENAI_ENDPOINT")
openai_deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

if not aca_pool_management_endpoint:
    raise ValueError("Environment variable POOL_MANAGEMENT_ENDPOINT is not set.")
if not openai_endpoint:
    raise ValueError("Environment variable OPENAI_ENDPOINT is not set.")
if not openai_deployment_name:
    raise ValueError("Environment variable OPENAI_DEPLOYMENT_NAME is not set.")

openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Set up model client based on API key or EntraID credentials
if openai_api_key:
    model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=openai_deployment_name,
        model="gpt-4o-2024-11-20",
        api_version="2024-06-01",
        azure_endpoint=openai_endpoint,
        api_key=openai_api_key,
    )
else:
    token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

    # https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html#azure-openai
    model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=openai_deployment_name,
        model="gpt-4o-2024-11-20",
        api_version="2024-06-01",
        azure_endpoint=openai_endpoint,
        azure_ad_token_provider=token_provider,
    )

# Set up the agent chat
# Use an assistant agent for writing code
# Use a code executor agent for executing code with the ACA sessions executor
code_agent = AssistantAgent(
    "code_agent",
    model_client=model_client,
    system_message="""Write Python script in markdown block, and it will be executed.
        Prefer outputting to the console but save images to a file in the current directory. Do not use plt.show(). All code required to complete this task must be contained within a single response.
        Reply only 'TERMINATE' if the task is done.""",
)

work_dir = tempfile.mkdtemp()
executor = ACADynamicSessionsCodeExecutor(
    work_dir=work_dir,
    pool_management_endpoint=aca_pool_management_endpoint,
    credential=DefaultAzureCredential()
)
executor_agent = CodeExecutorAgent(
    "executor_agent", code_executor=executor)

termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)
team = RoundRobinGroupChat(
    participants=[code_agent, executor_agent],
    termination_condition=termination,
)


@app.get("/")
async def root():
    return RedirectResponse("/docs")


@app.get("/chat")
async def chat(message: str):
    try:
        # Run the chat
        user_message = message
        result = None
        async for message in team.run_stream(task=user_message):
            if isinstance(message, TaskResult):
                result = message

        # extract the details from the result
        token_count = 0
        message_summaries = []
        code_output_value = ""
        for message in result.messages:
            if isinstance(message, TextMessage):
                message_summaries.append(
                    f"{message.source}: {message.content}")
                if message.source == "executor_agent":
                    code_output_value = message.content
                if message.models_usage:
                    token_count += message.models_usage.completion_tokens + \
                        message.models_usage.prompt_tokens

        chat_result_dict = {
            "messages": message_summaries,
            "total_tokens": token_count,
            "human_input": user_message,
            "output": code_output_value,
        }

        return JSONResponse(content={"result": code_output_value, "chat_history": chat_result_dict})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
