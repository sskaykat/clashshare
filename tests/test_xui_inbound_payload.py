import unittest
from unittest.mock import patch

from app import app, _build_inbound_payload, XuiApiError


class XuiInboundPayloadTest(unittest.TestCase):
    def test_default_payload_supported_protocols(self):
        protocols = [
            'vless',
            'vmess',
            'trojan',
            'shadowsocks',
            'wireguard',
            'hysteria2',
            'http',
            'socks',
            'dokodemo-door',
            'tun',
        ]

        for index, protocol in enumerate(protocols, start=1):
            with self.subTest(protocol=protocol):
                payload = _build_inbound_payload({
                    'remark': f'test-{protocol}',
                    'port': 20000 + index,
                    'protocol': protocol,
                    'network': 'tcp',
                    'security': 'none',
                    'total_gb': 0,
                    'expiry_days': 0,
                    'enable': True,
                })
                self.assertEqual(payload['protocol'], protocol)
                self.assertEqual(payload['streamSettings']['network'], 'tcp')
                self.assertIn('settings', payload)

    def test_full_payload_is_validated(self):
        payload = _build_inbound_payload({
            'inbound_payload': {
                'enable': True,
                'remark': 'full-json',
                'listen': '',
                'port': 24443,
                'protocol': 'vless',
                'total': 0,
                'expiryTime': 0,
                'settings': {'clients': [], 'decryption': 'none', 'fallbacks': []},
                'streamSettings': {
                    'network': 'xhttp',
                    'security': 'reality',
                    'realitySettings': {
                        'target': 'www.amd.com:443',
                        'serverNames': ['www.amd.com'],
                        'privateKey': 'priv',
                        'shortIds': ['abcd1234'],
                        'settings': {'fingerprint': 'chrome', 'serverName': 'www.amd.com', 'spiderX': '/'}
                    }
                },
                'sniffing': {'enabled': True, 'destOverride': ['http', 'tls'], 'metadataOnly': False, 'routeOnly': False},
            }
        })
        self.assertEqual(payload['streamSettings']['network'], 'xhttp')
        self.assertEqual(payload['streamSettings']['security'], 'reality')

    def test_edit_payload_preserves_existing_clients(self):
        existing = {
            'enable': True,
            'remark': 'old',
            'listen': '',
            'port': 10001,
            'protocol': 'vless',
            'total': 0,
            'expiryTime': 0,
            'tag': 'inbound-10001',
            'settings': {'clients': [{'email': 'alice'}], 'decryption': 'none', 'fallbacks': []},
            'streamSettings': {'network': 'tcp', 'security': 'none'},
            'sniffing': {'enabled': True, 'destOverride': ['http'], 'metadataOnly': False, 'routeOnly': False},
        }
        payload = _build_inbound_payload({
            'inbound_payload': {
                'enable': True,
                'remark': 'new',
                'listen': '',
                'port': 10002,
                'protocol': 'vless',
                'total': 0,
                'expiryTime': 0,
                'settings': {'clients': [], 'decryption': 'none', 'fallbacks': []},
                'streamSettings': {'network': 'tcp', 'security': 'none'},
                'sniffing': {'enabled': True, 'destOverride': ['http'], 'metadataOnly': False, 'routeOnly': False},
            }
        }, existing)
        self.assertEqual(payload['settings']['clients'], [{'email': 'alice'}])
        self.assertEqual(payload['tag'], 'inbound-10001')

    def test_rejects_unknown_protocol(self):
        with self.assertRaises(XuiApiError):
            _build_inbound_payload({
                'remark': 'bad',
                'port': 20000,
                'protocol': 'unknown',
            })

    def test_add_route_forwards_full_payload(self):
        forwarded = {}
        inbound_payload = {
            'enable': True,
            'remark': 'route-json',
            'listen': '',
            'port': 25555,
            'protocol': 'trojan',
            'total': 0,
            'expiryTime': 0,
            'settings': {'clients': [], 'fallbacks': []},
            'streamSettings': {'network': 'grpc', 'security': 'tls'},
            'sniffing': {'enabled': True, 'destOverride': ['http'], 'metadataOnly': False, 'routeOnly': False},
        }

        def fake_xui_request(method, path, json_body=None, config_id=None, **kwargs):
            forwarded['method'] = method
            forwarded['path'] = path
            forwarded['json_body'] = json_body
            forwarded['config_id'] = config_id
            return {'success': True, 'msg': 'ok'}

        with app.test_client() as client:
            with client.session_transaction() as session:
                session['admin_id'] = 1

            with patch('app._xui_request', side_effect=fake_xui_request):
                response = client.post('/api/xui/inbounds', json={
                    'backend_id': 7,
                    'inbound_payload': inbound_payload,
                })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(forwarded['method'], 'POST')
        self.assertEqual(forwarded['path'], '/panel/api/inbounds/add')
        self.assertEqual(forwarded['config_id'], 7)
        self.assertEqual(forwarded['json_body']['protocol'], 'trojan')
        self.assertEqual(forwarded['json_body']['streamSettings']['network'], 'grpc')

    def test_vless_reality_full_payload_keeps_current_fields(self):
        payload = _build_inbound_payload({
            'inbound_payload': {
                'enable': True,
                'remark': 'vless-reality',
                'listen': '',
                'port': 24444,
                'protocol': 'vless',
                'total': 0,
                'expiryTime': 0,
                'settings': {
                    'clients': [],
                    'decryption': 'none',
                    'encryption': 'none',
                    'testseed': [900, 500, 900, 256],
                    'fallbacks': []
                },
                'streamSettings': {
                    'network': 'tcp',
                    'security': 'reality',
                    'realitySettings': {
                        'show': False,
                        'xver': 0,
                        'target': 'www.amd.com:443',
                        'serverNames': ['www.amd.com'],
                        'privateKey': 'priv',
                        'shortIds': ['abcd1234'],
                        'maxTimediff': 0,
                        'mldsa65Seed': 'seed',
                        'settings': {
                            'publicKey': 'pub',
                            'fingerprint': 'chrome',
                            'serverName': 'www.amd.com',
                            'spiderX': '/',
                            'mldsa65Verify': 'verify'
                        }
                    }
                },
                'sniffing': {'enabled': True, 'destOverride': ['http', 'tls'], 'metadataOnly': False, 'routeOnly': False},
            }
        })
        self.assertEqual(payload['settings']['testseed'], [900, 500, 900, 256])
        self.assertEqual(payload['streamSettings']['realitySettings']['target'], 'www.amd.com:443')
        self.assertEqual(payload['streamSettings']['realitySettings']['settings']['publicKey'], 'pub')

    def test_rejects_empty_reality_short_ids(self):
        with self.assertRaises(XuiApiError):
            _build_inbound_payload({
                'inbound_payload': {
                    'enable': True,
                    'remark': 'bad-reality',
                    'listen': '',
                    'port': 24445,
                    'protocol': 'vless',
                    'total': 0,
                    'expiryTime': 0,
                    'settings': {'clients': [], 'decryption': 'none', 'fallbacks': []},
                    'streamSettings': {
                        'network': 'tcp',
                        'security': 'reality',
                        'realitySettings': {
                            'target': 'www.amd.com:443',
                            'serverNames': ['www.amd.com'],
                            'privateKey': 'priv',
                            'shortIds': []
                        }
                    },
                    'sniffing': {'enabled': True, 'destOverride': ['http'], 'metadataOnly': False, 'routeOnly': False},
                }
            })

    def test_server_helper_route_forwards_backend(self):
        forwarded = {}

        def fake_xui_request(method, path, json_body=None, config_id=None, **kwargs):
            forwarded['method'] = method
            forwarded['path'] = path
            forwarded['config_id'] = config_id
            return {'success': True, 'obj': {'privateKey': 'priv', 'publicKey': 'pub'}}

        with app.test_client() as client:
            with client.session_transaction() as session:
                session['admin_id'] = 1

            with patch('app._xui_request', side_effect=fake_xui_request):
                response = client.get('/api/xui/server/x25519-cert?backend_id=7')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(forwarded['method'], 'GET')
        self.assertEqual(forwarded['path'], '/panel/api/server/getNewX25519Cert')
        self.assertEqual(forwarded['config_id'], 7)
        self.assertEqual(response.get_json()['cert']['publicKey'], 'pub')


if __name__ == '__main__':
    unittest.main()
