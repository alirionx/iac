FROM ubuntu:focal

RUN apt update && apt install -y mariadb-server mariadb-client

#RUN /usr/bin/mysqld_safe > /dev/null 2>&1 &

RUN echo '[mysqld]' >> /etc/mysql/my.cnf
RUN echo 'bind-address = 0.0.0.0' >> /etc/mysql/my.cnf

COPY start.sh /root/
RUN chmod +x /root/start.sh

EXPOSE 3306
#CMD /usr/bin/mysqld_safe
CMD /root/start.sh

#run via: docker run -d -p3306:3306 -e MYUSR=penner -e MYPWD=penner -e MYDB=guacamole_db -v $PWD/inject:/inject --name myriadb1 manager1:5000/myriadb:v01