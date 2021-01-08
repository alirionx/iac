FROM ubuntu:focal

RUN echo "Europe/Berlin" > /etc/timezone
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
  sudo nano supervisor \
  net-tools iputils-ping \
  libnss-ldap libpam-ldap ldap-utils \
  ubuntu-mate-desktop xrdp 
  #xorgxrdp
  #ubuntu-desktop

RUN export SUDO_FORCE_REMOVE=yes && DEBIAN_FRONTEND=noninteractive apt install -y sudo-ldap
RUN apt remove -y blueman

COPY common-password /etc/pam.d/common-password
COPY common-session /etc/pam.d/common-session
COPY ldap.conf /etc/ldap.conf
#COPY sudo-ldap.conf /etc/sudo-ldap.conf
COPY nsswitch.conf /etc/nsswitch.conf
COPY useradd.skel /etc/default/useradd

RUN mkdir /var/run/dbus
RUN echo "mate-session" > /etc/skel/.Xsession

#-LAZY!!!
#CMD rm /run/xrdp/xrdp-sesman.pid && /usr/sbin/xrdp-sesman && /usr/sbin/xrdp --nodaemon

COPY supervisord_xrdp.conf /etc/supervisor/conf.d/xrdp.conf
CMD supervisord --nodaemon -c /etc/supervisor/supervisord.conf
