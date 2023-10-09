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

from interaction.context import InteractionContext,InteractionHandler,InteractionException
from interaction.context import InteractionContext
from exceptions.app_exceptions import InvalidQueryException

from infrastructure.llm.query_cache import LLMQueryCache

import infrastructure.llm.openai_wrapper as oaiw

INVALID = 'False'

ENGLISH = 'en'
SPANISH = 'es'

answer_map = {
   ENGLISH : 'Sorry, you have issued an out of context question',
   SPANISH : 'Lo siento, me has hecho una pregunta fuera del contexto de mis servicios.'
   }

DEFAULT_LANG = SPANISH

class QueryValidationHandler(InteractionHandler):

    def __init__(
          self,
          validation_prompt:str, 
          llm_cache:LLMQueryCache):
       self.prompt    = validation_prompt
       self.llm_cache = llm_cache

    def handle(self,context: InteractionContext):
       query             = context.query
       validation_prompt = self.prompt.format(question=query)
       answer            = oaiw.get_llm_response(validation_prompt)
    
       if INVALID in answer:
          context.finish_pipeline_processing()
          answer = answer_map.get (context.lang,answer_map[DEFAULT_LANG] )
          self.cache_answer( query , answer)
          raise InvalidQueryException(f"Invalid Query: {query}")
       
    def cache_answer(self,query:str,answer:str):
      try:
        self.llm_cache.put_in_cache([query],answer)
      except Exception as e:
        logging.error(f"Fail to cache answer",e)