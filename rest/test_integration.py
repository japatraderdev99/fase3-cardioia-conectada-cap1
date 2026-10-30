"""Testes sobre socket HTTP real com diretório temporário e porta efêmera."""
from email import policy
from email.parser import BytesParser
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from client import request
from server import make_server


class Integration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.server = make_server(self.temp.name, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.sample = dict(sample_id='synthetic-001', synthetic=True, timestamp='2026-10-30T00:00:00-03:00', bpm=72, temperature_c=25)

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self.server.store.db.close()
        self.temp.cleanup()

    def test_normal_post_get_and_list(self):
        status, body = request(self.base, '/samples', self.sample)
        self.assertEqual(status, 201)
        self.assertEqual(body['alerts'], [])
        self.assertEqual(body['email_status'], 'not_required')
        self.assertEqual(request(self.base, '/samples/synthetic-001'), (200, body))
        self.assertEqual(request(self.base, '/samples')[1]['items'], [body])
        self.assertEqual(list(Path(self.temp.name).glob('outbox/*.eml')), [])

    def test_alert_file_and_idempotency(self):
        self.sample.update(bpm=135, temperature_c=39)
        status, body = request(self.base, '/samples', self.sample)
        self.assertEqual(status, 201)
        self.assertEqual(body['alerts'], ['bpm_acima_120', 'temperatura_acima_38'])
        mailpath = Path(self.temp.name) / 'outbox/synthetic-001.eml'
        mail = BytesParser(policy=policy.default).parsebytes(mailpath.read_bytes())
        self.assertEqual(mail['X-CardioIA-Simulated'], 'true')
        self.assertEqual(mail['To'], 'equipe-simulada@example.invalid')
        self.assertIn('SIMULACAO EDUCACIONAL', mail.get_content())
        self.assertEqual(request(self.base, '/samples', self.sample), (200, body))
        self.assertEqual(len(list(mailpath.parent.glob('*.eml'))), 1)
        self.sample['bpm'] = 136
        self.assertEqual(request(self.base, '/samples', self.sample)[0], 409)

    def test_exact_boundaries_and_individual_alerts(self):
        for i, (bpm, temp, expected) in enumerate([(120, 38, []), (121, 38, ['bpm_acima_120']), (120, 38.1, ['temperatura_acima_38'])]):
            sample = dict(self.sample, sample_id=f'limit-{i}', bpm=bpm, temperature_c=temp)
            self.assertEqual(request(self.base, '/samples', sample)[1]['alerts'], expected)

    def test_invalid_values(self):
        for field, value in [('synthetic', False), ('bpm', True), ('bpm', -1), ('bpm', 251), ('temperature_c', 81), ('sample_id', '../x'), ('timestamp', '2026-10-30')]:
            with self.subTest(field=field, value=value):
                self.assertEqual(request(self.base, '/samples', dict(self.sample, **{field: value}))[0], 400)
        self.assertEqual(request(self.base, '/samples', dict(self.sample, extra='not allowed'))[0], 400)
        self.assertEqual(request(self.base, '/samples', [1, 2])[0], 400)

    def test_malformed_body_media_size_and_nan(self):
        for body, media, expected in [(b'{', 'application/json', 400), (b'{}', 'text/plain', 415), (b'x' * 4097, 'application/json', 413), (json.dumps(dict(self.sample, bpm=float('nan'))).encode(), 'application/json', 400)]:
            req = Request(self.base + '/samples', data=body, headers={'Content-Type': media})
            with self.assertRaises(HTTPError) as context:
                urlopen(req, timeout=5)
            self.assertEqual(context.exception.code, expected)
            context.exception.close()

    def test_routes_and_local_only_client(self):
        self.assertEqual(request(self.base, '/health')[0], 200)
        self.assertEqual(request(self.base, '/missing')[0], 404)
        self.assertEqual(request(self.base, '/samples/missing')[0], 404)
        with self.assertRaises(ValueError):
            request('https://example.com', '/samples')

    def test_restart_persistence_and_email_recovery(self):
        self.sample['bpm'] = 130
        request(self.base, '/samples', self.sample)
        mailpath = Path(self.temp.name) / 'outbox/synthetic-001.eml'
        mailpath.unlink()
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self.server.store.db.close()
        self.server = make_server(self.temp.name, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.assertTrue(mailpath.exists())
        self.assertEqual(request(self.base, '/samples/synthetic-001')[0], 200)
        self.assertEqual(request(self.base, '/samples', self.sample)[0], 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
