import hmac

from django.conf import settings

import shortuuid


def generate_checksum(data_bytes):
    checksum = hmac.new(
        str.encode(settings.SECRET_KEY), data_bytes, digestmod="sha256",
    ).hexdigest()
    checksum = shortuuid.uuid(checksum)[:8]

    return checksum
