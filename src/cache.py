import time
import json

import redis
from redis.exceptions import ConnectionError

redis_client = redis.Redis(host='localhost', port=6379, db=0)


def is_cache_stale(product_id:int):
    cache_time_key = f"cache_time:{product_id}"
    cache_time = redis_client.get(cache_time_key)

    # cache expires after an hour
    return cache_time is not None and time.time() - float(cache_time) < 3600 

def store_product_prices(product_id:int, prices:dict):
    prices_cache_key = f"prices:{product_id}"
    cache_time_key = f"cache_time:{product_id}"

    redis_client.set(prices_cache_key, json.dumps(prices))
    redis_client.set(cache_time_key, time.time())

def retrieve_product_prices(product_id:int):
    try:
        prices_cache_key = f"prices:{product_id}"
        c_prices = redis_client.get(prices_cache_key)

        if c_prices and not is_cache_stale(product_id):
            return json.loads(c_prices)
        else:
            return None
    except ConnectionError:
        print("Could not connect to cache.")
        return None