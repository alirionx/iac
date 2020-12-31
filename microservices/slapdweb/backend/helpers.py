import os
#-Global Vars---------------------------------------------------------------------

varAry = {
  "slapdHost": {
    "std": "slapd",
    "env": "LDAP_HOSTNAME",
    "type": "str"
  },
  "slapdPort": {
    "std": 389,
    "env": "LDAP_PORT",
    "type": "int"
  },
  "myHost": {
    "std": "myriadb",
    "env": "MYSQL_HOSTNAME",
    "type": "str"
  },
  "myPort": {
    "std": 3306,
    "env": "MYSQL_PORT",
    "type": "int"
  },
  "myDb": {
    "std": "guacamole_db",
    "env": "MYSQL_DATABASE",
    "type": "str"
  },
  "myUsr": {
    "std": "maria",
    "env": "MYSQL_USER",
    "type": "str"
  },
  "myPwd": {
    "std": "maria",
    "env": "MYSQL_PASSWORD",
    "type": "str"
  }
}

enVars = {}

for key, obj in varAry.items():
  if obj["env"] in os.environ:
    if obj["type"] == "int":
      enVars[key] = int(os.getenv(obj["env"]))
    else:
      enVars[key] = os.getenv(obj["env"])
  else:
    enVars[key] = obj["std"]


#slapdHost = "192.168.10.61"
slapdHost = enVars["slapdHost"]
slapdPort = enVars["slapdPort"]
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

#myHost = "192.168.10.61"
myHost = enVars["myHost"]
myPort = enVars["myPort"]
myUsr = enVars["myUsr"]
myPwd = enVars["myPwd"]
myDb = enVars["myDb"]
guacAdm = "guacadmin"
guacVdiGrp = "vdi"

#---------------------------------------------------------------------------------

import json
from flask import Response
#------------------------------
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, MODIFY_ADD, HASHED_MD5
from ldap3.utils.hashed import hashed
if slapdMode == "ldaps": uSsl = True
else: uSsl = False

