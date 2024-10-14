import os
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from datetime import datetime, timezone, timedelta
from azure.storage.blob import ResourceTypes, AccountSasPermissions, generate_blob_sas, generate_account_sas


class StorageHelper(object):

    def __init__(self, container_name) -> None:

        endpoint = os.environ["AZURE_STORAGE_ACCOUNT_ENDPOINT"]
        tenant_id = os.environ["SP_TENANT_ID"]
        client_id = os.environ["SP_CLIENT_ID"]
        client_secret = os.environ["SP_CLIENT_SECRET"]

        connection_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

        # credential = DefaultAzureCredential()
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        self.blob_service_client = BlobServiceClient(account_url=endpoint, credential=credential)
        # self.blob_service_client = BlobServiceClient.from_connection_string(connection_str)
        self.container_client = self.blob_service_client.get_container_client(container_name)
        
        try:
            self.container_client.create_container()
        except ResourceExistsError as re:
            # Container already created
            print(f"Container [{container_name}] already created!")
            pass

    def upload_blob(self, file): 
        # Upload a blob to the container

        with open(file, "rb") as data:
            blob_client = self.container_client.upload_blob(name=os.path.basename(file), data=data, overwrite=True)
            return blob_client.url

    def upload_blob_with_key(self, file, blob_key):
        # Upload a blob to the container with a specified key
        with open(file, "rb") as data:
            blob_client = self.container_client.upload_blob(name=blob_key, data=data, overwrite=True)
            return blob_client.url

    def upload_blob_from_stream(self, stream, blob_key):
        # Upload a blob to the container from a stream
        blob_client = self.container_client.upload_blob(name=blob_key, data=stream, overwrite=True)
        return blob_client.url

    def download_blob(self, blob_key, file_path):
         with open(file_path, "wb") as blob_file:
                download_stream = self.blob_client.download_blob()
                blob_file.write(download_stream.readall())

    def list_blobs(self):
        # List the blobs in the container
        blob_list = self.container_client.list_blobs()
        for blob in blob_list:
            print(blob.name)
        return blob_list
    
    def delete_blob(self, blob_key):
        # Delete a blob
        self.container_client.delete_blob(blob_key)
        print(f"Blob {blob_key} deleted")

    def generate_blob_sas_token(self, blob_key):
        # Generate a SAS token for the blob and return the link
        blob_client = self.container_client.get_blob_client(blob_key)
        sas_token = generate_blob_sas(
            self.blob_service_client.account_name,
            container_name=self.container_client.container_name,
            blob_name=blob_client.blob_name,
            user_delegation_key=self.blob_service_client.get_user_delegation_key(datetime.now(timezone.utc), datetime.now(timezone.utc) + timedelta(hours=1)),
            # account_key=self.blob_service_client.credential.account_key,
            account_key=None,
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=1)
        )

        blob_url = blob_client.url
        return f"{blob_url}?{sas_token}"
    

