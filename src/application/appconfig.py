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
import os
import logging

from jproperties import Properties

class Env():...
_env = Env()

configs = Properties()

QDRANT_LOCAL     = 'local'
QDRANT_SERVER    = 'url'

def _load(config_filepath:str):
    global configs
    
    with open(config_filepath, 'rb') as config_file:
       configs.load(config_file)     

    _env.query_cache_collection =  configs.get("query_cache_collection",'query_cache').data
    _env.rag_collection         =  configs.get("rag_collection", 'aileena_qa').data
    _env.rag_vector_dimension   =  int(configs.get("rag_vector_dimension", 1536).data) 
    _env.st_model               =  configs.get("st_model",'sentence-transformers/stsb-xlm-r-multilingual').data 
    _env.rag_prompt_filepath    =  configs.get("rag_prompt_filepath").data
   
    _env.telegram_bot_token     =  configs.get("telegram_bot_token").data
    _env.twilio_account_sid     =  configs.get("twilio_account_sid").data
    _env.twilio_auth_token      =  configs.get("twilio_auth_token").data
    _env.open_ai_key            =  configs.get("open_ai_key").data
    _env.cache_vector_dimension =  int(configs.get("cache_vector_dimension").data)
    _env.query_validation_filepath =  configs.get("query_validation_filepath").data
    _env.welcome_filepath       = configs.get("welcome_filepath").data
    _env.help_filepath          = configs.get("help_filepath").data
    _env.tmp_audio_folder       = configs.get("tmp_audio_folder").data
    _env.whatsapp_api_port      = int(configs.get("whatsapp_api_port",8080).data)

    qdrant_connection_str       = configs.get("qdrant_connection",'local|local_qdrant').data
    
    if '|' not in qdrant_connection_str:
        raise EnvironmentError('Invalid Qdrant connection configuration. example: local|qrant_local  ulr|localhost')
    
    connection_type,connection_str = qdrant_connection_str.split('|')

    if connection_type.lower() not in (QDRANT_LOCAL,QDRANT_SERVER) : 
        raise EnvironmentError('Invalid Qdrant connection type. Values (local,url). Example: local|qrant_local  ulr|localhost')

    _env.qdrant_connection_type =  connection_type
    _env.qdrant_connection      =  connection_str


def get_property(name:str,default=None):
    return configs.get(name,default).data

def openai_key():
    return _env.open_ai_key

def get_twilio_sid():
      return _env.twilio_account_sid

def get_twilio_token():
     return _env.twilio_auth_token

def load(env_file_path=None):
    if env_file_path:
       if os.path.exists(env_file_path):
          _load(env_file_path)
       else:
          raise EnvironmentError(f"Env file '{env_file_path}' not found!")  
    else:
      env_file_path = 'env.txt'
      if os.path.exists(env_file_path):
         _load(env_file_path) 
      else:
          raise EnvironmentError('No default env.txt file found!')