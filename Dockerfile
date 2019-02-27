FROM quay.io/keboola/docker-custom-python:latest

COPY . /code/
RUN pip install --upgrade pip
RUN pip install bs4

WORKDIR /data/
CMD ["python", "-u", "/code/main.py"]
