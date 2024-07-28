import logging
import time
import functools
from datetime import datetime
import csv
from langchain.callbacks.base import BaseCallbackHandler


def timer(func):
    """Print the run timespan of the decorated function"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter() #1
        func(*args, **kwargs)
        end_time = time.perf_counter() #2
        elapsed_time = end_time - start_time 
        params = kwargs.get("params", None)
        print(f"Params: {params}")
        if params and type(params) == dict:
            params["elapsed"] = elapsed_time
            
        print(f"Finished {func.__name__!r} in {elapsed_time:.4f} seconds")

    return wrapper


def read_lines(filename):
    lines = None
    with open(f"{filename}", "r") as f:
        lines = f.readlines()
    
    return lines


def write_csv(headers, rows, filename):
    """ Helper function to write data in csv format """
    with open(f"./Data/{filename}", 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(headers)
        # write multiple rows
        writer.writerows(rows)

def read_csv(filename, fieldnames):
    with open(f"./Data/{filename}", 'r', encoding='UTF8', newline='') as f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        index = 0
        rows = [row for row in reader]
        rows.pop(0)
        return rows
            

def write_json(fieldnames, rows, filename):
    with open(f"./Data/{filename}", 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class ChainLogger(BaseCallbackHandler):
    
    def __init__(self):
        self.logs = []

    def on_chain_start(self, serialized, **kwargs):
        self.logs.append(f"Starting chain: {serialized}")

    def on_chain_end(self, output, **kwargs):
        self.logs.append(f"Finished chain with output: {output}")

    def on_tool_start(self, serialized, **kwargs):
        self.logs.append(f"Starting tool: {serialized}")

    def on_tool_end(self, output, **kwargs):
        self.logs.append(f"Finished tool with output: {output}")

    def on_agent_action(self, action, **kwargs):
        self.logs.append(f"Agent action: {action}")

    def on_agent_finish(self, output, **kwargs):
        self.logs.append(f"Agent finished with output: {output}")
