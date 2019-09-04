import jwt
import ast
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
import time
import json
import OpenSSL
import base64


class jwt_issuer():

    # Load the information needed to act as ID provider
    def __init__(self, config):
        self.issuer = config['issuer']
        self.algorithm = config['algorithm']
        self.private_key = self.load_private_key(config['private_key'])

    def load_private_key(self, path):
        with open(path) as key_file:
            # Private key object from OpenSSL module
            private_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM
, key_file.read())
        # Private key object from cryptography module
        private_key = private_key.to_cryptography_key()
        return private_key

    def create_token(self, sub, aud=None, scope=None):

        # Issued at
        iat = int(time.time())
        # Expiration time
        exp = int(time.time()) + 3600

        payload = {
            'iss': self.issuer,
            'sub': sub,
            'iat': iat,
            'exp': exp,
        }

        if aud != None:
            payload['aud'] = aud
        if scope != None:
            payload['scope'] = scope

        return payload

    def sign_token(self, token):
        token = jwt.encode(token, self.private_key, algorithm=self.algorithm)

        # Check if we can decode the token
        while True:
            for i in range(4):
                try:
                    decoded_token = (token + '=' * i).decode('base64')
                    token = token + '=' * i
                    return token
                except:
                    if i == 3:
                        token = jwt.encode(token, self.private_key, algorithm=self.algorithm)



class jwt_validator():

    # Load trusted issuers
    def __init__(self, config):
        self.trusted_issuers = {}
        for issuer in config['trusted_issuers'].keys():
            self.trusted_issuers[issuer] = self.load_public_key(config['trusted_issuers'][issuer])

    def load_public_key(self, path):
        with open(path) as cert_file:
            certificate = load_pem_x509_certificate(cert_file.read().encode(), default_backend())
        public_key = certificate.public_key()
        return public_key

    def decode_token(self, token):

    # Ensure we can decode the token
        for i in range(4):
            try:
                try:
                    header = (token.split('.')[0]+ '=' * i).decode('base64')
                    header = json.loads(header)
                except:
                    header = base64.b64decode((token.split('.')[0] + '=' * i)).decode('utf-8')
                    header = ast.literal_eval(header)
            except Exception as e:
                print(e)
                if i == 3:
                    return None

        for i in range(4):
            try:
                try:
                    payload = (token.split('.')[1] + '=' * i).decode('base64')
                    payload = json.loads(payload)
                except:
                    payload = base64.urlsafe_b64decode((token.split('.')[1] + '==' * i)).decode('utf-8')
                    payload = ast.literal_eval(payload)
            except Exception as e:
                print(e)
                if i == 3:
                    return None

        if payload['iss'] in self.trusted_issuers:
            public_key = self.trusted_issuers[payload['iss']]
            try:
                if 'aud' in payload:
                    result = jwt.decode(token, public_key, audience=payload['aud'])
                else:
                    result = jwt.decode(token, public_key, algorithms=['RS256'], leeway=10)
                return result
            except Exception as e:
                print(e)
                print("Error in token decoding")
                return None
        else:
            print('Untrusted issuer')
            return None
