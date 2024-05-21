import os
import re

import dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from autogen import ConversableAgent, config_list_from_json
from aca_sessions_executor import ACASessionsExecutor

dotenv.load_dotenv()

app = FastAPI()

# Load autogen agent configurations from a JSON configuration list
config_list = config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={"model": ["gpt-4"]}
)

# Initialize the ConversableAgent for writing code
code_writer_agent = ConversableAgent(
    name="CodeWriter",
    system_message="You are a helpful AI assistant. You use your coding skill to solve problems. You have access to an IPython kernel to execute Python code. You output only valid python code. This valid code will be executed in a sandbox, resulting in result, stdout, or stderr. All necessary libraries have already been installed. Once the task is done, returns 'TERMINATE'.",
    llm_config={"config_list": config_list},
    is_termination_msg=lambda msg: "code output" in msg["content"]
)

# Endpoint for ACA session management, fetched from environment variables
aca_pool_management_endpoint = os.getenv("ACA_SESSIONS_ENDPOINT")
aca_sessions_executor = ACASessionsExecutor(aca_pool_management_endpoint)

# Initialize the CodeExecutor agent
code_executor_agent = ConversableAgent(
    name="CodeExecutor",
    llm_config=False,
    code_execution_config={"executor": aca_sessions_executor},
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", "").strip().upper()
)


@app.get("/")
async def root():
    return RedirectResponse("/docs")


@app.get("/chat")
async def chat(message: str):
    try:
        # Initiating chat between CodeExecutor and CodeWriter with the provided message
        chat_result = code_executor_agent.initiate_chat(
            code_writer_agent,
            message=message
        )
        # Find the last message containing 'Code output:' from assistant
        code_output_message = None
        for msg in reversed(chat_result.chat_history):
            if msg['role'] == 'assistant' and 'Code output:' in msg['content']:
                code_output_message = msg['content']
                break

        # Extract and round the value of 'Code output'
        if code_output_message:
            code_output_match = re.search(r'Code output:\s*(.*)', code_output_message)
            if code_output_match:
                code_output_value = code_output_match.group(1)
                # Further processing to extract and round the numeric part if necessary
                numeric_match = re.search(r'(\d+\.\d+)', code_output_value)
                if numeric_match:
                    rounded_value = round(float(numeric_match.group(1)), 2)
                    code_output_value = f"{rounded_value} mph"

        else:
            code_output_value = None  # If no Code output found

        # Convert chat_result to a dictionary
        chat_result_dict = {
            "chat_id": chat_result.chat_id,
            "chat_history": chat_result.chat_history,
            "summary": chat_result.summary,
            "cost": chat_result.cost,
            "human_input": chat_result.human_input,
        }

        return JSONResponse(content={"result": code_output_value, "chat_history": chat_result_dict})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
