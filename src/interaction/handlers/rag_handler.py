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

from interaction.context import InteractionException,InteractionContext,InteractionHandler
from infrastructure.llm.core import Embeddings
from infrastructure.vector.database import VectorDatabase
from interaction.context import InteractionContext
import infrastructure.llm.openai_wrapper as oaiw
from infrastructure.llm.query_cache import LLMQueryCache

import interaction.handlers.query_replicator as qr

MIN_EXPECTED_SIMILARITY_SCORE = 0.75

ENGLISH = 'en'
SPANISH = 'es'

answer_map = {
   ENGLISH : "Sorry, I don't have enough information to answer your question",
   SPANISH : 'Lo siento, actualmente no tengo suficiente información para contestar tu pregunta.'
   }

DEFAULT_LANG = SPANISH

class RAGQueryHandler(InteractionHandler):
   
   def __init__(self,
                *,
                embeddings:Embeddings,
                vector_db:VectorDatabase,
                collection_name:str,
                prompt:str,
                cache:LLMQueryCache):
      self.embeddings = embeddings
      self.vector_db  = vector_db
      self.collection = collection_name
      self.prompt = prompt
      self.cache  = cache
   
   
   def __retrieve_context_documents(self,query,top_k=3):
     query_emb =  self.embeddings([query])
     results   = self.vector_db.query(
                      self.collection,
                      query_emb[0],
                      top_k)
     return self.__filter_documents(results)
   

   def __filter_documents(self,results):   
      documents = [item.payload['doc'] for item in results if item.score >= MIN_EXPECTED_SIMILARITY_SCORE]
      print(f'context-lenght: {len(documents)}')
      return '' if len(documents)==0 else "\n".join(documents[0:10])

   
   def handle(self,context: InteractionContext):
      
      query = context.query
      retrieved_context = self.__retrieve_context_documents(query)
      
      if (len(retrieved_context)>0):
         prompt = self.prompt.format(context=retrieved_context,question=query)
         answer = oaiw.get_llm_response(prompt,max_tokens=300,temperature=0.1)
      else:
         answer = answer_map.get (context.lang ,answer_map[DEFAULT_LANG] )

      context.answer = answer
      self.cache_answer(query,answer)

   def cache_answer(self,query:str,answer:str):
     try:
        sim_queries = qr.generate_similar_queries(query)
        sim_queries.insert(0,query)
        self.cache.put_in_cache(sim_queries,answer)
     except Exception as e:
        logging.error(f"Failure caching similar queries",e)
   
