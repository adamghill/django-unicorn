import hmac

from django.conf import settings

import shortuuid


def generate_checksum(data_bytes):
    if isinstance(data_bytes, str):
        data_bytes = str.encode(data_bytes)

    checksum = hmac.new(
        str.encode(settings.SECRET_KEY), data_bytes, digestmod="sha256",
    ).hexdigest()
    checksum = shortuuid.uuid(checksum)[:8]

    return checksum


def dicts_equal(d1, d2):
    """ return True if all keys and values are the same """
    return all(k in d2 and d1[k] == d2[k] for k in d1) and all(
        k in d1 and d1[k] == d2[k] for k in d2
    )
