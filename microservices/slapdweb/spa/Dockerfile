FROM ubuntu:focal

RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y \
    nginx

COPY ./dist/. /var/www/html/
COPY nginx.conf /etc/nginx/sites-enabled/default

COPY start.sh /root/start.sh
RUN chmod +x /root/start.sh
CMD /root/start.sh

#CMD nginx -g 'daemon off;'
#CMD nginx

