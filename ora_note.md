http://hi.baidu.com/blueman/blog/item/64e975f0b0da56aaa50f52b3.html

#查看用户和表空间

sqlplus sys/sys as sysdba;

select * from all_users;

select * from dba_tablespaces;

#服务重启

cd $ORACLE_HOME/bin   #进入到oracle的安装目录

./dbstart           #重启服务器

./lsnrctl start     #重启监听器

#查看数据库实例名

select name from v$database; -- 要在sysdba下， SQL> connect / as sysdba

desc v$database;  -- 这也是很好的查看方式。

#查看表索引

select index_name from user_indexes where table_name='ECONF_RESERVE_JOINCONF_LOG';

使用conn / as sysdba登陆数据库，　然后就可以用alter user sys identified by "newsyspassword"来修改sys的密码了

/oracle/product/10.2.0/db_1/network/admin/listener.ora

# 修改用户密码

sqlplus登录后

    conn / as sysdba;
    alter user sys identified by "sys";
    alter user econf identified by "econf";
