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
import re
from typing import List

def split_document( text: str,chunk_size = 1000 , stride = 700) -> List[str]:
    text =  " ".join(text.split()) #split by words removing \n and \n\n
    chunks = []
    text_length = len(text)

    # Iterate through the text with the specified stride
    for start in range(0, text_length, stride):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

    return chunks
