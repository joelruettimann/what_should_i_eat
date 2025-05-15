# import azure.functions as func
# import logging
# import base64
# from library.processing import handle_conversation
# import os
# import io
# from PIL import Image
# import uuid
# import open
prompt = '''
"You are a friendly and creative kitchen assistant.
You are passed an description of an image and asked to analyze it:

If it contains food or ingredients, suggest a dish that could be made using what you see and write a short recipe for it (including title, ingredients, steps, An estimate of total calories and macronutrients (protein, carbohydrates, fat) for the full dish).

If the image does not contain food (e.g. a table, chair, or unrelated object), respond humorously 
for example if the user is a beaver inspecting furniture, and give a playful warning like:
'Ahh, interesting! You must be a beaver. Remember, don’t chew more than half the table a day!
Or ahh you like iron, you must be a
Or another animal eating iron.
Or a cow eating gras.
Also include a fake, funny nutrition breakdown of the object, such as:
"Estimated calories: 800 kcal (mostly bark-based). Macros: 0g protein, 10g carbs (cellulose), 60g fat (wood oils).'

'''


import azure.functions as func
import logging
from pydantic import BaseModel
from typing import List
import json
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import base64


# Currently using the following model has to be replaced with the one above
model = ChatOpenAI(
    openai_api_key="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",
    model="gpt-4o",  # Specify the OpenAI model you want to use
    temperature=1.2
)



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

@app.route(route="process-image", methods=["POST"])
def process_image(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing image request.')

    try:
        # Get the image bytes from the request
        file = req.files.get("file")
        if not file:
            return func.HttpResponse("No file uploaded", status_code=400)

        # Generate unique filename
        unique_id = str(uuid.uuid4())
        original_filename = file.filename
        filename = f"{unique_id}_{original_filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Create folder if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Save file temporarily
        # Save file temporarily
        with open(file_path, "wb") as f:
            f.write(file.read())



        # Add the new user message
        with open(file_path, "rb") as image_file:
            image_base64 =  base64.b64encode(image_file.read()).decode('utf-8')

        # Example usage: Replace 'path/to/your/image.jpg' with the actual path to your image

        base64_data = "your_base64_string_here"  # Make sure it doesn't include the data prefix
        image_message = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpg;base64,{image_base64}"
            }
        }

        text_message = {
            "type": "text",
            "text": "Create an in deteailed description of the image descibe everything which is visible in the image. Includie quanties if possible"
        }

        # langchain_messages.append(
        #     HumanMessage(content=[text_message, image_message])
        # )
        #langchain_messages.append(HumanMessage(content="test"))

        # Get response from LLM
        ai_message_description = model([HumanMessage(content=[text_message, image_message])])

        prompt_for_suggestion = {
            "type": "text",
            "text": f'{prompt} This is the description {ai_message_description.content}'
        }

        ai_message = model([HumanMessage(content=prompt_for_suggestion["text"])])

        #ai_message = model(langchain_messages)
        messages =  [
            {"role": "user", "content": prompt_for_suggestion["text"]},
            {"role": "ai", "content": ai_message.content}
        ]

        prompt_for_suggestion = {
            "type": "text",
            "text": prompt
        }

        # Save the JSON dump including the image ID
        json_dump_path = os.path.join(UPLOAD_DIR, f"{unique_id}_data.json")
        with open(json_dump_path, "w") as json_file:
            json.dump({
                "image_id": unique_id,
                "description": ai_message_description.content,
                "suggestion": ai_message.content
            }, json_file)

        #os.remove(file_path)
        return func.HttpResponse(
            ChatResponse(
                response="",
                history=messages
            ).model_dump_json(),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        #os.remove(file_path)
        logging.error(f"Error processing image: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

import os
import uuid
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
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


        langchain_messages.append(HumanMessage(content=request.user_message))

        # Get response from LLM
        ai_message = model(langchain_messages)



        return func.HttpResponse(
            ChatResponse(
                response=ai_message.content,
                history=request.messages + [
                    {"role": "user", "content": request.user_message},
                    {"role": "ai", "content": ai_message.content}
                ]
            ).model_dump_json(),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error processing chat request: {e}")
        return func.HttpResponse("Internal Server Error", status_code=500)