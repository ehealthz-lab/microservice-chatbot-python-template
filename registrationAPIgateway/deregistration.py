#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
from objects import tokens
import requests

configfile = "config.conf"  # Configuration file


class deregistration():

    def __init__(self):
        self.config = {}

        # Client Configuration from file config.cfg
        cfg = configparser.ConfigParser()
        if not cfg.read(configfile, "utf8"): #if not cfg.read(["config.cfg"]):
            print ("File does not exist")
        if cfg.has_option("net_dispatcher", "client_id"): #client_id
            self.config['CLIENT_ID'] = cfg.get("net_dispatcher", "client_id")
        else:
            print ("Config file need to have client_id field")
        if cfg.has_option("net_dispatcher", "file_cert_dispatcher"): #file_cert_dispatcher
            self.config['RUTA_CERT'] = cfg.get("net_dispatcher", "file_cert_dispatcher")
        else:
            print ("Config file need to have file_cert_dispatcher field")
        if cfg.has_option("net_dispatcher", "delete_functionality"): #delete_functionality
            self.config['DELETE_FUNCTIONALITY'] = (cfg.get("net_dispatcher", "delete_functionality"))
        else:
            print ("Config file need to have delete_functionality field")

    def deregister(self):
        # It checks expiration time of the token
        tokens.server_token().exp_token()

        # It obtains the token
        token = tokens.server_token().get_tokenDB()

        # It deletes the funcionality in the database
        data = requests.delete(self.config['DELETE_FUNCTIONALITY'] + "?client_id=" + self.config['CLIENT_ID'],
                               headers={'Authorization': 'Bearer ' + token['Data']['id_token']},
                               verify=self.config['RUTA_CERT'])
        print(data.content)
