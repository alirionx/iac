FROM ubuntu:focal

RUN apt update && \
    apt install -y \
    python3 \
    python3-pip \
    gunicorn

RUN pip3 install flask ldap3 pymysql

RUN mkdir /app
COPY *.py /app/

WORKDIR /app

#LAZY
#CMD python3 /app/slapdweb_backend.py

CMD gunicorn --bind 0.0.0.0:5000 slapdweb_backend:app
