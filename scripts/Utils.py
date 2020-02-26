# Copyright (C) 2020, M.B.Moessner
#
# SPDX-License-Identifier: Apache-2.0 
#

import sys
import os
import io
import glob
import logging
import shutil
import hashlib
import psutil
from subprocess import *

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s",datefmt='%Y-%m-%d %H:%M:%S')
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
logger = logging.getLogger()

# Compute a hash over both lists and compare
# Return 1 if they are equal, else 0
def compareLists(lA, lB):
  m = hashlib.sha1()
  n = hashlib.sha1()

  for i in range(len(lA)):
    m.update(lA[i].encode("utf-8"))

  for i in range(len(lB)):
    n.update(lB[i].encode("utf-8"))

  m = m.hexdigest()
  n = n.hexdigest()

  if m == n:
    return 1

  return 0

def run_cmd(cmd, workdir, *args, **kwargs):
  if "env" in kwargs:
    cmdEnv = kwargs.get("env", None)
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT,shell=True, bufsize=1,  cwd=workdir, env=cmdEnv)
  else:
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT,shell=True, bufsize=1,  cwd=workdir)

  for line in iter(p.stdout.readline, b''):
    tmp = str(line)
    if tmp.endswith("\\r\\n'"):
      logger.info(tmp[2:len(tmp)-5])
    elif tmp.endswith("\\r\\n\""):
      logger.info(tmp[2:len(tmp)-5])
    else:
      logger.info(tmp[2:len(tmp)-3])
  p.stdout.close()
  p.wait()

def run_cmd_ng(cmd, workdir, *args, **kwargs):
  if "env" in kwargs:
    cmdEnv = kwargs.get("env", None)
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT,shell=True,  cwd=workdir, env=cmdEnv)
  else:
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT,shell=True,  cwd=workdir)
  for line in io.TextIOWrapper(p.stdout, encoding="utf-8"):
    if line[0] == "[": 
        if line[1] == "E" or line[1] == "W" or line[1] == "I" or line[1] == "D": 
      #print(len(line))
            print (line.rstrip())
  #for line in iter(p.stdout.readline, ""):
  #    print (line.rstrip())
   # tmp = str(line)
   # if tmp.endswith("\\r\\n'"):
   #   logger.info(tmp[2:len(tmp)-5])
   # elif tmp.endswith("\\r\\n\""):
   #   logger.info(tmp[2:len(tmp)-5])
   # else:
   #   logger.info(tmp[2:len(tmp)-3])
  p.stdout.close()
  p.wait()


def run_build(ninjaBin,workDir):
  if not os.path.exists(workDir):
    logger.error("Error build folder does not exist. Run config")
    sys.exit()

  cmd = [ninjaBin]
  cmd.append("-v")
  run_cmd(cmd, workDir)


def run_install(ninjaBin,workDir):
  if not os.path.exists(workDir):
    logger.error("Error build folder does not exist. Run config")
    sys.exit()

  cmd = [ninjaBin]
  cmd.append("install")
  cmd.append("-v")
  run_cmd(cmd, workDir)
  
