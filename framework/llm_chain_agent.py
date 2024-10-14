import os
import openai
from openai import AzureOpenAI
import base64
from pathlib import Path
from io import StringIO, BytesIO
import requests
import dotenv
import langchain
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain.chains import ConversationChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable


"""
This class is used to create an Embedding Agent that can be used to interact with Azure OpenAI.
The agent can be used to generate embeddings for text and images.
"""
class BaseEmbeddingAgent:
    
    def __init__(self):
        pass

    def get_text_embeddings(self, text):
        raise NotImplementedError("This method should be implemented in the derived class")
    
    def get_image_embeddings(self, blob_image_path):
        raise NotImplementedError("This method should be implemented in the derived class")
        

class AzureOpenAIEmbeddingsAgent(BaseEmbeddingAgent):
        
    def __init__(self):
        self.AOAI_client = AzureOpenAI(
                            api_key=os.environ['AZURE_OPENAI_API_KEY'], 
                            azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'], 
                            api_version=os.environ['OPENAI_API_VERSION']
                        )
    
    def get_text_embeddings(self, text):
        '''
        Generate embeddings from string of text.
        This will be used to vectorize data and user input for interactions with Azure OpenAI.
        '''
        response = self.AOAI_client.embeddings.create(input=text, model=os.environ['AZURE_EMBEDDING_DEPLOYMENT_NAME'])
        embeddings =response.model_dump()
        return embeddings['data'][0]['embedding']
    
    def get_image_embeddings(self, blob_image_path):
        raise NotImplementedError("This method is not supported for this class")
        

class AIVisionEmbeddingsAgent(BaseEmbeddingAgent):
           
    def __init__(self):
        super().__init__()
    
    def get_text_embeddings(self, text):
        # Create a code snippet for calling post api using requests
        vision_ep = os.environ["COGNITIVE_MULTISVC_ENDPOINT"]
        vision_key = os.environ["COGNITIVE_MULTISVC_API_KEY"]

        operation_name = "vectorizeText"

        url = f"{vision_ep}/computervision/retrieval:{operation_name}?api-version=2024-02-01&model-version=2023-04-15"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": vision_key
        }
        data = {
            "text": text
        }
        response = requests.post(url, headers=headers, json=data)
        print(response.json())

        return response.json()["vector"]
    
    def get_image_embeddings(self, blob_image_path):
        # Create a code snippet for calling post api using requests
        vision_ep = os.environ["COGNITIVE_MULTISVC_ENDPOINT"]
        vision_key = os.environ["COGNITIVE_MULTISVC_API_KEY"]

        operation_name = "vectorizeImage"

        url = f"{vision_ep}/computervision/retrieval:{operation_name}?api-version=2024-02-01&model-version=2023-04-15"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": vision_key
        }
        data = {
            "url": blob_image_path
            # "url": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
            # "url": f"data:image/jpeg;base64,{b64_encoded_image}"
        }
        response = requests.post(url, headers=headers, json=data)
        print(response.json())

        return response.json()["vector"]
        

"""
This class is used to create a Language Model chain agent that can be used to interact with Azure OpenAI.
The chain agent can be used to create a chain with memory or without memory.
"""
class LLMChainAgent:

    @staticmethod
    def get_llm_chain(memory = False):
        llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_CHATGPT_DEPLOYMENT_NAME"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            openai_api_type="azure",
            openai_api_version=os.environ["OPENAI_API_VERSION"],
            openai_api_key=os.environ["AZURE_OPENAI_API_KEY"]
        )

        # Create a chat prompt template
        prompt = ChatPromptTemplate.from_messages([
            ('system', 'You are a helpful assistant. Answer the question asked by the user in the most efficient manner.'),
            ('user', 'Question : {input}'),
        ])

        if memory:
            # Create a memory
            memory = ConversationBufferMemory()
            # Create a chain with this memory object and the model object created earlier.
            chain = ConversationChain(
                llm=llm,
                memory=memory,
            )

        else:
            
            # create a chain
            chain = prompt | llm | StrOutputParser()

        return chain


    @staticmethod
    def get_llm_chain_with_history(window_size=3):
       
        # Create a chain with this memory object and the model object created earlier.
        llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_CHATGPT_DEPLOYMENT_NAME"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            openai_api_type="azure",
            openai_api_version=os.environ["OPENAI_API_VERSION"],
            openai_api_key=os.environ["AZURE_OPENAI_API_KEY"]
        )

        # Create a memory
        # memory = ConversationBufferMemory(return_messages=True)
        memory = ConversationBufferWindowMemory(k=window_size, return_messages=True)
        # memory = ConversationSummaryMemory(llm=llm)

        # Create a chain with this memory object and the model object created earlier.
        chain = ConversationChain(
            llm=llm,
            memory=memory
        )

        return chain


def main():
    env_name = os.environ["APP_ENV"] if "APP_ENV" in os.environ else "local"
    # Load env settings
    env_file_path = Path(f"../.env.{env_name}")
    print(f"Loading environment from: {env_file_path}")
    with open(env_file_path) as f:
        dotenv.load_dotenv(dotenv_path=env_file_path)

    # test the llm chain
    agent = LLMChainAgent.get_llm_chain_with_history(window_size=0)
    response = agent.invoke({"input": "Which is the most popular Beethoven\'s symphony?"})
    print(response)
    
    print("----------------------------------------------------------------")
    # Now, let us ask a follow up question
    response2 = agent.invoke({'input' : 'Which is the last one?'})
    print(response2)

    print("----------------------------------------------------------------")
    # Now, let us ask a follow up question
    response3 = agent.invoke({'input' : 'Which is the second last one?'})
    print(response3)


if __name__ == "__main__":
    main()
