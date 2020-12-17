FROM ubuntu:focal

COPY ./slapd.debconf /root/
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y slapd ldap-utils

# COPY sync-conf_master.ldif /root/
# COPY sync-conf_slave.ldif /root/

COPY memof-mod_apply.ldif /root/
COPY memof-mod_enable.ldif /root/
RUN /usr/sbin/slapd -h "ldap:/// ldapi:///" -g openldap -u openldap -F /etc/ldap/slapd.d && \
    ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f /root/memof-mod_enable.ldif && \
    ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /root/memof-mod_apply.ldif

COPY start.sh /root/start.sh
RUN chmod +x /root/start.sh

EXPOSE 389

#LAZY!!!
CMD /root/start.sh
#VOLUME /var/lib/ldap
#VOLUME /etc/ldap/slapd.d