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
from abc import ABC, abstractmethod
from typing import List,Dict

from exceptions.app_exceptions import LLMInvocationException,InvalidQueryException
from interaction.context       import InteractionContext,InteractionHandler,InteractionException



INVALID_QUERY_DEFAULT_RESPONSE = 'Lo siento, me has hecho una pregunta que está fuera del contexto de mis servicios.'
LLM_ERROR_DEFAULT_RESPONSE     = 'Lo siento, ha ocurrido un error al atender tu respuesta, por favor intenta nuevamente'
DEFAULT_ERROR_RESPONSE         = 'Ups, ocurrio un error. Intenta nuevamente'

class QAPipeline(ABC):

    def __init__(
          self,
          name,
          *handlers,
          **kwargs):
       
       self.name         = name
       self.handler_list = [ handler for handler in handlers if isinstance(handler,InteractionHandler) ]

       self.invalid_query_response = kwargs.get(
          'default_invalid_query_response' ,
          INVALID_QUERY_DEFAULT_RESPONSE)
       
       self.llm_error_response = kwargs.get(
          'default_llm_error_response' ,
          LLM_ERROR_DEFAULT_RESPONSE)
       
       self.unexpected_error_response = kwargs.get(
          'unexpected_llm_error_response' ,
          DEFAULT_ERROR_RESPONSE)
   

    def handle_query_interaction(self,context:InteractionContext): 
     
        
        for handler in self.handler_list:
           print(handler,context.query)
           try:
             handler.handle(context)
             if context.stop_pipeline:
                answer = context.answer
                break
           except InvalidQueryException as iqe:
             answer =  self.invalid_query_response
             break
           except LLMInvocationException as e:
             answer = self.llm_error_response
             logging.error(e)
             break
           except Exception as e:  
            answer = self.unexpected_error_response
            logging.error(e)
            break       
        else:
           answer = context.answer
        
        return answer 
    

