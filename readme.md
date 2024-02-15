# PDF-chatbot application using LangChain

Application code for Chatbot created using OpenAI with your own PDF files

## Create a new Python environment

`python -m venv <name_of_env>`

## Activate environment

`<name_of_env>\Scripts\activate`

## Dectivate environment

`<name_of_env>\Scripts\deactivate`

## Install the packages

Install the packages required for building the app. This includes the user interface components and the LLMs we will be working with.

`pip install streamlit pypdf2 langchain python-dotenv faiss-cpu openai huggingface_hub tiktoken`

This is the command to install packages from requirements.txt file

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
