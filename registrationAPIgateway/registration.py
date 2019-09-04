#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
from objects import tokens
import requests

configfile = "config.conf"  # Configuration file


class registration():

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
        if cfg.has_option("net_dispatcher", "boolean_menu"):  # boolean_menu
            self.config['MENU'] = cfg.getboolean("net_dispatcher", "boolean_menu")
        else:
            print("Config file need to have boolean_menu field")
        if cfg.has_option("net_dispatcher", "addrr"):  # addrr
            self.config['ADDRR'] = cfg.get("net_dispatcher", "addrr")
        else:
            print("Config file need to have addrr field")
        if cfg.has_option("net_dispatcher", "canUse"):  # canUse
            self.config['CANUSE'] = cfg.get("net_dispatcher", "canUse")
        else:
            print("Config file need to have canUse field")
        if cfg.has_option("net_dispatcher", "client_id"):  # client_id
            self.config['CLIENT_ID'] = cfg.get("net_dispatcher", "client_id")
        else:
            print("Config file need to have client_id field")
        if cfg.has_option("net_dispatcher", "message"):  # message
            self.config['MESSAGE'] = cfg.get("net_dispatcher", "message")
        else:
            print("Config file need to have message field")
        if cfg.has_option("net_dispatcher", "new_functionality"):  # new_functionality
            self.config['NEW_FUNCTIONALITY'] = cfg.get("net_dispatcher", "new_functionality")
        else:
            print("Config file need to have new_functionality field")

    def register(self):
        # It checks expiration time of the token
        tokens.server_token().exp_token()

        # It obtains the token
        token = tokens.server_token().get_tokenDB()

        # It adds the functionality in the database
        data = requests.post(self.config['NEW_FUNCTIONALITY'],
                             json={"client_id": self.config['CLIENT_ID'],
                                   "message": self.config['MESSAGE'],
                                   "menu": self.config['MENU'],
                                   "address": self.config['ADDRR'],
                                   "canUse": [self.config['CANUSE']]},
                             headers={'Authorization': 'Bearer ' + token['Data']['id_token']},
                             verify=self.config['RUTA_CERT'])

        print('Registration: ', data.content)
