FROM python:3.8

ADD main.py .

COPY . /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt
# create sqlite3 database "ss_all_with_class.sqlite3"



CMD ["python", "./main.py"]