#!/bin/bash

if [ ! -z "${GUACD_HOSTNAME}" ]; then
  TGTHOST=${GUACD_HOSTNAME}
else
  TGTHOST=guacamole
fi
sed -i 's/GUACD_HOSTNAME/'$TGTHOST'/g' /etc/nginx/sites-enabled/default

nginx -g 'daemon off;'
