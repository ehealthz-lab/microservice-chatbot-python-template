import json
from credentials.JWT import jwt_validator

def auth_jwt(authHeader):
    with open('credentials/security.conf') as config_file:
        config = json.loads(config_file.read())
        validator = jwt_validator(config['jwt_validator'])
        aux = authHeader.split(' ')
        if aux[0] == 'Bearer':
            token = aux[1]
            decoded_token = validator.decode_token(token)
            if decoded_token is not None:
                return decoded_token
