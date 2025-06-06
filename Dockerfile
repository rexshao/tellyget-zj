FROM python:3.9-slim
RUN mkdir /app
COPY ./* /app/
WORKDIR /app
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple/ --no-cache-dir  beautifulsoup4 requests requests-toolbelt pycryptodome netifaces
RUN python ./setup.py install

CMD ["tellyget", "-h"]