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

from interaction.context import InteractionContext,InteractionException,InteractionHandler

from infrastructure.llm.query_cache import LLMQueryCache

class QueryCacheHandler(InteractionHandler):

    def __init__(self,chache:LLMQueryCache):
        self.llm_cache = chache

    def handle(self, context: InteractionContext):
        answer = self.llm_cache.get_answer_from_cache(context.query)
        if (answer):
            context.answer = answer
            context.finish_pipeline_processing()