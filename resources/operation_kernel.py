#!/usr/bin/python
# -*- coding: utf-8 -*-

import configparser

configfile = "config.conf"  # Configuration file
config = {}
# Client Configuration fom file config.cfg
cfg = configparser.ConfigParser()
if not cfg.read(configfile, "utf8"):
    print("File does not exist")
if cfg.has_option("general", "debug"):  # file_cert_dispatcher
    debug = int(cfg.get("general", "debug"))
else:
    debug = 1
    print("Config file need to have debug field")


# Funcion that defines the operations that the kernel performs
def operacion_kernel(oob, kernel, data, logger):
    response = ''
    # La variable OOB indica la operación a realizar
    if oob == 'FOO':
        # Do what operations it needs
        ''

    kernel.setPredicate('oob', 'null', data['user'])

    return response
