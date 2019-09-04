#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Flask App

import json
import configparser
import re
from flask import Flask, request, abort
from registrationAPIgateway import registration, deregistration
from objects import tokens
from credentials import interceptors as auth
from resources import datos_user
from resources.operation_kernel import operacion_kernel
import aiml
from unicodedata import normalize
import time
import urllib.parse
import resources.send_message as send
import logging.handlers
import signal
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)
configfile = "config.conf" # Configuration file

app = Flask(__name__)

actualizar = False  # Used not to desregister if a message is sent to /shutdown

# It changes the default log of Flask, generating it only for errors
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)


#---------------------------------------------------------------------------------------------------------------------#
# It turns off the server; when it wants to update, the registration is not done
#---------------------------------------------------------------------------------------------------------------------#
@app.route('/shutdown', methods=['POST'])
def shutdown():
    tokenHeader = request.headers.get('Authorization')
    decodedtoken = auth.auth_jwt(tokenHeader)

    if decodedtoken is None:
        abort(401)
        resp = '401'
        print('Unauthorized')
        return 'Unauthorized'
    else:
        global actualizar
        actualizar = True
        shutdown_server()
        return 'Server shutting down...'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    logger_error.error('Server Shutting Down...')
    func()


#---------------------------------------------------------------------------------------------------------------------#
# It receives messages to know the status of the microservice, if it responds it is active
#---------------------------------------------------------------------------------------------------------------------#
@app.route('/status', methods=['GET'])
def handle_status():
    return '200 OK'


#---------------------------------------------------------------------------------------------------------------------#
# Main part of the program
# Route to which the messages sent by the user arrive
#---------------------------------------------------------------------------------------------------------------------#
@app.route('/message', methods=['POST'])
def handle_message(*args, **kwargs):
    # It checks the token
    tokenHeader = request.headers.get('Authorization')
    decodedtoken = auth.auth_jwt(tokenHeader)

    AppResp = {"user": "000",
               "platform": "",
               "message":
                   {"timestamp": 0,
                    "attachments": None,
                    "body": "Default"}
               }

    if not decodedtoken:
        # Security Error; unauthorized
        abort(401)
        resp = '401'
        print('Unauthorized')

    else:
        if request.headers['Content-Type'] == 'application/json':

            # It obtains the json
            data={}
            data = json.loads(request.data.decode('utf-8'))

            # It obtains the user information in the database, passing the id (phone number)
            user = datos_user.userDB()
            user_data = user.get_user_data(data['user'])
            # It adds 'user' in the response
            AppResp['user'] = data['user']

            # Message sent by the user
            aux = data['message']['body']

            # It prevents the content of the input message from being wrong; only special characters
            aux = normalize('NFC', aux)
            aux = aux.replace('.', ' ').replace('?', ' ').replace('!', ' ')
            m = re.match('^[^a-zA-Z0-9ñ]*$', aux)
            if m:
                mensaje = 'Vaya, no te he entendido. Repítemelo por favor'
                AppResp['message']['body'] = mensaje
                resp = app.make_response(json.dumps(AppResp))
                user_data['runningFunctionality'] = config['client_id']
                user.change_user_data(data['user'], user_data)
                return resp
            if debug <= -1:
                print('NUEVA CONEXIÓN: ENTRADA', aux)
            # A log is generated with the user and the input message
            logger.info('- Origen: ' + data['user'] + ' Destino: Chatbot Message: ' + str(aux))

            # Bot response
            try:
                # It sends the input message to the AIML
                respuesta = str(kernel.respond(str(aux), data['user'])).replace('\\n', '\n').replace('\\t', '   ')
            except Warning as err:
                if debug <= 0:
                    print(err)
                # There is no match for the input message
                logger_error.exception(err)
                respuesta = 'Ups, parece que ha habido un error 😅Vuelve a intentarlo;'
                user_data['runningFunctionality'] = None
                user.change_user_data(data['user'], user_data)
            except Exception as err:
                if debug <= 0:
                    print(err)
                logger_error.exception(err)
                respuesta = 'Ups, parece que ha habido un error 😅Vuelve a intentarlo;'
                user_data['runningFunctionality'] = None
                user.change_user_data(data['user'], user_data)

            # It checks the value of the kernel task variable (indicates the function to be performed)
            oob = kernel.getPredicate('oob', data['user'])
            # If there is a tasks to be performed oob!=null
            contador_maximo = 8
            while oob and oob != 'null':
                try:
                    add_response = operacion_kernel(oob, kernel, data, logger_error)
                except Exception as err:
                    if debug <= 0:
                        print(err)
                    logger_error.exception(err)
                    respuesta = 'Ups, parece que ha habido un error 😅Vuelve a intentarlo;'
                    kernel.setPredicate('oob', '', data['user'])
                    user_data['runningFunctionality'] = None
                    user.change_user_data(data['user'], user_data)

                else:
                    respuesta = respuesta + add_response
                    respuesta = respuesta.replace('Uso interno', '')
                oob = kernel.getPredicate('oob', data['user'])
                contador_maximo = contador_maximo - 1  # To prevent errors
                if contador_maximo == 0:
                    break

            if debug <= -1:
                print('RESPUESTA KERNEL + OOB: ' + respuesta)
            # Log of the response
            logger.info('- Origen: Chatbot Destino: ' + data['user'] + ' Message: ' + str(respuesta))

            # If the message contains ';' it marks the separation between several messages
            # It sends several messages to the user
            aux = respuesta.split(';')
            token = tokens.server_token().get_tokenDB()
            for position, mensaje in enumerate(aux):
                # It sends a message to url_message
                AppResp['message']['body'] = mensaje
                # It only sends here. If there is more than one message, the last one is not sent yet
                if position + 1 is not len(aux):
                    attachment = ''
                    r = send.do_post(config['url_message'], mensaje, attachment, data)
                    time.sleep(2)
            # The last reply message is generated
            AppResp['message']['body'] = urllib.parse.quote(AppResp['message']['body'])

            # It obtains the value of the microservice variable from the kernel; used to indicate what
            # microservice the user has to run
            microservicio = kernel.getPredicate('microservicio', data['user'])

            # It changes the user functionality based on the bot response
            if microservicio == 'null':
                if debug <= 0:
                    print('Salir del microservicio')
                user_data['runningFunctionality'] = None
                # It prevents the message from being sent empty
                if not AppResp['message']['body']:
                    AppResp['message']['body'] = 'Vale, salimos.'
            else:
                user_data['runningFunctionality'] = config['client_id']
                # It prevents the message from being sent empty
                if not AppResp['message']['body']:
                    AppResp['message']['body'] = 'Ups, parece que ha habido un error 😅Vuelve a intentarlo'
                    user_data['runningFunctionality'] = None
                    if debug <= -5:
                        print(data)
                        print(AppResp['message']['body'])
                        print(AppResp['user'])

            # It changes the values of the user in the database
            user.change_user_data(data['user'], user_data)
            # It generates the response and the headers
            resp = app.make_response(json.dumps(AppResp))
            if debug <= -5:
                print(resp.data)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Content-Type'] = 'application/json'
            resp.headers['Authorization'] = 'Bearer ' + token['Data']['id_token']
            # It sends the response
        else:
            abort(415, 'Unsupported Media Type')
            resp = '415'
            print('Unsupported Media Type')

    return resp


