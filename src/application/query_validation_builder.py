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
import json

from interaction.handlers.query_validation import QueryValidationHandler
from infrastructure.llm.query_cache        import LLMQueryCache

PROMPT_HEADER_KEY   = 'prompt_header'
VALID_QUERIES_KEY   = 'valid_queries'
INVALID_QUERIES_KEY = 'invalid_queries'

def new_query_validation_handler(
        validation_queries_filepath:str,
        llmCache:LLMQueryCache):
    

    if os.path.exists(validation_queries_filepath):
        with open(validation_queries_filepath,encoding='utf-8') as file:
            query_validation_json = file.read()
    else:
        raise EnvironmentError(f"Query validation samples file '{validation_queries_filepath}' not found!")  
    
    sample_queries = json.loads(query_validation_json)

    template          = sample_queries[PROMPT_HEADER_KEY]
    valid_questions   = sample_queries[VALID_QUERIES_KEY]
    invalid_questions = sample_queries[INVALID_QUERIES_KEY]

    for invalid,valid in zip(invalid_questions,valid_questions):
       template += f'question: {invalid}\nvalid = False\n'
       template += f'question: {valid}\nvalid = True\n'
       
    template += '\n\nquestion: {question}'

    return QueryValidationHandler(validation_prompt=template,llm_cache=llmCache)