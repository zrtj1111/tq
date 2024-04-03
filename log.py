# -*- encoding: utf-8 -*-
import logging
import os
from logging.handlers import RotatingFileHandler

fhandler = RotatingFileHandler(os.path.join("zq.log"),
                               mode="a+",
                               maxBytes=1024 * 1024 * 10,
                               backupCount=10,
                               encoding="utf-8")
chandler = logging.StreamHandler()

formatter = logging.Formatter(
    "%(asctime)s %(filename)s <%(funcName)s> [%(lineno)d] <%(module)s> - %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")

chandler.setFormatter(formatter)
fhandler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.addHandler(fhandler)
logger.addHandler(chandler)
