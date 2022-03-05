
import json
from typing import Optional
from redis import Redis
from slugify import slugify

redis = Redis(host="redis.pythonweekend.skypicker.com", port=6379, db=0)
example = "novak:journey:prague_budapest_2022-06-20"


def create_key(surname, source, destination, dep_date):
    return f"{slugify(surname)}:journey:{slugify(source)}_{slugify(destination)}_{dep_date}"


def store_dict(key: str, value: dict) -> None:
    redis.set(key, json.dumps(value), 10)


def retrieve_dict(key: str) -> Optional[dict]:
    maybe_value = redis.get(key)
    if maybe_value is None:
        return None
    return json.loads(maybe_value)
