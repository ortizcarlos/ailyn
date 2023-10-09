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

import requests
import uuid
from   pydub import AudioSegment

from interaction.context import InteractionHandler,InteractionContext
from audio.decoder       import AudioTranscriber

from   tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
) 

WAV = 'wav'

@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
def fetch_resource(
                resource_url:str,
                *,
                tmp_folder:str,
                convert_to_wav=False):
    
    audio_resource = requests.get(resource_url, allow_redirects=True)
    local_filepath = f"{tmp_folder}/{uuid.uuid4()}"
    
    with open(local_filepath, 'wb') as f: 
       f.write(audio_resource.content)
    
    if convert_to_wav:
      AudioSegment.from_file(local_filepath).export( local_filepath + '.' + WAV, format=WAV)
      local_filepath += '.' + WAV

    return local_filepath

class AudioHandler(InteractionHandler):

    def __init__(
            self,
            *,
            tmp_audio_folder:str,
            convert_to_wav=False
            ):
        self.transcriber      = AudioTranscriber()
        self.convert_to_wav   = convert_to_wav
        self.tmp_audio_folder = tmp_audio_folder

    def handle(self, context: InteractionContext):
        if context.audionote_resource:
            source_audio_filepath = context.audionote_resource
            transciption = self.transcriber.transcribe(
                          fetch_resource(
                              source_audio_filepath,
                              tmp_folder=self.tmp_audio_folder,
                              convert_to_wav=self.convert_to_wav))
            context.query = transciption