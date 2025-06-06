FROM python:3.9-slim
RUN mkdir /app
COPY ./* /app/
WORKDIR /app
RUN echo "deb https://mirrors.tencent.com/debian/ bookworm main non-free non-free-firmware contrib" > /etc/apt/sources.list

RUN echo "deb https://mirrors.tencent.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list
RUN echo "deb https://mirrors.tencent.com/debian/ bookworm-updates main non-free non-free-firmware contrib" >> /etc/apt/sources.list
RUN echo "deb https://mirrors.tencent.com/debian/ bookworm-backports main non-free non-free-firmware contrib" >> /etc/apt/sources.list
RUN rm /etc/apt/sources.list.d/*

RUN apt-get update && apt-get install -y cron \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/* \
RUN python ./setup.py install

CMD ["tellyget", "-h"]