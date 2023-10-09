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

from abc import ABC,abstractmethod
from typing import List,Dict

import infrastructure.llm.openai_wrapper as oaiw

class Embeddings(ABC):
    @abstractmethod
    def __call__(sentences:List[str]):
        pass


class OpenAIEmbeddings(Embeddings):
    def __call__(self,sentences:List[str]):
        return oaiw.get_embeddings(sentences=sentences)


class SentenceTransformersEmbedings(Embeddings):

    def __init__(self,model_name:str):
        
        try:
            import sentence_transformers

        except ImportError as exc:
            raise ImportError(
                "The sentence_transformers python package is not installed. "
                "Please install it with `pip install sentence-transformers`."
            ) from exc
        
        self.model =  sentence_transformers.SentenceTransformer(model_name)

    def __call__(self,sentences:List[str])->List[List[float]]:
        return self.model.encode(sentences).tolist()



