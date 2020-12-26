FROM ubuntu:focal

RUN echo "Europe/Berlin" > /etc/timezone
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
  sudo nano \
  net-tools iputils-ping \
  libnss-ldap libpam-ldap ldap-utils \
  ubuntu-mate-desktop xrdp 
  #xorgxrdp
  #ubuntu-desktop

RUN apt remove blueman

COPY common-password /etc/pam.d/common-password
COPY common-session /etc/pam.d/common-session
COPY ldap.conf /etc/ldap.conf
COPY nsswitch.conf /etc/nsswitch.conf

RUN mkdir /var/run/dbus
RUN echo "mate-session" > /etc/skel/.Xclients

#-LAZY!!!
CMD /usr/sbin/xrdp-sesman && /usr/sbin/xrdp --nodaemon