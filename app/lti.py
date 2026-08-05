import base64
import hashlib
import hmac
from typing import Dict
from urllib.parse import quote


def _percent_encode(value: str) -> str:
    return quote(str(value), safe='~-._')


def _normalized_url(request) -> str:
    scheme = request.scheme
    host = request.get_host().split('@')[-1]
    path = request.path
    return f"{scheme}://{host}{path}"


def _normalized_parameter_string(params: Dict[str, str]) -> str:
    encoded_pairs = []
    for key, value in params.items():
        if key == 'oauth_signature':
            continue
        encoded_pairs.append((_percent_encode(key), _percent_encode(value)))

    encoded_pairs.sort(key=lambda pair: (pair[0], pair[1]))
    return '&'.join(f"{k}={v}" for k, v in encoded_pairs)


def _signature_base_string(request, params: Dict[str, str]) -> str:
    method = request.method.upper()
    normalized_url = _normalized_url(request)
    normalized_params = _normalized_parameter_string(params)
    return '&'.join(
        [
            _percent_encode(method),
            _percent_encode(normalized_url),
            _percent_encode(normalized_params),
        ]
    )


def is_valid_lti_oauth_signature(request, params: Dict[str, str], consumer_secret: str) -> bool:
    signature_method = params.get('oauth_signature_method', '').upper()
    provided_signature = params.get('oauth_signature', '')

    if signature_method not in {'HMAC-SHA1', 'HMAC-SHA256'}:
        return False

    base_string = _signature_base_string(request, params)
    signing_key = f"{_percent_encode(consumer_secret)}&"

    digestmod = hashlib.sha1 if signature_method == 'HMAC-SHA1' else hashlib.sha256
    digest = hmac.new(signing_key.encode('utf-8'), base_string.encode('utf-8'), digestmod).digest()
    calculated_signature = base64.b64encode(digest).decode('utf-8')

    return hmac.compare_digest(calculated_signature, provided_signature)
