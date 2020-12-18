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
from flask import Flask, request, session
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
app.secret_key = "changeit"
app.debug = True

#-The API Request Handler Area-------------------------------------

@app.route('/', methods=['GET'])
def hello_app():
  return 'Hello from the SlapdWebApp API!'

#--------------------------
@app.route('/auth', methods=['POST'])
def app_auth():
  try:
    postIn = request.get_json()
    uid = postIn["uid"]
    pwd = postIn["pwd"]
  except Exception as e:
    print('Error: ' + str(e))
    resObj = {
      "status": "400 Bad Request",
      "msg": "Invalid input format. Post (uid and pwd (key, val)) in JSON!"
    }
    httpRes = myHelper.obj_to_json_http(resObj, 400)
    return httpRes

  #jsonStr = myHelper.obj_to_json_http(postIn)

  authRes = myLdapTool.ldap_auth(uid, pwd)
  if not authRes:
    resObj = {
      "status": "401 Unauthorized",
      "msg": "Invalid user and/or password, login failed"
    }
    httpRes = myHelper.obj_to_json_http(resObj, 401)
    return httpRes
  else:
    session["uid"] = uid
    resObj = {
      "status": "200 Ok",
      "msg": "User "+uid+" successfully logged in."
    }
    httpRes = myHelper.obj_to_json_http(resObj)
    return httpRes
  
#--------------------------
@app.route('/api/logout', methods=['POST'])
def api_logout():
  chk = True
  uid = str
  try:
    postIn = request.get_json()
    uid = postIn["uid"]
  except:
    chk = False
  
  if chk and uid == session["uid"]:
    session.pop('uid', None)
    resObj = {
      "status": "200 Ok",
      "msg": "Logout successfully"
    }
    httpRes = myHelper.obj_to_json_http(resObj, 200)
  else:
    resObj = {
      "status": "400 Bad Request",
      "msg": "Fail to logout"
    }
    httpRes = myHelper.obj_to_json_http(resObj, 400)
  
  return httpRes

#--------------------------
@app.route('/api/test/userinfo/<dn>', methods=['GET'])
def api_test_userinfo(dn):

  resObj = myLdapTool.check_user(dn)

  if not resObj:
    resObj = {
      "msg": "user dn not found",
      "status": "404 Not Found"
    }
  
  httpRes = myHelper.obj_to_json_http(resObj)
  return httpRes

#--------------------------
@app.route('/api/users', methods=['GET'])
def api_users_get():

  resObj = myLdapTool.vdi_users_get()
  httpRes = myHelper.obj_to_json_http(resObj)
  return httpRes
   

#-Pre-Handlers-----------------------------------------------------
@app.before_first_request
def check_ldap_ready():
  myLdapTool.app_pre_config()

@app.before_request
def check_access():
  if request.path.startswith('/api') and "uid" not in session:
    resObj = {
      "status": "401 Unauthorized",
      "msg": "not logged in"
    }
    httpRes = myHelper.obj_to_json_http(resObj, 401)
    return httpRes


#-App Runner------------------------------------------------------
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)

#------------------------------------------------------------------