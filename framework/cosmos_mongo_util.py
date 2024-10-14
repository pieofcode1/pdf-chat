import json
from pymongo import MongoClient
from bson import json_util


class CosmosMongoClient:

    def __init__ (self, altas_uri, dbname, embedding_agent=None):
        self.mongodb_client = MongoClient(altas_uri)
        self.database = self.mongodb_client[dbname]
        self.embedding_agent = embedding_agent

    ## A quick way to test if we can connect to Atlas instance
    def ping (self):
        self.mongodb_client.admin.command('ping')

    def list_databases(self):
        databases = self.mongodb_client.list_database_names()
        for db in databases:
            print(f"Database: {db}")
            # Get list of collections
            collections = self.mongodb_client[db].list_collection_names()

            # Loop through collections
            for col in collections:
                print(f"\tCollection: {col}")

                # Get document count
                doc_count = self.mongodb_client[db][col].count_documents({})
                print(f"\tDocument count: {doc_count}")

    def create_collection (self, collection_name):
        self.database.create_collection(collection_name)

    def get_collection (self, collection_name):
        collection = self.database[collection_name]
        return collection
    
    def get_indices(self, collection_name):
        return self.database[collection_name].getIndexes();
    
    def create_vector_index (self, collection_name, attr_name, index_name, type="vector-hnsw", num_lists=1, similarity="COS", dimensions=1536):
        search_options = None

        # Support for HNSW indexes are available for M40 cluster tiers and higher 

        if type == "vector-ivf":
            search_options = {
                'kind': type,
                'numLists': num_lists,
                'similarity': similarity,
                'dimensions': dimensions
            }
        elif type == "vector-hnsw": 
            search_options = {
                'kind': type,
                'm': 64,
                'efConstruction': 256,
                'similarity': similarity,
                'dimensions': dimensions
            }
        else:
            raise ValueError("Invalid index type. Supported types are 'vector-ivf' and 'vector-hnsw'")

        # Create IVF index
        self.database.command({
            'createIndexes': collection_name,
            'indexes': [
                    {
                    'name': index_name,
                    'key': {
                        attr_name: "cosmosSearch"
                    },
                    'cosmosSearchOptions': search_options
                }
            ]
        })

    def parse_json(data):
        return json.loads(json_util.dumps(data))

    def insert(self, collection_name, data):
        items = []
        if isinstance(data, dict):
            data = json.loads(json_util.dumps(data))
            items.append(data)
        else:
            for item in data:
                item = json.loads(json_util.dumps(item))
                items.append(item)

        data = json.loads(json_util.dumps(data))
        collection = self.database[collection_name]
        collection.insert_many(items)
            

    def find (self, collection_name, filter = {}, limit=100):
        collection = self.database[collection_name]
        result = collection.find(filter=filter, limit=limit)
        print(result)
        items = []
        for item in result:
            items.append(item)

        return items


    # https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/
    def perform_vector_search(self, collection_name, attr_name, prompt, projection: list = [], limit=3):
        collection = self.database[collection_name]
        embedding_vector = self.embedding_agent.get_text_embeddings(prompt)
        projected_fields = dict(similarityScore= { "$meta": 'searchScore' })
        if len(projection) != 0:
            for field in projection:
                projected_fields[field] = 1
        else:
            projected_fields["document"] = '$ROOT'

        print(f"Projected fields: {projected_fields}")

        pipeline = [
                {
                    "$search": {
                        "cosmosSearch": {
                            "vector": embedding_vector,
                            "path": attr_name,
                            "k": limit, 
                            "efsearch": 40 # optional for HNSW only 
                            #"filter": {"title": {"$ne": "Azure Cosmos DB"}}
                        },
                        "returnStoredSource": True 
                    }
                },
                {
                    "$project": projected_fields
                }
            ]
        results = collection.aggregate(pipeline)
        return list(results)


    def close_connection(self):
        self.mongodb_client.close()