FROM python:3.9-slim
RUN mkdir /app
COPY ./* /app/
WORKDIR /app

RUN python ./setup.py install

CMD ["tellyget", "-h"]