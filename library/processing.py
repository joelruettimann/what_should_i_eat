import azure.functions as func
import logging
from pydantic import BaseModel
from typing import List

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# 403 access denied error
# model = AzureChatOpenAI(
#     openai_api_version="2023-12-01-preview",
#     azure_deployment="gpt-4o-2024-08-06",
#     azure_endpoint="https://openai-aiattack-msa-002033-swedencentral-si-helixai-00.openai.azure.com/",
#     openai_api_key="DfC7qyFY8vuxjT3dqxmf2bZtdTzvfb0g7VOgvoJ9Q6jMa2EGG3qCJQQJ99BBACfhMk5XJ3w3AAABACOGqbQs"
# )


# Currently using the following model has to be replaced with the one above
model = ChatOpenAI(
    openai_api_key="openai_api_key",
    model="gpt-4",  # Specify the OpenAI model you want to use
    temperature=0.7)

class MessageBase(BaseModel):
    content: str

class SystemMessageModel(MessageBase):
    role: str = "system"

class UserMessageModel(MessageBase):
    role: str = "user"

class AIMessageModel(MessageBase):
    role: str = "ai"

class ChatRequest(BaseModel):
    messages: List[dict]
    user_message: str

class ChatResponse(BaseModel):
    response: str
    history: List[dict]



app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )


# here we will have an addtionl the argmuent: which chatbot. thi will then be sent to helix to determine which storage container to use   
@app.route(route="chat", methods=["POST"])
async def chat(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse the request body
        request_data = req.get_json()
        request = ChatRequest(**request_data)

        # Map input messages to LangChain's message schema
        role_to_message = {
            "system": SystemMessage,
            "user": HumanMessage,
            "ai": AIMessage
        }
        langchain_messages = [
            role_to_message[msg["role"]](content=msg["content"])
            for msg in request.messages
        ]

        # Add the new user message
        langchain_messages.append(HumanMessage(content=request.user_message))

        # Get response from LLM
        ai_message = model(langchain_messages)

        # Return the response directly
        return func.HttpResponse(
            ChatResponse(
                response=ai_message.content,
                history=request.messages + [
                    {"role": "user", "content": request.user_message},
                    {"role": "ai", "content": ai_message.content}
                ]
            ).json(),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing chat request: {e}")
        return func.HttpResponse("Internal Server Error", status_code=500)