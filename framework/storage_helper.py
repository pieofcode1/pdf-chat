import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from datetime import datetime, timedelta
from azure.storage.blob import ResourceTypes, AccountSasPermissions, generate_account_sas

class StorageHelper(object):

    def __init__(self, connection_str, container_name) -> None:
        self.connection_str = connection_str
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_str)
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
        sas_token = generate_account_sas(
            self.blob_service_client.account_name,
            account_key=self.blob_service_client.credential.account_key,
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        blob_url = blob_client.url
        return f"{blob_url}?{sas_token}"
    

