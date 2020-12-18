FROM ubuntu:focal

COPY ./slapd.debconf /root/
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y slapd ldap-utils

RUN debconf-set-selections /root/slapd.debconf && \
    DEBIAN_FRONTEND=noninteractive dpkg-reconfigure slapd

#-Howto dazu: https://www.xinux.net/index.php/Openldap_posix_memberof----
COPY memberof_config.ldif /root/
COPY refint1.ldif /root/
COPY refint2.ldif /root/

RUN /usr/sbin/slapd -h "ldap:/// ldapi:///" -g openldap -u openldap -F /etc/ldap/slapd.d && \
    ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /root/memberof_config.ldif && \
    ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f /root/refint1.ldif && \
    ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /root/refint2.ldif
#-------------------------------------------------------------------------

COPY start.sh /root/start.sh
RUN chmod +x /root/start.sh

EXPOSE 389

#LAZY!!!
CMD /root/start.sh
#VOLUME /var/lib/ldap
#VOLUME /etc/ldap/slapd.d