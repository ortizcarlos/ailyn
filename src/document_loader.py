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
import logging
import os
import sys
from   qdrant_client import QdrantClient
from typing import List,Dict

import application.appconfig  as appconfig
from   application import ailyn
from   util import (text,text_extractor)
from   infrastructure.llm.core        import OpenAIEmbeddings
from   infrastructure.vector.database import VectorDatabase


MINIBATCH_SIZE      = 3
DOCUMENT_CHUNK_SIZE = 1500
STRIDE              = 1200

def load_documents(
        directory_path:str, 
        acceptend_extensions,
        chunk_size, 
        stride) -> List[Dict]:
    
    """A generator that return document chuncks for each files in the directory"""

    files_in_directory = os.listdir(directory_path)

    # Filter files by the specified extension and process them
    for file_name in files_in_directory:
        extension = file_name.split('.')[-1]
        if extension in (acceptend_extensions):
            file_path  = os.path.join(directory_path, file_name)
            document   = text_extractor.extract_text_from_file(file_path)
            doc_chunks = text.split_document(document,chunk_size, stride)
            for doc in doc_chunks:
                yield dict(doc=doc,filename=file_name)

def recreate_retrieval_database( 
        directory_path:str, 
        *,
        acceptend_extensions,
        chunk_size=1200, 
        stride=700):
    
    ailyn._vector_env.cache_vector_database.create_collection(
         appconfig._env.query_cache_collection,
         appconfig._env.cache_vector_dimension)
  
    ailyn._vector_env.rag_vector_database.create_collection(
        appconfig._env.rag_collection,
        vector_dimension=  appconfig._env.rag_vector_dimension)

    metadata  = []
    doc_batch = [] 
    doc_count = 0
   
    for doc in load_documents(directory_path,acceptend_extensions,chunk_size,stride):
        metadata.append(doc)
        doc_batch.append(doc['doc'])
        if doc_count == MINIBATCH_SIZE:
            doc_count = 0
            ailyn._vector_env.rag_vector_database.save_batch(
                            collection  = appconfig._env.rag_collection,
                            vector_list = ailyn._vector_env.rag_embeddings(doc_batch),
                            meta_batch  = metadata)
            metadata  = []
            doc_batch = []
        else:   
            doc_count += 1

    if (len(metadata)>0):
        ailyn._vector_env.rag_vector_database.save_batch(
                            collection  =  appconfig._env.rag_collection,
                            vector_list =  ailyn._vector_env.rag_embeddings(doc_batch),
                            meta_batch=metadata)
        
def _boot_app():

    if len(sys.argv) ==1 :
      print("Usage: python document_loader.py [env filepath] data_folder")
      sys.exit(1)

    if len(sys.argv) > 2:
      ailyn.load(sys.argv[1])
      documents_folder = sys.argv[2]
    else:
      #Looks up for the default env file 'env.txt' in the current path
      ailyn.load()
      documents_folder = sys.argv[1] 
    
    return ( 
              documents_folder,
              int(ailyn.get_config_property('document_text_chunk_size',DOCUMENT_CHUNK_SIZE)),
              int(ailyn.get_config_property('document_text_stride',STRIDE))
              )



if __name__=='__main__':

    file_extensions  = text_extractor.accepted_file_extensions

    documents_folder,chunk_size,stride = _boot_app()
    if not(os.path.exists(documents_folder)): FileExistsError(f"Documents folder '{documents_folder}' not found!")  

    print(F'Processing files in folder {documents_folder}')

    recreate_retrieval_database(
        documents_folder,
        acceptend_extensions=file_extensions,
        chunk_size = chunk_size,
        stride     = stride )
    