import pymysql

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
    print('*New ldaptools object created')
      

  #-The Methods--------------------------------------------------

  def create_ldap_cli(self ):
    conSrv = Server(host=slapdHost, port=slapdPort, use_ssl=uSsl)
    ldapCon = Connection(conSrv, slapdUsrDn, slapdUsrPwd, auto_bind=True, version=3)

    return ldapCon

  #-OLD-#
  def con_check(self ):
    ldapSrv = Server(host=slapdHost, port=slapdPort, use_ssl=uSsl)
    ldapCon = Connection(ldapSrv)
    ldapCon.bind()

  #-----------------------------

  def app_pre_config(self ):
    ldapCon = self.create_ldap_cli()

    ouList = ['groups', 'users']
    ouResList = []
    ldapCon.search(slapdBaseDn, '(objectclass=organizationalUnit)')
    ldapEntries = ldapCon.entries
    
    for ldapEntrie in ldapEntries:
      ouResList.append(ldapEntrie.entry_dn)
    # print(ouList)

    for ou in ouList:
      if 'ou='+ou+','+slapdBaseDn not in ouResList:
        ldapCon.add(
          'ou='+ou+','+slapdBaseDn, 
          'organizationalUnit', {
            'description': 'OrgUnit for directory %s' %ou, 
            'ou': ou
          }
        )

    #---------------------------
    grpResList = []
    ldapCon.search(slapdBaseDn, '(objectclass=groupOfNames)')
    ldapEntries = ldapCon.entries
    
    for ldapEntrie in ldapEntries:
      grpResList.append(ldapEntrie.entry_dn)
    print(grpResList)

    for grp, dn in initGrpObj.items():
      if dn not in grpResList:
        ldapCon.add(
          dn,
          'groupOfNames', {
            'description': 'Group for %s users' %grp, 
            'cn': grp,
            'member': slapdUsrDn,
          }
        )

    return True

  #------------------------------------------------
  def check_user(self, userDn ):
    ldapCon = self.create_ldap_cli()

    ldapCon.search(userDn, '(objectclass=inetOrgPerson)', attributes=["*"])
    try:
      ldapEntrie = ldapCon.entries[0]
    except Exception as e:
      print('Error: '+ str(e))
      return False

    resObj = ldapEntrie.entry_attributes_as_dict
    try: del resObj['userPassword']
    except: inf = 'no pwd'
    return resObj

  #------------------------------------------------
  def vdi_get_next_uid_number(self ):
    ldapCon = self.create_ldap_cli()

    uidNbrTmp = 5000
    ldapCon.search(slapdBaseDn, '(objectclass=inetOrgPerson)', attributes=["uidNumber"])
    ldapEntries = ldapCon.entries
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
    ldapCon = self.create_ldap_cli()

    ldapCon.search('ou=users,'+slapdBaseDn, '(&(objectclass=inetOrgPerson)(memberOf=cn=vdi,ou=groups,dc=vdi,dc=dev))', attributes=["*"])
    ldapEntries = ldapCon.entries

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
    ldapCon = self.create_ldap_cli()

    ldapCon.search('uid='+uid+',ou=users,'+slapdBaseDn, '(&(objectclass=inetOrgPerson)(memberOf=cn=vdi,ou=groups,dc=vdi,dc=dev))', attributes=["*"])
    
    if len(ldapCon.entries) < 1:
      return False

    ldapEntry = ldapCon.entries[0]
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

  #----------------------------
  def vdi_user_ids_get(self ):
    ldapCon = self.create_ldap_cli()

    ldapCon.search('ou=users,'+slapdBaseDn, '(&(objectclass=inetOrgPerson)(memberOf=cn=vdi,ou=groups,dc=vdi,dc=dev))', attributes=["uid"])
    ldapEntries = ldapCon.entries

    resObj = []
    for res in ldapEntries:
      resPartObj = res.entry_attributes_as_dict
      resObj.append(resPartObj['uid'][0])
   
    #print(resObj)
    return resObj

  #------------------------------------------------
  def vdi_user_create(self, dataObj ):
    ldapCon = self.create_ldap_cli()
    
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
    res = ldapCon.add(userDn, ['inetOrgPerson', 'posixAccount', 'top'], dataObj)
    print(ldapCon.result)
    res = ldapCon.modify(initGrpObj['vdi'], { 'member': [(MODIFY_ADD, [userDn] ) ] } )
    print(ldapCon.result)
    return res

  #------------------------------------------------
  def vdi_user_edit(self, dataObj ):
    ldapCon = self.create_ldap_cli()

    try: 
      uid = dataObj['uid']
      del dataObj['uid']
    except Exception as e:
      print('Error: '+ str(e))
      return False

    if slapdBaseDn in uid:
      userDn = uid
    else:
      userDn = 'uid='+uid+',ou=users,'+slapdBaseDn
    
    chk = True
    for key, val in dataObj.items():
      res = ldapCon.modify(userDn, { key: [(MODIFY_REPLACE, [val] ) ] } )
      if not res: chk = res
    
    return chk

  #------------------------------------------------
  def vdi_user_setpwd(self, dataObj ):
    ldapCon = self.create_ldap_cli()
    try: 
      uid = dataObj['uid']
      pwd = dataObj['pwd']
    except Exception as e:
      print('Error: '+ str(e))
      return False

    if slapdBaseDn in uid:
      userDn = uid
    else:
      userDn = 'uid='+uid+',ou=users,'+slapdBaseDn
    
    hashedPwd = hashed(HASHED_MD5, pwd)
    ldapChanges = {
      'userPassword': [(MODIFY_REPLACE, [hashedPwd])]
    }
    res = ldapCon.modify(userDn, changes=ldapChanges )
    
    return res

  #------------------------------------------------
  def vdi_users_delete(self, uid ):
    ldapCon = self.create_ldap_cli()

    if slapdBaseDn in uid:
      userDn = uid
    else:
      userDn = 'uid='+uid+',ou=users,'+slapdBaseDn
    #print(userDn)
    res = ldapCon.delete(userDn)
    return res

  #------------------------------------------------
  def ldap_auth(self, usr, pwd ):
    ldapCon = self.create_ldap_cli()

    if slapdBaseDn in usr:
      userDn = usr
    else:
      userDn = 'uid='+usr+',ou=users,'+slapdBaseDn
    
    authRes = ldapCon.rebind(user=userDn, password=pwd)

    ldapCon.search(initGrpObj["admins"], '(objectclass=groupOfNames)', attributes=["member"])
    try:
      ldapEntryAry = ldapCon.entries[0]['member']
    except:
      return False

    if userDn not in ldapEntryAry:
      return False
    else:
      return authRes


