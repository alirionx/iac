#!/bin/bash

#/usr/bin/mysqld_safe > /dev/null 2>&1 &
#MYPID=$(cat /proc/sys/kernel/ns_last_pid)
#echo $MYPID

service mysql start

if [ ! -z "${MYUSR}" ] &&  [ ! -z "${MYPWD}" ]; then
  mysql -e "grant all privileges on *.* to '"$MYUSR"'@'%' identified by '"$MYPWD"';"
fi

if [ ! -z "${MYDB}" ]; then
  mysql -e "create schema $MYDB CHARACTER SET = 'utf8' COLLATE = 'utf8_german2_ci';"
fi

if [ -d "/inject" ]; then
  for filename in /inject/*.sql; do
    cat $filename | mysql $MYDB
  done  
fi

#kill -9 $MYPID
service mysql stop

/usr/bin/mysqld_safe