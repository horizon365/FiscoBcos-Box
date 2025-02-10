# FiscoBcos-Box
FiscoBcos 的区块链盒子，包含 WEB 查看页面， 以及 restFul API

### 简介
基于FiscoBcos python-sdk 开发的区块链浏览器，自带 restFul API 接口，无须 Java、MySQL
```
https://github.com/FISCO-BCOS/fisco-bcos-browser.git
```


#### 项目效果
首页

![首页截图](https://github.com/horizon365/FiscoBcos-Box/blob/master/index.png)

交易详情

![首页截图](https://github.com/horizon365/FiscoBcos-Box/blob/master/transaction_detail.png)



### 使用 docker 快速运行

```shell
docker run -p 5555:5555 -d --mount type=volume,source=fisco,target=/root/fisco shujuliuer/fisco_box
```

主页访问地址: http://ip:5555/index.html

通过 API 接口上链一条数据
```shell
curl --location 'http://127.0.0.1:5555/sendTrans/rawTrans' \
--header 'Content-Type: application/json' \
--data '{"data": "cross the world"}'
```


### 区块链浏览器的api详解：

1. 浏览器可配合python-sdk配置的区块链查看三个主要模块：首页概览、区块列表、交易列表。
2. api分为flask版和tornado版，实现功能基本相同。
3. api启动自动部署合约，获取合约地址，合约地址在交易上链的时候需要用到。（可获取一次合约后存入缓存，之后启动查询缓存）
4. 如果只使用浏览器的查询，不需要部署合约，也无需合约地址。
5. 每次部署合约都会生成一个区块，区块内包含一个交易。


### API 接口：

>GET 查询api：

/query_info/index  获取主页的数据，包括预览，交易量图，最近的区块和交易

/query_info/block_list  获取区块列表，根据区块高度或者区块哈希搜索或者根据页数取10个区块列表

/query_info/transaction_list  获取交易列表，根据区块高度或者交易哈希搜索或者根据页数取10个交易列表

/query_info/block_detail   根据区块哈希，获取区块的详情

/query_info/transaction_detail   根据交易哈希，获取交易详情和交易回执

>POST 上传交易api：

/sendTrans/rawTrans   上传json格式数据，发送交易上链 


### 开发原理

1. 安装Fisco Bcos的python-sdk，python-sdk配置规则参照官方教程；

2. 将python-fisco-consle下面的所有文件与文件夹一并复制放入python-sdk根目录。其中包括static静态页面目录，以及flask和tornado 的启动文件；

3. 启动fisco_browser_flask.py 或 fisco_browser_tornado.py 则分别启动flask/tornado 的工程；
