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

from  typing import List, Dict
from  qdrant_client import QdrantClient
from  infrastructure.vector.store_common import VectorStorageException,QdrantStore,VectorStore

'''
Main class to interact with the Vector Database.
'''
class VectorDatabase:

    def __init__(self , vector_store:VectorStore) -> None:
        self.store = vector_store
        
    def from_qdrant(qdrant_client:QdrantClient):
        return VectorDatabase(vector_store = QdrantStore(qdrant_client))
    
    def create_collection(
          self, 
          collection_name :str, 
          vector_dimension:int):
        self.store.create_collection(collection_name,vector_dimension)

    def save_single( 
            self,
            collection:str, 
            vector:List, 
            metadata:Dict):
        self.store.save_vector_batch(
            collection,
            vectors  = [vector],
            metadata = metadata)

    def save_batch(self, collection:str, vector_list:List[List],meta_batch:List[Dict]):
        if len(vector_list) != len(meta_batch):
            raise VectorStorageException("Vector list and Metadata list must have the same size")
        self.store.save_vector_batch(
            collection,
            vector_list,
            meta_batch)

    def query(self,collection,query_embeddings:List,top_k=5) -> list:   
        return self.store.query(
            collection,
            query_embeddings=query_embeddings,
            top_k=top_k)

