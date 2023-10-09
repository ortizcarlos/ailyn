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
from   io import BytesIO
from   pathlib import Path

import docx
import fitz

class InvalidFileFormat(Exception):...

accepted_file_extensions = ('pdf','txt','docx')
PDF,TXT,DOCX             = accepted_file_extensions

PARAGRAPH_SEPARATOR = '\n'
PAGE_SEPARATOR      = '\n'

def validate_file_format(file_extension:str):
    if not  file_extension in accepted_file_extensions:
        raise InvalidFileFormat()
    
def _get_content_from_bytes_(bytes, extension):
    if extension == DOCX:
        text_content = extract_text_from_docx_file(bytes)
    elif extension == PDF:
        text_content = extract_text_from_pdf_file(bytes)
    return text_content

def extract_text_from_file(file_path:str):

    extension = file_path.split(".")[-1].lower()
    validate_file_format(extension)
    
    file_obj = Path(file_path)

    if extension in [DOCX,PDF]:
        with file_obj.open(mode='rb') as f:
            binary_data = f.read()
        bytes = BytesIO(binary_data)

    if extension == TXT:
        with file_obj.open() as f:
            file_text = f.read()
    else:
        file_text = _get_content_from_bytes_(bytes, extension)

    return file_text


def extract_text_from_docx_file(fileBytes):
    doc      = docx.Document(fileBytes)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return PARAGRAPH_SEPARATOR.join(fullText)


def extract_text_from_pdf_file(fileBytes):
    doc      = fitz.fitz.open("pdf", fileBytes)
    fullText = []
    for page in doc:
        fullText.append(page.get_text())
    return PAGE_SEPARATOR.join(fullText)