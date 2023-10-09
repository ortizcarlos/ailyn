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

from abc import ABC, abstractmethod
from exceptions.app_exceptions import InteractionException

class InteractionContext():

    def __init__(
            self,
            *,
            query:str,
            source_id:str,
            destination_id:str,
            audio_note_resorce_id=None,
            lang='es'):
        
        if not(query) and not(audio_note_resorce_id):
           raise InteractionException("Query is not optional")
        
        self._source_id      = source_id
        self._destination_id = destination_id
        self._audio_note_resource_id = audio_note_resorce_id
        self._query         = query
        self._stop_pipeline = False
        self._answer        = None
        self._language      = lang

    
    @property
    def query(self):
        return self._query
    
    @query.setter
    def query(self,value:str):
        self._query = value
    
    @property
    def audionote_resource(self):
        return self._audio_note_resource_id
    
    @property
    def source_id(self):
        return self._source_id
    
    @property
    def destination_id(self):
        return self._destination_id
    
    @property
    def answer(self):
        return self._answer
    
    @answer.setter
    def answer(self,answer):
        self._answer = answer

    @property
    def stop_pipeline(self):
        return self._stop_pipeline
        
    def finish_pipeline_processing(self):
        self._stop_pipeline = True
        
    
    @property
    def lang(self):
        return self._language
    

class InteractionHandler(ABC):

    @abstractmethod
    def handle(self,context:InteractionContext):
        pass