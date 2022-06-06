FROM python:3.8

ADD main.py .

COPY . /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt

CMD ["python", "./main.py"]