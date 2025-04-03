Nginx 配置：  
```nginx configuration
location /fisco/api/ {
proxy_pass http://127.0.0.1:9518/;
more_clear_headers 'Cache-Control';
more_set_headers 'Cache-Control: no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0';
}

```


# 手动打包docker
```shell
docker build --platform linux/amd64 -t harbor.cngb.org/cngbdb/fisco_box .
```
# 运行docker
```shell
docker run -p 9518:5555 -d --mount type=volume,source=fisco,target=/root/fisco --label io.portainer.accesscontrol.teams=cngbdb --name fisco harbor.cngb.org/cngbdb/fisco_box
```
# 修改js中的硬地址,用来匹配nginx代理配置
```shell
docker exec -it fisco sed -i 's/url: "/url: "\/fisco\/api/g' /python-sdk/static/js/*.js
```


