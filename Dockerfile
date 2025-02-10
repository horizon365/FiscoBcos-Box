FROM fiscoorg/playground:python_sdk

WORKDIR /python-sdk

RUN pip install flask==2.2.5 -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir

COPY . /python-sdk
RUN mv python-fisco-console/* /python-sdk

EXPOSE 20200 30300 8545 5555

CMD ["bash", "run.sh"]