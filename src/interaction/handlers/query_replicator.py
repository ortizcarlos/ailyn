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

import json

import infrastructure.llm.openai_wrapper  as oaiw

def generate_similar_queries(user_query:str) -> list:
  '''uses GPT to generate a list of related or similar questions using a user query'''

  prompt = '''
  You are an assistant for a Customer Service Interface.
  Generate a set of five search queries that are similar to this question.
  Use a variation of related keywords for the queries, trying to be as general as possible, including and excluding terms.
  For example, include queries like ['keyword_1 keyword_2', 'keyword_1', 'keyword_2'].
  Be creative. The more queries you include, the more likely you are to find relevant results.
  return JSON.
  
  expected format: {"queries": ["query_1", "query_2", "query_3"]}

  Answer in spanish.
  '''

  prompt += f'User question: {user_query}'
  result = oaiw.get_llm_response(prompt,max_tokens=200)
  return json.loads(result)['queries']


  
  
  