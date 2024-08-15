FROM python:3.11.4-alpine

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/PY/BIN:$PATH"

#RUN adduser --disabled-password --gecos '' amir
#RUN chown -R amir:amir /code
#USER amir

RUN pip install --upgrade pip

COPY . /code

RUN pip install -r requirements.txt
