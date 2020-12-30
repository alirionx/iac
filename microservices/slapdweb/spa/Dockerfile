FROM ubuntu:focal

RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y \
    nginx

COPY ./dist/. /var/www/html/
COPY nginx.conf /etc/nginx/sites-enabled/default

#LAZY
#CMD python3 /app/slapdweb_backend.py

CMD nginx -g 'daemon off;'
#CMD nginx
