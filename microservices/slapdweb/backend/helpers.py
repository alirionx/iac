
#-Global Vars---------------------------------------------------------------------
slapdHost = "192.168.10.61"
slapdPort = 389
slapdMode = "ldap" # could be ldaps
slapdBaseDn = "dc=vdi,dc=dev"
slapdUsrDn = "cn=admin,dc=vdi,dc=dev" 
slapdUsrPwd = "admin" 
 

#---------------------------------------------------------------------------------

import json
from flask import Response
#------------------------------
from ldap3 import Server, Connection, ALL 
if slapdMode == "ldaps": uSsl = True
else: uSsl = False

#---------------------------------------------------------------------------------
class helpers:
  #-Fixed Class Vars---------------------------------------------


  #-Initializer--------------------------------------------------
  def __init__(self):
    print('*New helpers object created')

  #-The Methods--------------------------------------------------
  def ldap_conn_create(self ):
    conSrv = Server(host=slapdHost, port=slapdPort, use_ssl=uSsl, get_info=ALL)
    try:
      curCon = Connection(conSrv, slapdUsrDn, slapdUsrPwd, auto_bind=True)
      return curCon
    except Exception as e:
      print('Error: ' + str(e))
      return False

    #print(conSrv.info)

  #-------------------------------
  def obj_to_json_http(self, dataObj, status=200):
    resJson = json.dumps(dataObj, indent=2)
    resp = Response(
      response=resJson,
      status=status,
      mimetype="application/json")
    return resp

#--------------------------------------------------------------------------------

class ldaptool:
  #-Fixed Class Vars---------------------------------------------
  myHelper = helpers()
  ldapCon = myHelper.ldap_conn_create()

  #-Initializer--------------------------------------------------
  def __init__(self):
    if not self.ldapCon:
      print("Fail to establish ldap connection ")
    else:
      print('*New ldaptools object created')


  #-The Methods--------------------------------------------------
  def app_pre_config(self ):
    
    ouList = ['groups', 'users']
    ouResList = []
    self.ldapCon.search(slapdBaseDn, '(objectclass=organizationalUnit)')
    ldapEntries = self.ldapCon.entries
    
    for ldapEntrie in ldapEntries:
      ouResList.append(ldapEntrie.entry_dn)
    # print(ouList)

    for ou in ouList:
      if 'ou='+ou+','+slapdBaseDn not in ouResList:
        self.ldapCon.add(
          'ou='+ou+','+slapdBaseDn, 
          'organizationalUnit', {
            'description': 'OrgUnit for directory %s' %ou, 
            'ou': ou
          }
        )

    #---------------------------
    grpList = ['vdi', 'admins']
    grpResList = []
    self.ldapCon.search(slapdBaseDn, '(objectclass=groupOfNames)')
    ldapEntries = self.ldapCon.entries
    
    for ldapEntrie in ldapEntries:
      grpResList.append(ldapEntrie.entry_dn)
    #print(grpResList)

    for grp in grpList:
      if 'cn='+grp+',ou=groups,'+slapdBaseDn not in grpResList:
        self.ldapCon.add(
          'cn='+grp+',ou=groups,'+slapdBaseDn, 
          'groupOfNames', {
            'description': 'Group for %s users' %grp, 
            'cn': grp,
            'member': slapdUsrDn,
          }
        )

  #------------------------------------------------
  def check_user(self, userDn ):
    
    self.ldapCon.search(userDn, '(objectclass=inetOrgPerson)', attributes=["*"])
    try:
      ldapEntrie = self.ldapCon.entries[0]
    except Exception as e:
      print('Error: '+ str(e))
      return False

    resObj = ldapEntrie.entry_attributes_as_dict
    return resObj

  #------------------------------------------------
  def vdi_users_get(self ):
    
    self.ldapCon.search('ou=users,'+slapdBaseDn, '(&(objectclass=inetOrgPerson)(memberOf=cn=vdi,ou=groups,dc=vdi,dc=dev))', attributes=["*"])
    ldapEntrie = self.ldapCon.entries

    resObj = []
    for res in ldapEntrie:
      resPartObj = res.entry_attributes_as_dict
      try: del resPartObj["userPassword"]
      except: inf = "no PWD"
      tmpObj = {}
      for key,val in resPartObj.items():
        if type(val) == list and len(val) == 1:
          tmpObj[key] = val[0]
        else:
          tmpObj[key] = val

      resObj.append(tmpObj)
   
    #print(resObj)
    return resObj

  #------------------------------------------------
  def ldap_auth(self, uid, pwd ):
    userDN = 'uid='+uid+',ou=users,'+slapdBaseDn
    conSrv = Server(host=slapdHost, port=slapdPort, use_ssl=uSsl, get_info=ALL)
    try:
      curCon = Connection(conSrv, userDN, pwd)
      print(userDN)
      return True
    except Exception as e:
      print('Error: ' + str(e))
      return False
  