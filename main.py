from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")
from typing import List, Optional, Dict, Any
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
import json
import os

class ChatMessage(BaseModel):
    role: str
    content: str

class SubRisk(BaseModel):
    riskClause: Optional[str] = None
    riskBrief: Optional[str] = None
    riskExplain: Optional[str] = None
    resultType: Optional[str] = None
    originalContent: Optional[str] = None
    resultContent: Optional[str] = None

class Result(BaseModel):
    examineResult: Optional[str] = None
    ruleTag: Optional[str] = None
    ruleTitle: Optional[str] = None
    examineBrief: Optional[str] = None
    riskLevel: Optional[str] = None
    subRisks: Optional[List[SubRisk]] = None
    ruleSequence: Optional[str] = None

class Output(BaseModel):
    result: Optional[Result] = None
    resultTaskId: Optional[str] = None

class Usage(BaseModel):
    input: int
    unit: str

class ResponseMessage(BaseModel):
    content: str

class ContractSection(BaseModel):
    Usage: Usage
    RequestId: str
    Output: Output
    Success: bool
    httpStatusCode: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    document_details: ContractSection



client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    output = await get_output()
    return templates.TemplateResponse("analysis.html", {"request": request, "output" : output})

def format_document_details(document_details):
    # Convert nested structure to readable string for the prompt
    lines = []
    for rule_title, items in document_details.items():
        lines.append(f"Rule: {rule_title}")
        for item in items:
            result = item.get("Output", {}).get("result", {})
            for k, v in result.items():
                lines.append(f"  {k}: {v}")
    return "\n".join(lines)

@app.get("/api/output")
async def get_output():
    output=[
        {
            "Usage": {
                "input": 0,
                "unit": "page"
            },
            "RequestId": "9056944B-5E3D-5204-9B58-31A57DD195BA",
            "Output": {
                "result": {
                    "examineResult": "此处无需修改",
                    "ruleTitle": "投标保证金要求,收取金额计算",
                    "examineBrief": "本任务为审查投标保证金要求,合同中未涉及投标保证金的具体条款。由于合同文本是关于工业手机M9的补充协议,主要涉及设备价格调整和售后服务承诺,并不涉及招标投标过程中的投标保证金。因此,合同文本在此方面不存在缺陷或风险,无需进行修改。",
                    "riskLevel": "normal",
                    "subRisks": [
                        {
                            "resultType": "通过"
                        }
                    ],
                    "ruleSequence": "2.1"
                },
                "resultTaskId": "ea524498-d7e6-4083-9b3f-410417950fc6"
            },
            "Success": True,
            "httpStatusCode": "200"
        },
        {
            "Usage": {
                "input": 0,
                "unit": "page"
            },
            "RequestId": "9056944B-5E3D-5204-9B58-31A57DD195BA",
            "Output": {
                "result": {
                    "examineResult": "需要修改",
                    "ruleTag": "审查合同的合法性",
                    "ruleTitle": "投标保证金要求,收取金额计算",
                    "examineBrief": "本任务为审查合同主体条款的信息完整性和主体资格的有效性。合同文本中仅提供了双方公司的名称,缺少详细的主体信息和主体资格的有效性证明,因此应当做如下修正,以避免潜在的法律风险。",
                    "riskLevel": "high",
                    "subRisks": [
                        {
                            "riskClause": "合同主体条款",
                            "riskBrief": "主体信息不完整",
                            "riskExplain": "合同文本中仅提供了双方公司的名称,但缺少详细的主体信息,如统一社会信用代码、法定代表人姓名、住所地等,可能导致法律风险。",
                            "resultType": "需修改",
                            "originalContent": "甲方:上海东普信息科技有限公司\n乙方:深圳市优博讯科技股份有限公司",
                            "resultContent": "甲方:上海东普信息科技有限公司,注册地址:上海市浦东新区XX路XX号,法定代表人:张伟,统一社会信用代码:91310000MA07FX2036,银行账户:6222020012345678901\n乙方:深圳市优博讯科技股份有限公司,注册地址:深圳市南山区XX路XX号,法定代表人:李华,统一社会信用代码:91440300MA07FX2037,银行账户:6222020012345678902"
                        },
                        {
                            "riskClause": "合同主体条款",
                            "riskBrief": "主体资格有效性未确认",
                            "riskExplain": "合同文本中未明确表示双方是否依法成立并有效存续,可能导致法律风险。",
                            "resultType": "需增加",
                            "originalContent": "甲方:上海东普信息科技有限公司\n乙方:深圳市优博讯科技股份有限公司",
                            "resultContent": "\n双方确认,甲方和乙方均为依法成立并有效存续的企业法人,具备签订本合同的主体资格。"
                        }
                    ],
                    "ruleSequence": "1.1"
                },
                "resultTaskId": "ea524498-d7e6-4083-9b3f-410417950fc6"
            },
            "Success": True,
            "httpStatusCode": "200"
        },
        {
            "Usage": {
                "input": 1,
                "unit": "page"
            },
            "RequestId": "9056944B-5E3D-5204-9B58-31A57DD195BA",
            "Output": {
                "result": {},
                "resultTaskId": "ea524498-d7e6-4083-9b3f-410417950fc6"
            },
            "Success": True,
            "httpStatusCode": "200"
        }
    ]
    return output

@app.post("/api/chat")
async def get_consultancy(request: ChatRequest):
    prompt =f"""You are an expert legal analyst and consultant.
    Given the following legal document and a history of a chat, perform the following tasks:
    1. Analyze the document
    2. answer the user's question based on the document.
    3. talk to the user in a friendly and professional manner, responding intuitively to their queries.
    Here is the legal document:\n\n{request.document_details.Output}\n\n
    Here is the chat history:\n\n{request.messages}
        """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ResponseMessage,
        },
    )
    message = json.loads(response.candidates[0].content.parts[0].text)
    return {"message": ChatMessage(role="AI consultant", content=message["content"])}