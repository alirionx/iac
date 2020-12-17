#!/usr/bin/python3

#-Load required base modules---------------------------------------
import os
import sys
import json
import importlib

#-Try to load required extra modules-------------------------------

modList = ["flask", "ldap3"]
errList = []
for mod in modList:
  try:
    impChk = importlib.import_module(mod)
  except:
    errList.append(mod)

if len(errList) > 0:
  print("The following pathon3 modules need to be installed for thos app:")
  print(", ".join(errList))
  exit("exiting...")

#------------------------------------
from flask import Flask, request
#import ldap3
from ldap3 import Server, Connection, SAFE_SYNC
from helpers import helpers, ldaptool
#------------------------------------------------------------------

#-Global Vars------------------------------------------------------
CurPath = os.path.dirname(os.path.realpath(__file__))

try: myHelper 
except: myHelper = helpers()
try: myLdapTool
except: myLdapTool = ldaptool()

#-Build the flask app object---------------------------------------
app = Flask(__name__)
app.debug = True

#-The API Request Handler Area-------------------------------------

@app.route('/')
def hello_app():
  return 'Hello from the SlapdWebApp API!'

#--------------------------
@app.route('/api/ldaptest')
def ldap_test():
  curCon = myHelper.ldap_conn_create()
  myDN = curCon.extend.standard.who_am_i()

  myLdapTool.app_pre_config()
  myLdapTool.check_user('uid=penner,ou=users,dc=vdi,dc=dev')

  return('<h2>%s</h2>' % str(myDN))


#-App Runner------------------------------------------------------
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)

#------------------------------------------------------------------