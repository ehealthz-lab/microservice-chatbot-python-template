#!/usr/bin/python
# -*- coding: utf-8 -*-

# FHIR client

__version__ = '1.0'


import configparser
import json
import time
from objects import tokens
import objects.message_template as message
import requests
import re
import urllib.parse

configfile = "config.conf"  # Configuration file
config = {}

# Client Configuration fom file config.cfg
cfg = configparser.ConfigParser()
if not cfg.read(configfile, "utf8"):
    print("File does not exist")
if cfg.has_option("net_dispatcher", "file_cert_dispatcher"):  # file_cert_dispatcher
    config['RUTA_CERT'] = cfg.get("net_dispatcher", "file_cert_dispatcher")
else:
    print("Config file need to have file_cert_dispatcher field")
if cfg.has_option("general", "debug"):  # file_cert_dispatcher
    debug = int(cfg.get("general", "debug"))
else:
    debug = 1
    print("Config file need to have debug field")


# It sends a POST request
def do_post(url, body, attachment, data):
    token_p = tokens.server_token().get_tokenDB()

    # It avoids errors with the URL (% and +)
    body = urllib.parse.quote(body.encode('UTF-8'))

    AppResp = message.AppResp
    if not body:
        AppResp['message']['body'] = None
    else:
        AppResp['message']['body'] = body
    if not attachment:
        AppResp['message']['attachments'] = None
    else:
        AppResp['message']['attachments'] = attachment

    AppResp['user'] = data['user']
    AppResp['platform'] = data['platform']
    AppResp['message']['timestamp'] = int(time.time())
    payload = bytes(json.dumps(AppResp), 'utf-8')
    header = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token_p['Data']['id_token'],
        'Content-length': str(len(payload))
    }
    try:
        r = requests.post(url, json.dumps(AppResp), headers=header, verify=config['RUTA_CERT'])
    except:
        print('ERROR AL ENVIAR MENSAJE')
        return '400'
    else:
        if debug <= 0:
            print(r.status_code, 'Mensaje enviado')
        if not str(r.status_code).startswith('2'):
            print(r.content)
            print('URL', r.url)
    return r


# It resends the message to other microservice
def do_post_reenviar(url, body):

    token_p = tokens.server_token().get_tokenDB()

    payload = bytes(json.dumps(body), 'utf-8')
    header = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token_p['Data']['id_token'],
        'Content-length': str(len(payload))
    }
    r = requests.post(url, json.dumps(body), headers=header, verify=config['RUTA_CERT'])
    if debug <= 0:
        print(r.status_code, 'Mensaje enviado')
    if not str(r.status_code).startswith('2'):
        print(r.content)
        print('URL', r.url)
    return r


# It sends a GET request
def do_get(url):
    token_p = tokens.server_token().get_tokenDB()

    r = requests.get(url,
                     headers={'Authorization': 'Bearer ' + token_p['Data']['id_token']},
                     verify=config['RUTA_CERT'])
    if debug <= 0:
        print(r.status_code, 'Get Mensaje recibido')

    return r
