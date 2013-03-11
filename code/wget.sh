# 由于公司上网要通过proxy, 而安装eclipse插件时我有不会配置http_proxy,
# 于是, 用 wget 取下apache的目录下的所有文件, 在开启python的SimpleHttpServer
wget -m -np http://download.fr.forge.objectweb.org/eclipse-update/