if __name__ == '__main__':

    # Server Configuration from file config.cfg
    config = {}
    cfg = configparser.ConfigParser()
    if not cfg.read(configfile):
        print("File does not exist")
    if cfg.has_option("net", "ip"):  # ip
        config['ip'] = cfg.get("net", "ip")
    else:
        print("Config file need to have ip field")
    if cfg.has_option("net", "port"):  # port
        config['port'] = int(cfg.get("net", "port"))
    else:
        print("Config file need to have port field")
    if cfg.has_option("net", "file_key"):  # file_key
        config['file_key'] = cfg.get("net", "file_key")
    else:
        print("Config file need to have file_key field")
    if cfg.has_option("net", "file_cert"):  # file_key
        config['file_cert'] = cfg.get("net", "file_cert")
    else:
        print("Config file need to have file_cert field")
    if cfg.has_option("net_dispatcher", "url_message"):  # url message
        config['url_message'] = cfg.get("net_dispatcher", "url_message")
    else:
        print("Config file need to have url_message field")
    if cfg.has_option("net_dispatcher", "client_id"):  # client_id
        config['client_id'] = cfg.get("net_dispatcher", "client_id")
    else:
        print("Config file need to have client_id field")
    if cfg.has_option("net_dispatcher", "url_attachment"):  # url attachment
        config['url_attachment'] = cfg.get("net_dispatcher", "url_attachment")
    else:
        print("Config file need to have url_attachment field")
    if cfg.has_option("general", "debug"):  # file_cert_dispatcher
        debug = int(cfg.get("general", "debug"))
    else:
        debug = 1
        print("Config file need to have debug field")
    # Server settings
    if cfg.has_option("net", "file_key"):
        network_setting = {
            "addr": config['ip'],
            "port": config['port'],
            "ssl": {
                "cert": config['file_cert'],
                "key": config['file_key']
            }
        }
    else:
        network_setting = {
            "addr": config['ip'],
            "port": config['port'],
        }

    # It creates the Kernel and the AIML file that it needs to learn
    config['file_aiml'] = cfg.get("bot", "file_aiml")
    kernel = aiml.Kernel()
    kernel.learn(config['file_aiml'])
    kernel.respond("LOAD AIML B")

    # It creates the loggers
    filename = 'logs/Interaction.log'
    # It creates a log that changes each day the name
    logger = logging.getLogger('INTERACCIONES')
    logger.setLevel('INFO')
    logger.propagate = False
    # It creates a log for connections, which stores a maximum of 60 days
    file_handler = logging.handlers.TimedRotatingFileHandler(filename, when='midnight', interval=1, encoding='utf-8',
                                                             backupCount=60)
    formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Events log (errors)
    logger_error = logging.getLogger('Errors')
    fh = logging.handlers.RotatingFileHandler('logs/errors.log', maxBytes=200 * 1024, backupCount=5)
    fh.setFormatter(formatter)
    logger_error.propagate = False
    logger_error.addHandler(fh)

    # Authentication token
    tokens.server_token().get_token()

    # API gateway registration; it keeps trying until it gets an answer
    while True:
        try:
            tokens.server_token().get_token()
            # Register in the API gateway
            reg = registration.registration()
            reg.register()
            break
        except:
            time.sleep(4)
            pass
    signal.signal(signal.SIGTERM, sigterm_handler)
    logger_error.error('Server Starting...')
    try:
        # It starts the server
        if 'ssl' in network_setting:
            app.run(host=network_setting['addr'], port=network_setting['port'], threaded=True,
                    ssl_context=(network_setting['ssl']['cert'], network_setting['ssl']['key']))
        else:
            app.run(host=network_setting['addr'], port=network_setting['port'], threaded=True)

    except KeyboardInterrupt:
        print('Keyboard interrupt received: EXITING')

    finally:
        logger_error.error('Server Shutting Down...')
        # API gateway deregistration
        if not actualizar:
            dereg = deregistration.deregistration()
            dereg.deregister()
