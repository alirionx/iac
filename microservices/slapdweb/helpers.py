
#-Global Vars---------------------------------------------------------------------
slapdHost = "192.168.10.61"
slapdPort = 389
slapdMode = "ldap" # could be ldaps
slapdBaseDn = "dc=vdi,dc=dev"
slapdUsrDn = "cn=admin,dc=vdi,dc=dev" 
slapdUsrPwd = "admin" 


#---------------------------------------------------------------------------------
class helpers:
  #-Fixed Class Vars---------------------------------------------


  #-Initializer--------------------------------------------------
  def __init__(self):
    print('*New helpers object created')

  #-The Methods--------------------------------------------------
  def ldap_conn_create(self ):
    from ldap3 import Server, Connection, ALL
    
    if slapdMode == "ldaps": uSsl = True
    else: uSsl = False
    
    conSrv = Server(host=slapdHost, port=slapdPort, use_ssl=uSsl, get_info=ALL)
    try:
      curCon = Connection(conSrv, slapdUsrDn, slapdUsrPwd, auto_bind=True)
      return curCon
    except Exception as e:
      print(str(e))
      return False

    #print(conSrv.info)

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
    grpResList = []
    self.ldapCon.search(slapdBaseDn, '(objectclass=groupOfNames)')
    ldapEntries = self.ldapCon.entries
    
    for ldapEntrie in ldapEntries:
      grpResList.append(ldapEntrie.entry_dn)
    print(grpResList)
    if 'cn=vdi,ou=groups,'+slapdBaseDn not in grpResList:
      self.ldapCon.add(
        'cn=vdi,ou=groups,'+slapdBaseDn, 
        'groupOfNames', {
          'description': 'Group for VDI users', 
          'cn': 'vdi',
          'member': slapdUsrDn,
        }
      )

  #------------------------------------------------
  def check_user(self, userDn ):
    self.ldapCon.search(userDn, '(objectclass=*)', attributes=["*"])
    ldapEntrie = self.ldapCon.entries[0]
    #res = ldapEntrie.entry_attributes_as_dict
    print(ldapEntrie.entry_to_json())