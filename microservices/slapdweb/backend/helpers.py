
#-Global Vars---------------------------------------------------------------------
slapdHost = "192.168.10.61"
slapdPort = 389
slapdMode = "ldap" # could be ldaps
slapdBaseDn = "dc=vdi,dc=dev"

slapdUsrDn = "cn=admin,dc=vdi,dc=dev" 
slapdUsrPwd = "admin" 

slapdAdminGrp = "cn=admins,ou=groups,dc=vdi,dc=dev"
slapdVdiGrp = "cn=vdi,ou=groups,dc=vdi,dc=dev"
initGrpAry = [slapdAdminGrp, slapdVdiGrp] 
initGrpObj = {
  "admins": "cn=admins,ou=groups,dc=vdi,dc=dev",
  "vdi": "cn=vdi,ou=groups,dc=vdi,dc=dev"
}

#---------------------------------------------------------------------------------

import json
from flask import Response
#------------------------------
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, MODIFY_ADD
if slapdMode == "ldaps": uSsl = True
else: uSsl = False

#---------------------------------------------------------------------------------
class helpers:
  #-Fixed Class Vars---------------------------------------------


  #-Initializer--------------------------------------------------
  def __init__(self):
    print('*New helpers object created')

  #-The Methods--------------------------------------------------
  

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

  #-Initializer--------------------------------------------------
  def __init__(self):
    self.conSrv = Server(host=slapdHost, port=slapdPort, use_ssl=uSsl)
    try:
      self.curCon = Connection(self.conSrv, slapdUsrDn, slapdUsrPwd, auto_bind=True, version=3)
      print('*New ldaptools object created')
    except Exception as e:
      print('Error: '+ str(e))
      return None
      

  #-The Methods--------------------------------------------------
  # def ldap_conn_create(self ):
    
  #   try:
  #     curCon.bind()
  #     return curCon
  #   except Exception as e:
  #     print('Error: ' + str(e))
  #     return False

    #print(conSrv.info)

  def app_pre_config(self ):
    
    ouList = ['groups', 'users']
    ouResList = []
    self.curCon.search(slapdBaseDn, '(objectclass=organizationalUnit)')
    ldapEntries = self.curCon.entries
    
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
    grpResList = []
    self.curCon.search(slapdBaseDn, '(objectclass=groupOfNames)')
    ldapEntries = self.curCon.entries
    
    for ldapEntrie in ldapEntries:
      grpResList.append(ldapEntrie.entry_dn)
    print(grpResList)

    for grp, dn in initGrpObj.items():
      if dn not in grpResList:
        self.curCon.add(
          dn,
          'groupOfNames', {
            'description': 'Group for %s users' %grp, 
            'cn': grp,
            'member': slapdUsrDn,
          }
        )

  #------------------------------------------------
  def check_user(self, userDn ):
    
    self.curCon.search(userDn, '(objectclass=inetOrgPerson)', attributes=["*"])
    try:
      ldapEntrie = self.curCon.entries[0]
    except Exception as e:
      print('Error: '+ str(e))
      return False

    resObj = ldapEntrie.entry_attributes_as_dict
    try: del resObj['userPassword']
    except: inf = 'no pwd'
    return resObj

  #------------------------------------------------
  def vdi_get_next_uid_number(self ):
    uidNbrTmp = 5000
    self.curCon.search(slapdBaseDn, '(objectclass=inetOrgPerson)', attributes=["uidNumber"])
    ldapEntries = self.curCon.entries
    uidNbrs = []
    for res in ldapEntries:
      resPartObj = res.entry_attributes_as_dict
      uidNbrs.append(resPartObj["uidNumber"][0])
    
    newUidNbr = False
    while newUidNbr == False:
      uidNbrTmp += 1
      if uidNbrTmp not in uidNbrs:
        newUidNbr = uidNbrTmp

    return newUidNbr

  #------------------------------------------------
  def vdi_users_get(self ):
    
    self.curCon.search('ou=users,'+slapdBaseDn, '(&(objectclass=inetOrgPerson)(memberOf=cn=vdi,ou=groups,dc=vdi,dc=dev))', attributes=["*"])
    ldapEntries = self.curCon.entries

    resObj = []
    for res in ldapEntries:
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
  def vdi_user_get(self, uid ):
    
    self.curCon.search('uid='+uid+',ou=users,'+slapdBaseDn, '(&(objectclass=inetOrgPerson)(memberOf=cn=vdi,ou=groups,dc=vdi,dc=dev))', attributes=["*"])
    
    if len(self.curCon.entries) < 1:
      return False

    ldapEntry = self.curCon.entries[0]
    resPartObj = ldapEntry.entry_attributes_as_dict
    try: del resPartObj["userPassword"]
    except: inf = "no PWD"
    tmpObj = {}
    for key,val in resPartObj.items():
      if type(val) == list and len(val) == 1:
        tmpObj[key] = val[0]
      else:
        tmpObj[key] = val

    return tmpObj

  #------------------------------------------------
  def vdi_user_create(self, dataObj ):
    try:
      userDn = 'uid='+dataObj['cn']+',ou=users,'+slapdBaseDn
    except:
      return False
    
    uidNbr = self.vdi_get_next_uid_number()
    
    try:
      del dataObj['uid']
      dataObj['uidNumber'] = uidNbr
      dataObj['gidNumber'] = 0
    except Exception as e:
      print('Error: '+ str(e))

    #print(userDn, dataObj, uidNbr)
    res = self.curCon.add(userDn, ['inetOrgPerson', 'posixAccount', 'top'], dataObj)
    print(self.curCon.result)
    res = self.curCon.modify(initGrpObj['vdi'], { 'member': [(MODIFY_ADD, [userDn] ) ] } )
    print(self.curCon.result)
    return res

  #------------------------------------------------
  def vdi_user_edit(self, dataObj ):
    try: 
      uid = dataObj['uid']
      del dataObj['uid']
    except:
      return False

    if slapdBaseDn in uid:
      userDn = uid
    else:
      userDn = 'uid='+uid+',ou=users,'+slapdBaseDn
    
    chk = True
    for key, val in dataObj.items():
      res = self.curCon.modify(userDn, { key: [(MODIFY_REPLACE, [val] ) ] } )
      if not res: chk = res
    
    return chk

  #------------------------------------------------
  def vdi_users_delete(self, uid ):
    if slapdBaseDn in uid:
      userDn = uid
    else:
      userDn = 'uid='+uid+',ou=users,'+slapdBaseDn
    #print(userDn)
    res = self.curCon.delete(userDn)
    return res

  #------------------------------------------------
  def ldap_auth(self, usr, pwd ):
    if slapdBaseDn in usr:
      userDn = usr
    else:
      userDn = 'uid='+usr+',ou=users,'+slapdBaseDn

    #print(userDn)

    authRes = self.curCon.rebind(user=userDn, password=pwd)
    self.curCon.search(userDn, '(objectclass=inetOrgPerson)', attributes=["memberOf"])
    
    try:
      memOfs = self.curCon.entries[0]["memberOf"]
    except:
      return False

    if initGrpObj["admins"] not in memOfs:
      authRes = False
   
    return authRes
  