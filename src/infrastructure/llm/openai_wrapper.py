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
import logging
import openai
from   time     import sleep
from   tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
) 

EMBEDDINGS_MODEL      = "text-embedding-ada-002"
CHAT_COMPLETION_MODEL = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS    = 250

def set_openai_key(key:str):
     openai.api_key = key

@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
def get_embeddings(sentences:list) -> list:
    try:
        response = openai.Embedding.create(
            input=sentences, 
            engine=EMBEDDINGS_MODEL)
    except:
        done = False
        while not done:
            sleep(5)
            try:
                response = openai.Embedding.create(
                    input=sentences, 
                    engine=EMBEDDINGS_MODEL)
                done = True
            except:
                pass
            
    embeds = [record['embedding'] for record in response['data']]
    return embeds

@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
def get_llm_response(
        prompt, 
        * ,
        completion_model:str = CHAT_COMPLETION_MODEL, 
        max_tokens:int       = DEFAULT_MAX_TOKENS, 
        temperature:float    = 0.7):
    
    response = openai.ChatCompletion.create(
              model    = completion_model,
              messages = [
                   {"role": "user", "content": prompt}
              ],
              max_tokens = max_tokens,
              temperature=temperature
    )
    result = ''
    
    for choice in response.choices:
       result += choice.message.content

    return result

