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

import uuid

from typing import List, Dict
from abc import ABC,abstractmethod
from  qdrant_client import QdrantClient
from  qdrant_client.http import models


class VectorStorageException(Exception): ...

class VectorStore(ABC):
   
   @abstractmethod
   def create_collection(
          self, 
          collection_name :str, 
          vector_dimension:int):
      pass
   
   @abstractmethod
   def save_vector_batch(
      self, 
      collection_name, 
      vectors: List[List], 
      metadata: List[Dict] , 
      idfunc:None):
      pass
   
   @abstractmethod
   def query(
         self,
         collection: str,
         query_embeddings: List, 
         top_k=5)-> list:
      pass
   

class QdrantStore(VectorStore):

    def __init__(self, client:QdrantClient):
        self.client = client

    def create_collection(
          self, 
          collection_name:str, 
          vector_dimension:int
          ):
       distance_method = models.Distance.COSINE
       # Create a collection in Qdrant
       self.client.recreate_collection(
              collection_name = collection_name,
              vectors_config  = models.VectorParams(
                        size            = vector_dimension,
                        distance        = distance_method
                      )
        )

    def save_vector_batch(
          self, 
          collection_name, 
          vectors:  List[List], 
          metadata: List[Dict], 
          idfunc=None):
       
       if len(vectors) != len(metadata):
         raise VectorStorageException("Vector list and Metadata list must have the same size")
          
       points = []
       if (idfunc==None): idfunc = lambda x: str(uuid.uuid4())
       for embedding, metainfo in zip(vectors, metadata):
          points.append(models.PointStruct(
               id      = idfunc(metainfo),
               payload = metainfo,
               vector  = embedding,
            ) 
          )

       self.client.upsert( collection_name=collection_name, points=points)

    def query(
          self,
          collection: str,
          query_embeddings: List,
          top_k=5)-> list:
       return self.client.search(
                             collection_name = collection,
                             query_vector    = query_embeddings,
                             limit           = top_k)


