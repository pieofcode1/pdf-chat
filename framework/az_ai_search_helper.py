import json
import os
import openai
from pathlib import Path
import dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient, SearchIndexingBufferedSender
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
# from azure.search.documents.indexes.models import (
#     SemanticSettings,
#     SemanticConfiguration,
#     PrioritizedFields,
#     SemanticField
# )
from langchain_community.vectorstores import AzureSearch
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import TextSplitter
from langchain_community.utilities import BingSearchAPIWrapper


from azure.search.documents.models import *
from azure.search.documents.indexes.models import *

from .cosmos_util import CosmosUtil


# Load env settings if not already loaded
if os.getenv("AZURE_OPENAI_ENDPOINT") is None:
    env_name = os.environ["APP_ENV"] if "APP_ENV" in os.environ else "local"
    # Load env settings
    env_file_path = Path(f"./.env.{env_name}")
    print(f"Loading environment from: {env_file_path}")
    with open(env_file_path) as f:
        dotenv.load_dotenv(dotenv_path=env_file_path)
    # print(os.environ)


def get_az_search_index_client():
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_ADMIN_KEY"]

    credential = AzureKeyCredential(key)

    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    return index_client


def get_az_search_client():
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
    key = os.environ["AZURE_SEARCH_ADMIN_KEY"]

    credential = AzureKeyCredential(key)

    client = SearchClient(endpoint=endpoint,
                          index_name=index_name,
                          credential=credential)
    return client


def get_ai_search_index_client(index_name):
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
    if index_name is None:
        raise ValueError("Index name is required")
    credential = AzureKeyCredential(key)

    client = SearchClient(endpoint=endpoint,
                          index_name=index_name,
                          credential=credential)
    return client


def get_ai_search_index_clients(index_names):
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
    if index_names is None or len(index_names) == 0:
        raise ValueError("Index name is required")
    credential = AzureKeyCredential(key)

    index_client_map = {}
    for index_name in index_names:
        client = SearchClient(endpoint=endpoint,
                              index_name=index_name,
                              credential=credential)
        
        index_client_map[index_name] = client

    return index_client_map

def get_az_search_indices():

    service_client = get_az_search_index_client()
    # Get all the indices from the Azure Search service
    result = service_client.list_index_names()
    names = [x for x in result]
    # names = ["azure-plat-services-vector-search", "langchain-vector-demo"]
    return names


# Search for documents using vector search
def perform_vector_search(client, vectorized_query, attr_name: str, projection=None):
    
    # Create a search index
    vector_query = VectorizedQuery(vector=vectorized_query, k_nearest_neighbors=3, fields=attr_name)

    results = client.search(  
        search_text=None,  
        vector_queries= [vector_query],
        select=projection,
    )  

    results = [x for x in results]
    for result in results:
        print(f"Score: {result['@search.score']}")  
        print(f"Result: {result}")  
        print("..........................................")

    return results


def get_index_fields(index_name, embedding_function):
    if index_name == "azure-plat-services-vector-search":
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String,
                        key=True, sortable=True, filterable=True, facetable=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchableField(name="category", type=SearchFieldDataType.String,
                            filterable=True),
            SearchField(name="title_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True, vector_search_dimensions=1536, vector_search_configuration="myHnswProfile"),
            SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True, vector_search_dimensions=1536, vector_search_configuration="myHnswProfile"),
        ]

    else:
        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(
                    SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=len(embedding_function("Text")),
                vector_search_configuration="default",
            ),
            SearchableField(
                name="metadata",
                type=SearchFieldDataType.String,
                searchable=True,
            )
        ]

    return fields


def create_cogsearch_index(index_name, embeddings):

    print(f"Creating index: {index_name}")

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_ADMIN_KEY"]

    vector_store_en: AzureSearch = AzureSearch(
        azure_search_endpoint=endpoint,
        azure_search_key=key,
        index_name=index_name,
        embedding_function=embeddings.embed_query,
        semantic_configuration_name='config',
        semantic_settings=SemanticSearch(
            default_configuration='config',
            configurations=[
                SemanticConfiguration(
                    name='config',
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name='content'),
                        prioritized_content_fields=[
                            SemanticField(field_name='content')],
                        prioritized_keywords_fields=[
                            SemanticField(field_name='metadata')]
                    ))
            ])
    )


def create_bing_search_agent():
    bing_search = BingSearchAPIWrapper(k=3)
    return bing_search


def create_clip_cognition_indices():
    # Create Azure Search indices for Clip Cognition
    # Create the Azure Search index
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_ADMIN_KEY"])

    # Create a search index
    index_name = "cc-video-asset-index"
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)

    fields = [ 
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
        SearchableField(name="asset_name", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),

        SimpleField(name="blob_video_key", type=SearchFieldDataType.String),
        SimpleField(name="blob_audio_key", type=SearchFieldDataType.String),
        SimpleField(name="blob_video_url", type=SearchFieldDataType.String),
        SimpleField(name="blob_audio_url", type=SearchFieldDataType.String),
        SimpleField(name="frame_offset", type=SearchFieldDataType.Int32),
        SimpleField(name="frame_count", type=SearchFieldDataType.Int32),
        SimpleField(name="duration", type=SearchFieldDataType.Int32),
        SimpleField(name="total_frames", type=SearchFieldDataType.Int32),

        SimpleField(name="audio_summary", type=SearchFieldDataType.String),
        SimpleField(name="audio_transcription", type=SearchFieldDataType.String),
        SimpleField(name="video_summary", type=SearchFieldDataType.String),
        SimpleField(name="created_at", type=SearchFieldDataType.String, filterable=True, sortable=True),
        
        SearchField(name="audio_summary_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
        SearchField(name="video_summary_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    ]

    # Configure the vector search configuration  
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            )
        ]
    )

    # Configure the semantic search configuration
    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="asset_name"),
            keywords_fields=[SemanticField(field_name="audio_summary"), SemanticField(field_name="video_summary")],
            content_fields=[SemanticField(field_name="audio_summary"), SemanticField(field_name="video_summary")]
        )
    )

    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Create the search index with the semantic settings
    index = SearchIndex(name=index_name, fields=fields,
                        vector_search=vector_search, semantic_search=semantic_search)
    result = index_client.create_or_update_index(index)
    print(f' {result.name} created')

    # Create index for storing video frame summary
    index_name = "cc-video-asset-frames-index"
    # Create a search index
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    fields = [ 
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
        SearchableField(name="asset_name", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),

        SimpleField(name="url", type=SearchFieldDataType.String),
        SimpleField(name="summary", type=SearchFieldDataType.String),
        SimpleField(name="frame_id", type=SearchFieldDataType.Int32),
        SimpleField(name="created_at", type=SearchFieldDataType.String, filterable=True, sortable=True),
        
        SearchField(name="summary_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile")
    ]

    # Configure the vector search configuration  
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            )
        ]
    )

    # Configure the semantic search configuration
    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="asset_name"),
            keywords_fields=[SemanticField(field_name="summary")],
            content_fields=[SemanticField(field_name="summary")]
        )
    )

    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Create the search index with the semantic settings
    index = SearchIndex(name=index_name, fields=fields,
                        vector_search=vector_search, semantic_search=semantic_search)
    result = index_client.create_or_update_index(index)
    print(f' {result.name} created')