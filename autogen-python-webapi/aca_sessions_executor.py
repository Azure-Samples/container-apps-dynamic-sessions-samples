import requests
from typing import List
from azure.identity import DefaultAzureCredential
from autogen.coding import CodeBlock, CodeExecutor, CodeExtractor, CodeResult, MarkdownCodeExtractor

class ACASessionsExecutor(CodeExecutor):

    @property
    def code_extractor(self) -> CodeExtractor:
        return MarkdownCodeExtractor()

    def __init__(self, pool_management_endpoint: str) -> None:
        self.pool_management_endpoint = pool_management_endpoint
        self.access_token = None

    def ensure_access_token(self) -> None:
        if not self.access_token:
            credential = DefaultAzureCredential()
            scope = "https://dynamicsessions.io"
            self.access_token = credential.get_token(scope).token

    def execute_code_blocks(self, code_blocks: List[CodeBlock]) -> CodeResult:
        self.ensure_access_token()
        log = ""
        exitcode = 0
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        for code_block in code_blocks:
            properties = {
                "identifier": "adslfjlad",
                "codeInputType": "inline",
                "executionType": "synchronous",
                "pythonCode": code_block.code,
                "timeoutInSeconds": 100
            }

            try:
                response = requests.post(
                    self.pool_management_endpoint + "/python/execute",
                    headers=headers,
                    json={"properties": properties}
                )

                response.raise_for_status()
                data = response.json()
                log += data.get("stdout", "") + data.get("stderr", "")
                if "result" in data and data["result"] is not None:
                    log += str(data["result"])
                if "error" in data:
                    log += f"\n{data['error']}"
                    exitcode = 1
            except requests.RequestException as e:
                log += f"\nError while sending code block to endpoint: {str(e)}"
                exitcode = 1
                break

        return CodeResult(exit_code=exitcode, output=log)
