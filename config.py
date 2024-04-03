# -*- encoding: utf-8 -*-
import configparser
import os

cfg_dir = os.path.dirname(os.path.abspath(__file__))
_cf = configparser.ConfigParser()
_cf.read(os.path.join(cfg_dir, "tq.conf"))

# [app]
# COMPANY = __cf.get('zq', 'company')
# VERSION = __cf.get('zq', 'version')
# AUTHOR = __cf.get('zq', 'author')
DEBUG = _cf.get("tq", "debug")
TRADE_DATA_DIR = _cf.get("tq", "trade_data")
CODE_FILE = os.path.join(TRADE_DATA_DIR, "code.ftr")
