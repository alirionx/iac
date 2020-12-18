FROM ubuntu:focal

RUN apt update && \
    apt install -y \
    python3 \
    python3-pip

RUN pip3 install flask ldap3

RUN mkdir /app
COPY backend.py /app/

CMD python3 /app/backend.py

