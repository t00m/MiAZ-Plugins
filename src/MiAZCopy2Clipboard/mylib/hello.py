#!/usr/bin/python3

from MiAZ.backend.log import MiAZLog

log = MiAZLog('HelloWorld')

def hello_world():
    log.info("Hi everybody!")
