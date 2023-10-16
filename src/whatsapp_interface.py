"""
Copyright 2023 Carlos Ortiz Urshela

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import time
import logging
import sys
from   typing import Optional

import uvicorn
from   fastapi import FastAPI, File, Form,Response,Query,Request
from   fastapi.middleware.cors import CORSMiddleware

from   twilio.twiml.messaging_response import MessagingResponse

from   application import ailyn
from   interaction.context import InteractionContext
from   util.timing import timing

MAX_WAIT_MILISECONDS = 12000

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger          = logging.getLogger(__name__)

app  = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def pre_startup():
    global whatsapp_qa_pipeline,twilioMediator
    whatsapp_qa_pipeline = ailyn.new_qa_pipeline()
    twilioMediator       = ailyn.get_twilio_mediator()

@app.get("/bot-status")
async def bot_status():
    response = MessagingResponse() 
    response.message("OK")
    return Response(content=str(response), media_type="application/xml")

@timing
def run_qa_pipeline(context):
   return whatsapp_qa_pipeline.handle_query_interaction(context)


def isProcessable(form_data:dict,*,query,media_file):
   logger.info(f"query: [{query}] media_file:[{media_file}] ContentType: [{form_data.get('MediaContentType0','')}]'")
   if (form_data.get('MediaContentType0','') == 'image/jpeg'):
      return False
   
   return (query or media_file)
   
def trace_request(request,form_data:dict):
   logger.debug(f"Headers:           {request.headers}")
   logger.debug(f"Query Parameters:  {request.query_params}")
   logger.debug(f"Path Parameters:   {request.path_params}")
   for key in form_data:
       logger.debug(f'For-Variable [{key}] - Value [{form_data[key]}]')

@app.post('/bot-receiver')
async def bot_receiver(
                request: Request,
                To:str   = Form(...), 
                From:str = Form(...),
                Body:Optional[str]      = Form(''),
                MediaUrl0:Optional[str] = Form('')):
    
    response = MessagingResponse() 

    query       = Body.strip()
    media_resource  = MediaUrl0
    source      = From
    destination = To

    form_data = await request.form()

    if not(isProcessable(form_data,query=query,media_file=media_resource)):
       #The user sent an image or liked a message
       logger.debug('Interaction is not processable') 
       return

    context = InteractionContext(query          =query,
                                 source_id      =source,
                                 destination_id =destination,
                                 audio_note_resorce_id=media_resource)

    answer,duration = run_qa_pipeline(context)

    if duration > MAX_WAIT_MILISECONDS:
       '''
        The Twilio API waits a maximum of MAX_WAIT_MILISECONDS for a response.
        We have to send a direct response to the client when the request 
        processing took more than MAX_WAIT_MILISECONDS.
       '''
       logging.warning('A long LLM invocation detected')
       twilioMediator.send_msg( 
            From,
            To,
            answer)
    else:
        response.message(answer)
        return Response(content=str(response), media_type="application/xml")
    
def boot_app():
   if len(sys.argv) >= 2:
      ailyn.load(sys.argv[1])
   else:
      #Looks up for the default env file 'env.txt' in the current path
      ailyn.load()   




# Run the FastAPI app
if __name__ == "__main__":
   
   boot_app()
   uvicorn.run(
      app, 
      host= "0.0.0.0", 
      port= ailyn.get_whatsapp_api_port())
  