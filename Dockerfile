FROM fiscoorg/playground:python_sdk

WORKDIR /python-sdk
RUN apk add --no-cache tzdata && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN pip install flask==2.2.5 gunicorn==23.0.0 -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir

COPY . /python-sdk
RUN mv python-fisco-console/* /python-sdk

EXPOSE 20200 30300 8545 5555

CMD ["bash", "run.sh"]
