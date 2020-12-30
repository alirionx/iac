
#-Global Vars---------------------------------------------------------------------
import os
if "LDAP_HOSTNAME" in os.environ:
  slapdHost = os.getenv('LDAP_HOSTNAME')
else: 
  slapdHost = "slapd"

#slapdHost = "192.168.10.61"
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

#myHost = "192.168.10.61"
myHost = "myriadb"
myPort = 3306
myUsr = "maria"
myPwd = "maria"
myDb = "guacamole_db"
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
  try:
    conSrv = Server(host=slapdHost, port=slapdPort, use_ssl=uSsl)
    curCon = Connection(conSrv, slapdUsrDn, slapdUsrPwd, auto_bind=True, version=3)
  except Exception as e:
    print('Error: '+ str(e))

  #-Initializer--------------------------------------------------
  def __init__(self):
    print('*New ldaptools object created')
    # self.conSrv = Server(host=slapdHost, port=slapdPort, use_ssl=uSsl)
    # try:
    #   self.curCon = Connection(self.conSrv, slapdUsrDn, slapdUsrPwd, auto_bind=True, version=3)
    #   print('*New ldaptools object created')
    # except Exception as e:
    #   print('Error: '+ str(e))
    #   return None
      

  #-The Methods--------------------------------------------------
  # def ldap_conn_create(self ):
    
  #   try:
  #     curCon.bind()
  #     return curCon
  #   except Exception as e:
  #     print('Error: ' + str(e))
  #     return False

    #print(conSrv.info)


  def con_check(self ):
    ldapSrv = Server(host=slapdHost, port=slapdPort, use_ssl=uSsl)
    ldapCon = Connection(ldapSrv)
    ldapCon.bind()

  #-----------------------------

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
        self.curCon.add(
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

    return True

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


  def vdi_user_ids_get(self ):
    self.curCon.search('ou=users,'+slapdBaseDn, '(&(objectclass=inetOrgPerson)(memberOf=cn=vdi,ou=groups,dc=vdi,dc=dev))', attributes=["uid"])
    ldapEntries = self.curCon.entries

    resObj = []
    for res in ldapEntries:
      resPartObj = res.entry_attributes_as_dict
      resObj.append(resPartObj['uid'][0])
   
    #print(resObj)
    return resObj

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
    except Exception as e:
      print('Error: '+ str(e))
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
  def vdi_user_setpwd(self, dataObj ):
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
    res = self.curCon.modify(userDn, changes=ldapChanges )
    
    return res

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
    
    authRes = self.curCon.rebind(user=userDn, password=pwd)

    self.curCon.search(initGrpObj["admins"], '(objectclass=groupOfNames)', attributes=["member"])
    try:
      ldapEntryAry = self.curCon.entries[0]['member']
    except:
      return False

    if userDn not in ldapEntryAry:
      return False
    else:
      return authRes

    
    # authRes = self.curCon.rebind(user=userDn, password=pwd)
    # self.curCon.search(userDn, '(objectclass=inetOrgPerson)', attributes=["memberOf"])

    # try:
    #   memOfs = self.curCon.entries[0]["memberOf"]
    # except:
    #   return False

    # if initGrpObj["admins"] not in memOfs:
    #   authRes = False
   
    #return authRes


#--------------------------------------------------------------------------------
class mysqltool:
  #-Fixed Class Vars---------------------------------------------
  try:
    myCon = pymysql.connect(host=myHost, port=myPort, user=myUsr, passwd=myPwd, db=myDb)
    myCurs = myCon.cursor(pymysql.cursors.DictCursor)
  except Exception as e:
    print('Error: '+ str(e))

  #-Initializer--------------------------------------------------
  def __init__(self):
    print('*New mysqltools object created')
    # try:
    #   self.myCon = pymysql.connect(myHost, myUsr, myPwd, myDb, myPort)
    #   self.myCurs = self.myCon.cursor(pymysql.cursors.DictCursor)
    #   print('*New mysqltools object created')
    # except Exception as e:
    #   print('Error: '+ str(e))
    #   return None
      


  #-The Methods--------------------------------------------------
  def con_check(self):
    pymysql.connect(myHost, myUsr, myPwd, myDb, myPort)

  def vdi_user_ids_get(self ):
    self.myCurs.execute('''
      SELECT 
        a.name, 
        b.organization

        FROM guacamole_entity a
        JOIN guacamole_user b
        ON (a.entity_id = b.entity_id)

        WHERE b.organization = 'ldap'
      ;
    ''')
    qryRes = self.myCurs.fetchall()
    myUsrAry = []
    for row in qryRes:
      if row['name'] != guacAdm:
        myUsrAry.append(row['name'])
    
    return myUsrAry

  #-----------------------------------------
  def chk_groups(self ):
    self.myCurs.execute("SELECT * FROM guacamole_entity WHERE name = '%s';" % guacVdiGrp)
    qryRes = self.myCurs.fetchone()
    if qryRes == None:
      self.myCurs.execute("INSERT INTO guacamole_entity (name, type) VALUES('%s', 'USER_GROUP');" % guacVdiGrp)
      self.myCon.commit()

      self.myCurs.execute("SELECT entity_id FROM guacamole_entity WHERE name = '%s';" % guacVdiGrp)
      qryRes = self.myCurs.fetchone()
      entityId = qryRes['entity_id']

      self.myCurs.execute("INSERT INTO guacamole_user_group (entity_id, disabled) VALUES('%s', 0);" % entityId)
      self.myCon.commit()


  #-----------------------------------------
  def ldap_guacamole_sync(self ):
    
    self.chk_groups()

    myUsrAry = self.vdi_user_ids_get()

    tmpLdapTool = ldaptool()
    ldapUsrAry = tmpLdapTool.vdi_user_ids_get()
       
    print(ldapUsrAry, myUsrAry)

    #--------------------------------------
    for uid in ldapUsrAry:
      if uid not in myUsrAry:
        self.myCurs.execute('''
          INSERT INTO guacamole_entity (name, type)
          VALUES ('%s', 'USER');
        ''' %uid)
        self.myCon.commit()
        self.myCurs.execute('''
          SELECT
            entity_id,
            CONVERT(CURRENT_TIMESTAMP, CHAR(50)) as TIMESTAMP
          FROM guacamole_entity
          WHERE
            name = '%s'
            AND type = 'USER';
        ''' %uid)
        qryRes = self.myCurs.fetchone()
        print(qryRes)
        entityId = str(qryRes['entity_id'])
        curTimestamp = qryRes['TIMESTAMP']
        
        self.myCurs.execute('''
          INSERT INTO guacamole_user 
            ( entity_id, password_hash, password_date, organization ) 
            VALUES ('''+entityId+''', "1234", "'''+curTimestamp+'''", "ldap"); 
          ''')
        self.myCon.commit()

    #--------------------------------------
    for uid in ldapUsrAry:
      self.myCurs.execute("SELECT entity_id FROM guacamole_entity WHERE name = '%s';" % uid)
      qryRes = self.myCurs.fetchone()
      guacVdiUsrId = str(qryRes['entity_id'])

      self.myCurs.execute('''
        SELECT 
        a.entity_id, 
        b.user_group_id

        FROM guacamole_entity a
        JOIN guacamole_user_group b
        ON (a.entity_id = b.entity_id)

        WHERE a.name = "%s";
      ''' % guacVdiGrp)
      qryRes = self.myCurs.fetchone()
      guacVdiGrpId = str(qryRes['user_group_id'])


      #print(guacVdiGrpId, guacVdiUsrId)
      self.myCurs.execute("SELECT * FROM guacamole_user_group_member WHERE user_group_id = "+guacVdiGrpId+" AND member_entity_id = "+guacVdiUsrId+";")
      qryRes = self.myCurs.fetchone()
      print(qryRes)
      if qryRes == None:
        self.myCurs.execute("INSERT INTO guacamole_user_group_member (user_group_id, member_entity_id) VALUES("+guacVdiGrpId+","+guacVdiUsrId+");" )
        self.myCon.commit()

    #--------------------------------------
    for usr in myUsrAry:
      if usr not in ldapUsrAry:
        self.myCurs.execute("DELETE FROM guacamole_entity WHERE name = '%s';" %usr)
        self.myCon.commit()

    return True

#--------------------------------------------------------------------------------