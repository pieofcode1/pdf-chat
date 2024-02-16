# RAG Accelerator leveraging Azure OpenAI, AI Search & LangChain

Retrieval Augmented Generation (RAG) is a technique used in natural language processing to enhance the performance of chatbots and question-answering systems. It combines the power of retrieval-based models and generative models to provide more accurate and contextually relevant responses.

In the context of Azure, RAG can be implemented using Azure OpenAI, Azure Cognitive Search, and Azure LangChain. Azure OpenAI provides the language model capabilities, Azure Cognitive Search enables efficient indexing and retrieval of information, and Azure LangChain helps with language translation and understanding.

This accelarator app utilizes RAG for chatbot functionality. It demonstrates the power of Azure OpenAI and Cognitive services to extract the insights from variety of enterprise data sources such as PDF documents, Images, SQL Databases etc.

# Required Azure Services

- Azure OpenAI
- Azure Cognitive Search
- Azure Container Registry
- [Optional] Azure WebApps
- [Optional] SQL Database
- [Optional] Azure Bing Search 

# Tools

- Docker
- Python
- Git
- VS Code or any other Python IDE

# Running app in your local environment

## Create a new Python environment

`python -m venv <name_of_env>`

## Activate environment

`<name_of_env>\Scripts\activate`

## Dectivate environment

`<name_of_env>\Scripts\deactivate`

## Install the packages

Install the packages required for building the app from requirements.txt file.

`pip install -r .\requirements.txt`

In case you would like to use free version of HuggingFace Instructor Embeddings, you would require to install additional packages. Please bear in mind that you are running the model transformation on your laptop which ideally should run on GPUs.

`pip install InstructorEmbedding sentence_transformers`

In case you want to export your active environment to a new text file

`pip freeze > requirements.txt`

## Making Deployment Ready

Step 1: Build a docker image for the solution (Replace azure container registry URL with yours)
`docker build -f dockerfile -t dataplat.azurecr.io/aoai/pdf-chat-app:latest .`

Step 2: Push the image to Docker container registry. I am using Azure container registry. Please make sure you have configured your credentials on the maching you are pushing this image from.

`docker push dataplat.azurecr.io/aoai/pdf-chat-app:latest`

Step 3: Test locally before deploying this to Azure

`docker run -d -p 8501:8501 dataplat.azurecr.io/aoai/pdf-chat-app:latest`

## Running Locally

In order to run locally, follow the steps below:

Step 1: Create a local environment file by copying `.env` file from the root project directory and rename it to `.env.local`. Set all the parameter values from your Azure OpenAI or Public OpenAI deployment.

Step 2: Go to the root of the project and run this command `streamlit run app.py`. You will see the local URL displayed on the terminal to access the Webapp.
