"""Cliente REST com POST e GET reais em loopback; nunca envia e-mail."""
import argparse
from datetime import datetime, timezone
import json
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def request(base, path, data=None):
    parsed = urlsplit(base)
    if parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or parsed.path not in ('', '/'):
        raise ValueError('Esta demonstração aceita somente http://127.0.0.1:porta')
    body = json.dumps(data, allow_nan=False).encode() if data is not None else None
    req = Request(base.rstrip('/') + path, data=body, headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=5) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def demo(base):
    stamp = datetime.now(timezone.utc).isoformat()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    results = []
    for suffix, bpm, temp in [('normal', 72, 25), ('alerta', 135, 39)]:
        sample = {'sample_id': f'{run_id}-{suffix}', 'synthetic': True, 'timestamp': stamp,
                  'bpm': bpm, 'temperature_c': temp}
        status, data = request(base, '/samples', sample)
        if status != 201:
            raise RuntimeError(f'POST falhou: {status} {data}')
        results.append({'method': 'POST', 'status': status, 'body': data})
        status, data = request(base, '/samples/' + sample['sample_id'])
        if status != 200:
            raise RuntimeError(f'GET falhou: {status} {data}')
        results.append({'method': 'GET', 'status': status, 'body': data})
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://127.0.0.1:8000')
    args = parser.parse_args()
    print(json.dumps(demo(args.base), ensure_ascii=False, indent=2))
