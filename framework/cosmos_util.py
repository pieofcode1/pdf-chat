from azure.cosmos import CosmosClient
from azure.cosmos.diagnostics import RecordDiagnostics
import azure.cosmos.exceptions as exceptions

import json
import time
from datetime import date, datetime
from faker import Faker
import uuid
import random


class CosmosUtil:

    def __init__(self, url, key, database, containers) -> None:
        self.url = url
        self.key = key
        self.database_name = database

        container_names = list()
        if type(containers) != list:
            container_names.append(containers)
        else:
            container_names = containers

        self.container_map = dict()

        self.cosmose_client = CosmosClient(url, credential=key)
        self.database_client = self.cosmose_client.get_database_client(
            self.database_name)
        print(f"Container Name: {container_names}")
        for name in container_names:
            self.container_map[name] = self.database_client.get_container_client(
                name)

    def add_containers(self, container_names):
        for name in container_names:
            self.container_map[name] = self.database_client.get_container_client(
                name)

    @classmethod
    def initialize():
        pass

    def upsert_items(self, container, items, delay=1, cutoff=-1):
        documents = list()
        if type(items) != list:
            documents.append(items)
        else:
            documents = items

        try:
            pass
        except exceptions.CosmosResourceNotFoundError:
            pass

        container_client = self.container_map[container]
        print(f"Container Client - {container_client}")

        for item in documents:
            result = container_client.upsert_item(body=item)
            request_charge = container_client.client_connection.last_response_headers[
                "x-ms-request-charge"]
            print(f"Request Charge: {request_charge}")

    def query_items(self, container, predicate):

        container_client = self.container_map[container]
        if (predicate == None or predicate == ""):
            query = "SELECT * FROM r"
        else:
            if type(predicate) == dict:
                predicate_str = ""
                for key in predicate.keys():
                    predicate_str += f"r.{key} = '{predicate[key]}' AND "
                predicate_str = predicate_str[:-4]
                query = f"SELECT * FROM r WHERE {predicate_str}"
            else:
                query = f"SELECT * FROM r WHERE r.{predicate}"

        print(f"Query: {query}")

        m = RecordDiagnostics()
        items = list(container_client.query_items(
            query=query,
            enable_cross_partition_query=True,
            response_hook=m
        ))
        # print(f"Here: {items}")
        ru_consumption = (datetime.now().isoformat(), m.request_charge, float(
            m.headers["x-ms-request-duration-ms"]))

        return ru_consumption, items

    def query_devices_by_fw_versions(self, container, version):
        print(self.container_map.keys())
        container_client = self.container_map[container]
        # query = f"SELECT VALUE COUNT(1) as DeviceCount, r.FirmwareVersion FROM DeviceState r GROUP BY r.FirmwareVersion"
        query = f"SELECT * FROM DeviceState r WHERE r.FirmwareVersion = @vesion"
        print(f"Query: {query}")

        m = RecordDiagnostics()
        items = list(container_client.query_items(
            query=query,
            parameters=[
                dict(name="@vesion", value=version)
            ],
            enable_cross_partition_query=True,
            response_hook=m
        ))
        print(f"Here: {items}, {m.headers}")
        print(dir(m))
        print(m.request_charge)
        ru_consumption = (datetime.now().isoformat(), m.request_charge, float(
            m.headers["x-ms-request-duration-ms"]))

        return ru_consumption, items

    def read_change_feed(self, container_name):
        print(self.container_map.keys())
        container_client = self.container_map[container_name]
        response = container_client.query_items_change_feed(
            is_start_from_beginning=True)
        # response = container_client.query_items_change_feed()
        cnt = 0
        for doc in response:
            cnt = cnt + 1
            print(doc)

        print(f'\nFinished reading all the change feed: {cnt}\n')
