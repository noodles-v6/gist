在Linux下安装Windows字体
=========================

## 安装

把XP下的字体C:\WINDOWS\FONTS\simsun.ttc（也就是宋体,大小为10M），把他重命名为 simsun.ttf

拷贝simsun.ttf 字体到 /usr/share/fonts/zh_CN/TrueType/ 下来

在linux命令行下执行：fc-cache /usr/share/fonts/zh_CN/TrueType/

完成.

## 查看

使用 fc-list 参看linux下安装的所有字体. http://linux.die.net/man/1/fc-list
