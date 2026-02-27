FROM mysql:8.0

RUN microdnf install -y \
    curl \
    make \
 && microdnf clean all

WORKDIR app

COPY Makefile .
COPY schema/mysql.sql schema/mysql.sql

ENV MYSQL_DATABASE acris

ENTRYPOINT ["make"]
CMD ["mysql"]