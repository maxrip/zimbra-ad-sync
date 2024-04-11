#!/usr/bin/python3

import sys,os,time,yaml
from lib.local import LocalLdap
from lib.remote import RemoteLdap
from lib.logger import MyLogger
from lib.diff import Diff
from lib.prov import Cli

config = yaml.safe_load(open("config.yml"))

logger = MyLogger(config['loglevel'])
local = LocalLdap(logger,config)
remote = RemoteLdap(logger,config)
local.sync()
remote.sync()

diff = Diff(logger,config,local.users,remote.users,local.dl,remote.dl)
diff.generateUserDiff()
diff.generateDlDiff()


if len(diff.syscalls) > 0:
    logger.debug('%s',diff.syscalls)
    if config['executeCarbonio']: 
        try:
            Cli.executeCarbonio(diff.syscalls,config['sysCallLenght'],config['cmdBulk'])
        except Exception as err:
            logger.error('execute cli error: %s',err)
