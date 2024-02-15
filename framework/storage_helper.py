import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import HttpResponseError, ResourceExistsError


class StorageHelper(object):

    def __init__(self, connection_str, container_name) -> None:
        self.connection_str = connection_str
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
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
            blob_client = self.container_client.upload_blob(name=os.path.basename(file), data=data)

    def download_blob(self, blob_key, file_path):
         with open(file_path, "wb") as blob_file:
                download_stream = self.blob_client.download_blob()
                blob_file.write(download_stream.readall())


