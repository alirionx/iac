#!/bin/bash

if ! slapcat | grep vdi.dev || [ "$REINIT" == "yes" ]; then
  debconf-set-selections /root/slapd.debconf
  echo -e "slapd slapd/move_old_database boolean true" |debconf-set-selections
  DEBIAN_FRONTEND=noninteractive dpkg-reconfigure slapd
fi


# Irgendwann mal nen Master Slave Sync bauen!!!!

# if [ $JOIN == 'yes' ]; then
#   debconf-set-selections /root/slapd.debconf
#   echo -e "slapd slapd/move_old_database boolean true" |debconf-set-selections
#   DEBIAN_FRONTEND=noninteractive dpkg-reconfigure slapd
# fi

#/usr/sbin/slapd -h "ldap:/// ldapi:///" -g openldap -u openldap -F /etc/ldap/slapd.d

# if [ $ROLE == 'master' ]; then
#   ldapmodify -Y EXTERNAL -H ldapi:/// -f /root/sync-conf_master.ldif
# fi

# if [ -n "${LDAP_MASTER}" ] && [ -n "${LDAP_PWD}" ]; then
#   sed -i 's/{{LDAP_MASTER}}/'$LDAP_MASTER'/' /root/sync-conf_slave.ldif
#   sed -i 's/{{LDAP_PWD}}/'$LDAP_PWD'/' /root/sync-conf_slave.ldif
#   ldapmodify -Y EXTERNAL -H ldapi:/// -f /root/sync-conf_slave.ldif
# fi

/usr/sbin/slapd -h "ldap:/// ldapi:///" -g openldap -u openldap -F /etc/ldap/slapd.d -d 0

#LAZY
#service slapd start
#sleep infinity
