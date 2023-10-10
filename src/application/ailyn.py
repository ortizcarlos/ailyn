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

import openai
from qdrant_client import QdrantClient

from infrastructure.twilio.mediator import TwilioMediator

from infrastructure.vector.database import VectorDatabase
from infrastructure.llm.query_cache import LLMQueryCache
from infrastructure.llm.core        import OpenAIEmbeddings, SentenceTransformersEmbedings

import application.appconfig  as appconfig
from application.query_validation_builder import new_query_validation_handler
from interaction.handlers.cache_handler   import QueryCacheHandler
from interaction.handlers.rag_handler     import RAGQueryHandler
from interaction.qa_pipeline              import QAPipeline
from interaction.handlers.audio_handler   import AudioHandler

_pipeline_func      = None
_channels_env       = appconfig.Env()
_vector_env         = appconfig.Env()

def load(envfile_path:str=None):

    global _pipeline_func,_vector_env 
    global _channels_env
    appconfig.load(envfile_path)

    rag_prompt_file = appconfig._env.rag_prompt_filepath
    qdrant          = QdrantClient( path= appconfig._env.local_qdrant_path )
    openai.api_key  =  appconfig.openai_key()

    rag_qdrant_client   = qdrant
    rag_vector_database = VectorDatabase.from_qdrant(rag_qdrant_client)
    rag_embeddings      = OpenAIEmbeddings()
    rag_collection      = appconfig._env.rag_collection

    cache_collection_name = appconfig._env.query_cache_collection
    cache_embeddings_model_name = appconfig._env.st_model
    cache_qdrant_client   = qdrant
    cache_vector_database = VectorDatabase.from_qdrant(cache_qdrant_client)
    cache_embeddings      = SentenceTransformersEmbedings(cache_embeddings_model_name)

    _vector_env.rag_vector_database   = rag_vector_database
    _vector_env.cache_vector_database = cache_vector_database
    _vector_env.cache_embeddings      = cache_embeddings
    _vector_env.rag_embeddings        = rag_embeddings
    _channels_env.telegram_bot_token  = appconfig._env.telegram_bot_token
    _channels_env.welcome_filepath    = appconfig._env.welcome_filepath
    _channels_env.help_filepath       = appconfig._env.help_filepath

    rag_cache = LLMQueryCache(
                        cache_collection=cache_collection_name,
                        vector_database =cache_vector_database,
                        embbedings=cache_embeddings)

    def load_prompt_file(filepath) -> str:
        prompt = ''
        with open( filepath ,'r' , encoding='utf-8') as prompt_file:
            for line in prompt_file:
                prompt += line
        return prompt

    _channels_env._twilioMediator       = TwilioMediator(appconfig.twilioSID,appconfig.twilioToken)

    def _qa_pipeline():
        
        audioHandler           = AudioHandler(
                                     tmp_audio_folder=appconfig._env.tmp_audio_folder)
        cacheHandler           = QueryCacheHandler(rag_cache)
        queryValidationHandler = new_query_validation_handler(
            appconfig._env.query_validation_filepath,
            rag_cache)
        ragHandler = RAGQueryHandler(
            embeddings=rag_embeddings,
            vector_db=rag_vector_database,
            collection_name=rag_collection,
            cache=rag_cache,
            prompt=load_prompt_file(rag_prompt_file)
        )
        qa_pipeline = QAPipeline(
            'RAGPipeline',
            audioHandler,
            cacheHandler,
            queryValidationHandler,
            ragHandler)
        
        return qa_pipeline
    _pipeline_func = _qa_pipeline
    

def new_qa_pipeline():
    return _pipeline_func()

def get_twilio_mediator():
    return _channels_env._twilioMediator

def get_whatsapp_api_port():
    return appconfig._env.whatsapp_api_port



