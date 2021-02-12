import time

import orjson
import shortuuid

from django_unicorn.utils import generate_checksum


def post_and_get_response(client, url="", data={}, action_queue=[]):
    data = {}
    message = {
        "actionQueue": action_queue,
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(url, message, content_type="application/json",)

    return response
