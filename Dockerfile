FROM python:3.7.2
ADD . /todo
WORKDIR /todo
RUN pip install -r requirements.txt
