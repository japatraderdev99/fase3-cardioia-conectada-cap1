"""API REST didática: apenas loopback, dados sintéticos e e-mail em arquivo."""
import argparse
from datetime import datetime, timezone
from email.message import EmailMessage
from email.policy import SMTP
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
from pathlib import Path
import re
import sqlite3

FIELDS = {'sample_id', 'synthetic', 'timestamp', 'bpm', 'temperature_c'}


def validate(data):
    if not isinstance(data, dict) or set(data) != FIELDS:
        raise ValueError('Campos esperados: ' + ', '.join(sorted(FIELDS)))
    if data['synthetic'] is not True:
        raise ValueError('Somente dados sintéticos são aceitos')
    if not isinstance(data['sample_id'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', data['sample_id']):
        raise ValueError('sample_id inválido')
    if not isinstance(data['timestamp'], str):
        raise ValueError('timestamp deve ser ISO 8601 com fuso')
    try:
        stamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('timestamp inválido') from None
    if stamp.tzinfo is None:
        raise ValueError('timestamp exige fuso')
    for field, low, high in [('bpm', 0, 250), ('temperature_c', -40, 80)]:
        value = data[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f'{field} fora do intervalo {low}..{high}')
    return data


def risks(data):
    # Limiares educacionais, não diagnóstico. DHT22 mede ambiente, não febre real.
    return (["bpm_acima_120"] if data['bpm'] > 120 else []) + (["temperatura_acima_38"] if data['temperature_c'] > 38 else [])


def simulated_email(data, flags):
    mail = EmailMessage()
    mail['From'] = 'cardioia@example.invalid'
    mail['To'] = 'equipe-simulada@example.invalid'
    mail['Subject'] = f"[SIMULACAO] Alerta CardioIA {data['sample_id']}"
    mail['X-CardioIA-Simulated'] = 'true'
    mail.set_content('SIMULACAO EDUCACIONAL - nenhum envio SMTP.\n'
                     + json.dumps({'sample': data, 'alerts': flags}, ensure_ascii=False, indent=2))
    return mail.as_bytes(policy=SMTP)


class Store:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.outbox = self.directory / 'outbox'
        self.outbox.mkdir(exist_ok=True)
        self.db = sqlite3.connect(self.directory / 'samples.sqlite3', check_same_thread=False)
        self.db.execute('CREATE TABLE IF NOT EXISTS samples (id TEXT PRIMARY KEY, payload TEXT NOT NULL, result TEXT NOT NULL, email BLOB)')
        self.db.commit()
        # Reconstitui arquivos a partir da transação persistida após eventual interrupção.
        for sid, email in self.db.execute('SELECT id,email FROM samples WHERE email IS NOT NULL'):
            self.write_email(sid, email)

    def write_email(self, sid, email):
        path = self.outbox / (sid + '.eml')
        temporary = path.with_suffix('.tmp')
        temporary.write_bytes(email)
        temporary.replace(path)

    def add(self, data):
        payload = json.dumps(data, sort_keys=True, allow_nan=False)
        previous = self.db.execute('SELECT payload,result,email FROM samples WHERE id=?', (data['sample_id'],)).fetchone()
        if previous:
            if previous[0] != payload:
                return 409, {'error': 'sample_id já existe com conteúdo diferente'}
            if previous[2]:
                self.write_email(data['sample_id'], previous[2])
            return 200, json.loads(previous[1])
        flags = risks(data)
        result = dict(data, alerts=flags, email_status='simulated_file' if flags else 'not_required')
        email = simulated_email(data, flags) if flags else None
        with self.db:
            self.db.execute('INSERT INTO samples VALUES (?,?,?,?)', (data['sample_id'], payload, json.dumps(result), email))
        if email:
            self.write_email(data['sample_id'], email)
        return 201, result

    def read(self, sid=None):
        if sid is None:
            return [json.loads(row[0]) for row in self.db.execute('SELECT result FROM samples ORDER BY rowid DESC LIMIT 100')]
        row = self.db.execute('SELECT result FROM samples WHERE id=?', (sid,)).fetchone()
        return json.loads(row[0]) if row else None


def handler_for(store):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, data):
            content = json.dumps(data, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            if self.path == '/health':
                return self.reply(200, {'status': 'ok', 'synthetic_only': True, 'email_mode': 'file_only'})
            if self.path == '/samples':
                return self.reply(200, {'items': store.read(), 'limit': 100, 'order': 'newest_first'})
            if self.path.startswith('/samples/'):
                result = store.read(self.path.removeprefix('/samples/'))
                return self.reply(200, result) if result else self.reply(404, {'error': 'Amostra não encontrada'})
            self.reply(404, {'error': 'Rota não encontrada'})

        def do_POST(self):
            if self.path != '/samples':
                return self.reply(404, {'error': 'Rota não encontrada'})
            if self.headers.get_content_type() != 'application/json':
                return self.reply(415, {'error': 'Use application/json'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 4096:
                    return self.reply(413, {'error': 'Corpo deve ter 1..4096 bytes'})
                data = validate(json.loads(self.rfile.read(size)))
            except (ValueError, UnicodeError) as error:
                return self.reply(400, {'error': str(error)})
            try:
                status, result = store.add(data)
                self.reply(status, result)
            except (OSError, sqlite3.Error):
                self.reply(500, {'error': 'Falha local de persistência; repetir com mesmo sample_id'})

        def log_message(self, format, *args):
            pass  # Não grava payloads nem informações pessoais em logs HTTP.
    return Handler


def make_server(directory, port=8000):
    store = Store(directory)
    server = HTTPServer(('127.0.0.1', port), handler_for(store))
    server.store = store
    return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--data-dir', default='rest/runtime')
    args = parser.parse_args()
    server = make_server(args.data_dir, args.port)
    print(f'API sintética http://127.0.0.1:{server.server_port}; e-mails somente em arquivo', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        server.store.db.close()
