# Welcome to Ailyn

Ailyn is a simple but powerful open-source virtual sales agent that uses Retrieval Augmented Generation (RAG) techniques to provide customer service and sales on various platforms such as WhatsApp and Telegram.

If you are new to RAG, you can use AIlyn to learn how to implement the main components 
of a "ChapGPT on your private data" application, including document embedding, retrieval,
response caching, and more.

So far, Ailyn implements question answering with the OpenAI completion API and query and document embeddings with Sentence Transformers and the OpenAI embeddings API.

## Features and dependencies

1. **OpenAI API**: Ailyn uses OpenAI APIs to provide the functionality of question answering and embeddings.
2. **Qdrant Vectorial Database**: This project uses Qdrant, a flexible, high-performance vector database.
3. **OpenAI Whisper**: Ailyn works with OpenAI Whisper for automated voice-to-text processing.
4. **LLM Responses Caching**: This functionality allows better response times and reduces operational costs.

Before starting, you must install Whisper following the instructions here: https://github.com/openai/whisper
   
## Getting Started

To start using Ailyn, clone this repository and install all the required dependencies.

## Contributing

As an open-source project, we would love for you to contribute. If you are interested in helping, check out our contribution guide to understand how you can contribute.

## License 

This project is under the Apache 2 License.

## Contact

For more information about the project, contact the development team, or if you have any questions, don't hesitate to contact me at carlosortizur@gmail.com.