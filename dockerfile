# parent image
FROM python:3.7-slim

LABEL PRD="PRD"

WORKDIR /usr/src/app

# install FreeTDS
RUN apt-get update
RUN apt-get install unixodbc -y
RUN apt-get install unixodbc-dev -y
RUN apt-get install freetds-dev -y
RUN apt-get install freetds-bin -y
RUN apt-get install tdsodbc -y
RUN apt-get install --reinstall build-essential -y

# populate "ocbdinst.ini"
RUN echo "[FreeTDS]\n\
Description = FreeTDS unixODBC Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini

RUN echo "[sqlserver]\n\
driver = FreeTDS\n\
server = 10.101.189.35\n\
port = 1433\n\
TDS_Version = 4.2" >> /etc/odbc.ini

RUN odbcinst -i -s -f /etc/odbc.ini

# Edit odbc.ini, odbcinst.ini, and freetds.conf files
RUN echo "[sqlserver]\n\
host = 10.101.189.35\n\
port = 1433\n\
tds version = 4.2" >> /etc/freetds.conf

# Set the timzone to EST
#RUN cp /usr/share/zoneinfo/US/Eastern /etc/localtime
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#Install required python dependencies
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python"]
CMD ["./main.py"]