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

import infrastructure.llm.openai_wrapper as oaiw
from   infrastructure.llm.core  import Embeddings
from   infrastructure.vector.database import VectorDatabase

from typing import List,Dict

THRESHOLD  = 0.85
ANSWER_KEY = 'answer'
QUERY_KEY  = 'query'
QUERY_CACHE_BATCH = 5

class LLMQueryCache():

    def __init__(
          self,
          *,
          cache_collection:str,
          vector_database: VectorDatabase,
          embbedings:Embeddings):
        self.embeddings = embbedings
        self.collection = cache_collection
        self.vector_database = vector_database

    def get_answer_from_cache(self,query):
        embedding_list   = self.embeddings([query]) 
        query_embeddings = embedding_list[0]
        results = self.vector_database.query(self.collection, 
                          query_embeddings, 
                          top_k=2)
        return self.get_best_candidate(results)
    
    def get_best_candidate(self,results, threshold=THRESHOLD):
        try:
          best_candidate = max(
             (item for item in results if item.score >= threshold), 
              key=lambda item: item.score)
          return best_candidate.payload[ANSWER_KEY]
        except ValueError:
          return None

    def put_in_cache(self,queries:List[str],answer):
         for index in range( 0 , len(queries), QUERY_CACHE_BATCH ):  
           slice          = queries[index:index+QUERY_CACHE_BATCH]
           embedding_list = self.embeddings(slice)
           metadata = [ {QUERY_KEY:query, ANSWER_KEY:answer} for query in slice]
           
           self.vector_database.save_batch(
                                 self.collection, 
                                 vector_list=embedding_list, 
                                 meta_batch=metadata)