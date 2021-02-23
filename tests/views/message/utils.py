import time

import orjson
import shortuuid

from django_unicorn.utils import generate_checksum


def post_and_get_response(
    client, url="", data=None, action_queue=None, component_id=None
):
    if not data:
        data = {}
    if not action_queue:
        action_queue = []
    if not component_id:
        component_id = shortuuid.uuid()[:8]

    message = {
        "actionQueue": action_queue,
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": component_id,
        "epoch": time.time(),
    }

    response = client.post(url, message, content_type="application/json",)
    # body = orjson.loads(response.content)

    return response.json()
