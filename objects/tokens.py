#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#Class that obtains the tokens

import ssl
import socket
import json
import configparser
import urllib
import time
import base64
import requests
from objects import class_token_DB as DB


configfile = "config.conf"  # Configuration file
    

class server_token():

    def __init__(self):
        self.config = {}

        # Client Configuration from file config.cfg
        cfg = configparser.ConfigParser()  
        if not cfg.read(configfile, "utf8"):  # if not cfg.read(["config.cfg"]):
            print("File does not exist")
        if cfg.has_option("net_oauth", "url_oauth"): #url_oauth
            self.config['URL_OAUTH'] = cfg.get("net_oauth", "url_oauth")
        else:
            print ("Config file need to have url_oauth field")
        if cfg.has_option("net_oauth", "file_cert_oauth"):  # file_cert_oauth
            self.config['RUTA_CERT'] = cfg.get("net_oauth", "file_cert_oauth")
        else:
            print ("Config file need to have file_cert_oauth field")
        if cfg.has_option("net_oauth", "client_id"):  # client_id
            self.config['CLIENT_ID'] = cfg.get("net_oauth", "client_id")
        else:
            print ("Config file need to have client_id field")
        if cfg.has_option("net_oauth", "secret"):  # secret
            self.config['SECRET'] = cfg.get("net_oauth", "secret")
        else:
            print ("Config file need to have secret field")

        # It obtains the Host and the Port
        url = urllib.parse.urlparse(self.config['URL_OAUTH'])
        self.config['HOSTNAME'] = url.hostname
        self.config['PORT'] = url.port
    
        # Path for the comunication
        if not url.path == '':
            self.config['PATH'] = url.path
        else:
            self.config['PATH'] = '/'
        if not url.params == '':
            self.config['PATH'] = self.config['PATH']+';'+url.params
        if not url.query == '':
            self.config['PATH'] = self.config['PATH']+'?'+url.query
        if not url.fragment == '':
            self.config['PATH'] = self.config['PATH']+'#'+url.fragment
        # Path to obtain the authentication token
        self.config['PATH'] = self.config['PATH']+'&client_id='+self.config['CLIENT_ID']+'&client_secret='+self.config['SECRET']
        
    
    def get_token(self):
        try:
            # Connection and token request
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.config['HOSTNAME'], self.config['PORT']))
            s = ssl.wrap_socket(s, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1)
            s.sendall(bytes("GET "+self.config['PATH']+" HTTP/1.1\r\nHost: "+self.config['HOSTNAME']+"\r\nConnection: close\r\n\r\n", 'utf-8'))

            headers = {}
            data = {}
            aux = 1
            while True:
                message = s.recv(4096)
                if aux == 1:   # Status code
                    print(str(message,'utf-8').replace("\r\n","") + "  NEW TOKEN")

                if aux == 2 or aux == 3 or aux == 4:  # Headers (Server, Date, Content-type)
                    mensaje = str(message, 'utf-8').replace("\r\n", "").replace(" ", "")
                    mensaje = mensaje.split(":")
                    headers[mensaje[0]] = mensaje[1]

                if aux == 5:  # (Start response)
                    pass
        
                if aux == 6:  # Response
                    mensaje = str(message, 'utf-8').replace("'", "").replace("\r\n", "")\
                        .replace(" ", "").replace("{", "").replace("}", "")
                    raw = mensaje
                    # It converts string into dictionary to work easily
                    mensaje = mensaje.split(",")
                    for d in range(len(mensaje)):
                        data_aux = mensaje[d]
                        data_aux = data_aux.split(":")
                        data[data_aux[0]] = data_aux[1]

                if not message: #End response
                    s.close()
                    break
                aux=aux+1
        except:
            print('Error in GET token')

        try:
            DB.token.headers = headers
            DB.token.data = data
            print('New token received')
        except:
            print('Save token Error')


    def exp_token(self):
        # It loads the saved token
        try:
            token_id = DB.token.data['id_token'].split('.')
        except:
            print('Error in token loading')

        # Decodification of time exp in token
        try:
            payload = base64.b64decode(token_id[1]+ '==')
            payload = json.loads(payload)
        except:
            print('Error in token decoding')

        # It checks the expiration time
        if int(time.time()) < payload['exp']:
            pass
        else:
            # If it is expired, it updates automatically
            self.get_token()


    def get_tokenDB(self):
        # It loads the saved token
        token = {}
        token['Headers'] = DB.token.headers
        token['Data'] = DB.token.data
        return token # It allows to extract the token for authentication in communication
