"""Executa servidor/cliente locais e preserva evidência numa pasta nova por execução."""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import threading
from client import demo
from server import make_server

root = Path(__file__).resolve().parent.parent
run = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
directory = root / 'docs/rest/evidence' / run
directory.mkdir(parents=True)
server = make_server(directory / 'data', 0)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    result = {'executed_at_utc': datetime.now(timezone.utc).isoformat(),
              'python': platform.python_version(), 'transport': 'HTTP over loopback socket',
              'email_mode': 'local .eml only; no SMTP', 'synthetic_only': True,
              'responses': demo(f'http://127.0.0.1:{server.server_port}')}
    (directory / 'http-demo.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(directory)
finally:
    server.shutdown()
    thread.join()
    server.server_close()
    server.store.db.close()