#--------------------------------------------------------------------------------
class mysqltool:
  #-Fixed Class Vars---------------------------------------------


  #-Initializer--------------------------------------------------
  def __init__(self):
    print('*New mysqltools object created')
      

  #-The Methods--------------------------------------------------
  def create_mysql_cli(self, autoCommit=True ):
    myCon = pymysql.connect(host=myHost, port=myPort, user=myUsr, passwd=myPwd, db=myDb, autocommit=autoCommit)
    myCurs = myCon.cursor(pymysql.cursors.DictCursor)
    return myCurs

  #-OLD-#
  def con_check(self):
    myCon = pymysql.connect(host=myHost, port=myPort, user=myUsr, passwd=myPwd, db=myDb)
    myCurs = myCon.cursor(pymysql.cursors.DictCursor)
    myCurs.execute("SHOW TABLES;")


  def vdi_user_ids_get(self ):
    myCurs = self.create_mysql_cli()

    myCurs.execute('''
      SELECT 
        a.name, 
        b.organization

        FROM guacamole_entity a
        JOIN guacamole_user b
        ON (a.entity_id = b.entity_id)

        WHERE b.organization = 'ldap'
      ;
    ''')
    qryRes = myCurs.fetchall()
    myUsrAry = []
    for row in qryRes:
      if row['name'] != guacAdm:
        myUsrAry.append(row['name'])
    
    return myUsrAry

  #-----------------------------------------
  def chk_groups(self ):
    myCurs = self.create_mysql_cli()

    myCurs.execute("SELECT * FROM guacamole_entity WHERE name = '%s';" % guacVdiGrp)
    qryRes = myCurs.fetchone()
    if qryRes == None:
      myCurs.execute("INSERT INTO guacamole_entity (name, type) VALUES('%s', 'USER_GROUP');" % guacVdiGrp)
      #self.myCon.commit()

      myCurs.execute("SELECT entity_id FROM guacamole_entity WHERE name = '%s';" % guacVdiGrp)
      qryRes = myCurs.fetchone()
      entityId = qryRes['entity_id']

      myCurs.execute("INSERT INTO guacamole_user_group (entity_id, disabled) VALUES('%s', 0);" % entityId)
      #self.myCon.commit()


  #-----------------------------------------
  def ldap_guacamole_sync(self ):
    myCurs = self.create_mysql_cli()

    self.chk_groups()

    myUsrAry = self.vdi_user_ids_get()

    tmpLdapTool = ldaptool()
    ldapUsrAry = tmpLdapTool.vdi_user_ids_get()
       
    print(ldapUsrAry, myUsrAry)

    #--------------------------------------
    for uid in ldapUsrAry:
      if uid not in myUsrAry:
        myCurs.execute('''
          INSERT INTO guacamole_entity (name, type)
          VALUES ('%s', 'USER');
        ''' %uid)
        #self.myCon.commit()
        myCurs.execute('''
          SELECT
            entity_id,
            CONVERT(CURRENT_TIMESTAMP, CHAR(50)) as TIMESTAMP
          FROM guacamole_entity
          WHERE
            name = '%s'
            AND type = 'USER';
        ''' %uid)
        qryRes = myCurs.fetchone()
        print(qryRes)
        entityId = str(qryRes['entity_id'])
        curTimestamp = qryRes['TIMESTAMP']
        
        myCurs.execute('''
          INSERT INTO guacamole_user 
            ( entity_id, password_hash, password_date, organization ) 
            VALUES ('''+entityId+''', "1234", "'''+curTimestamp+'''", "ldap"); 
          ''')
        #self.myCon.commit()

    #--------------------------------------
    for uid in ldapUsrAry:
      myCurs.execute("SELECT entity_id FROM guacamole_entity WHERE name = '%s';" % uid)
      qryRes = myCurs.fetchone()
      guacVdiUsrId = str(qryRes['entity_id'])

      myCurs.execute('''
        SELECT 
        a.entity_id, 
        b.user_group_id

        FROM guacamole_entity a
        JOIN guacamole_user_group b
        ON (a.entity_id = b.entity_id)

        WHERE a.name = "%s";
      ''' % guacVdiGrp)
      qryRes = myCurs.fetchone()
      guacVdiGrpId = str(qryRes['user_group_id'])


      #print(guacVdiGrpId, guacVdiUsrId)
      myCurs.execute("SELECT * FROM guacamole_user_group_member WHERE user_group_id = "+guacVdiGrpId+" AND member_entity_id = "+guacVdiUsrId+";")
      qryRes = myCurs.fetchone()
      print(qryRes)
      if qryRes == None:
        myCurs.execute("INSERT INTO guacamole_user_group_member (user_group_id, member_entity_id) VALUES("+guacVdiGrpId+","+guacVdiUsrId+");" )
        #self.myCon.commit()

    #--------------------------------------
    for usr in myUsrAry:
      if usr not in ldapUsrAry:
        myCurs.execute("DELETE FROM guacamole_entity WHERE name = '%s';" %usr)
        #self.myCon.commit()

    return True

#--------------------------------------------------------------------------------