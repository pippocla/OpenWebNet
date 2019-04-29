
import os
import yaml
import logging
from time import sleep
import timeit

logging.basicConfig(level=logging.DEBUG)

perf= timeit.timeit(stmt = 'request_light_state()', number = 100, setup="""

from client import get_command_client

TABLE_LIGHT = '10'
light = TABLE_LIGHT

client = get_command_client()
def request_light_state():
    client.request_state('1', light)
""")

print("time taken: ", perf)
