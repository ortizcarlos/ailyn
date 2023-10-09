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

import time
import logging
import sys
from   typing import Optional


from   application import ailyn
from   interaction.context import InteractionContext

rag_qa_pipeline = None

def handle_query(query:str):
    context = InteractionContext(query=query,
                                 source_id='source',
                                 destination_id='destination')
    start_time = time.time()
    answer     = rag_qa_pipeline.handle_query_interaction(context)
    end_time   = time.time()
    duration   = end_time - start_time
    
    return answer

# Run the FastAPI app
if __name__ == "__main__":
    
    if len(sys.argv) >= 2:
      ailyn.load(sys.argv[1])
    else:
      #Looks up for the default env file 'env.txt' in the current path
      ailyn.load()  

    rag_qa_pipeline = ailyn.new_qa_pipeline()

    while True:  
      user_query = input("Enter a query (or 'exit' to quit): ")
      if user_query.lower() == 'exit':
        print("Exiting the program.")
        break 
    
      # Process the user input
      print(handle_query(user_query))
  