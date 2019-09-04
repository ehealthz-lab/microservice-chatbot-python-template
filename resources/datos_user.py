#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
from objects import tokens
import requests
import json

configfile = "config.conf" # Configuration file


class userDB():

    def __init__(self):
        self.config = {}

        # Client Configuration from file config.cfg
        cfg = configparser.ConfigParser()
        if not cfg.read(configfile, "utf8"):  # if not cfg.read(["config.cfg"]):
            print("File does not exist")
        if cfg.has_option("net_dispatcher", "file_cert_dispatcher"):  # file_cert_dispatcher
            self.config['RUTA_CERT'] = cfg.get("net_dispatcher", "file_cert_dispatcher")
        else:
            print("Config file need to have file_cert_dispatcher field")
        if cfg.has_option("net_dispatcher", "db_request"):  # db_request
            self.config['DB_REQUEST'] = cfg.get("net_dispatcher", "db_request")
        else:
            print("Config file need to have db_request field")
        if cfg.has_option("general", "debug"):  # file_cert_dispatcher
            debug = int(cfg.get("general", "debug"))
        else:
            debug = 1
            print("Config file need to have debug field")

    def get_user_data(self, user_number):
        # It checks expiration time of the token
        tokens.server_token().exp_token()

        # It obtains the token
        token = tokens.server_token().get_tokenDB()

        # Connection with the API gateway
        data_DB = requests.post(self.config['DB_REQUEST'], json={"url": "users/_find?criteria={\"id_signal\":\""+
        user_number+"\"}", "data": None}, headers={'Authorization': 'Bearer ' + token['Data']['id_token']}, verify=
        self.config['RUTA_CERT'])

        # It obtains the patient data
        return data_DB.json()['results'][0]

    def change_user_data(self, user_number, data_user):
        # It checks expiration time of the token
        tokens.server_token().exp_token()

        # POST message to send
        data_user = json.dumps(data_user)
        data_user = data_user.replace('"','\"')
        
        # It obtains the token
        token = tokens.server_token().get_tokenDB()
        
        # Connection with the API gateway
        resp = requests.post(self.config['DB_REQUEST'], json={"url": "users/_update", "data": "criteria={\"id_signal\": "
                                "\""+user_number+"\"}&newobj="+data_user},
                                headers={'Authorization': 'Bearer ' + token['Data']['id_token']}, verify=
                                self.config['RUTA_CERT'])
        print(resp)
