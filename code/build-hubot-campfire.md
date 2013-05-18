部署Hubut到Heroku上
==================

[Deploying Hubot onto Heroku](https://github.com/github/hubot/wiki/Deploying-Hubot-onto-Heroku) 已经清楚地讲了，
所以我这里不叫`How-to`，而是讲下我这个菜鸟当初在搭建时遇到了哪些问题。

##  Hubot、Heroku 和 Campfire 如何一起工作的

我搞了三天晚上都搞到凌晨，最后终于搞好了。之所以花了这么长的时间是由于我不知道三者是如何工作在一起的。

    Hubut       是我们的机器人
    Heroku      给我们提供了web环境
    Campfire    一个聊天软件，提供了对外的API

通过 Campfire 的 API，Hubot 作为一个会议成员加入到 Campfire 的聊天室中，当聊天室里的实际用户发送 `hubut help` 类似的 hubut 命令时，
Hubut就会自动地把结果推送到 Campfire 的聊天室里。

## 部署 Hubot 到 Heroku 时，git push 始终失败

这个问题把我小命都搞掉了，还在后来发现了[git clone fails for Heroku project](http://stackoverflow.com/questions/7305673/git-clone-fails-for-heroku-project)，才把问题解决了。

原来还是由于 ssh key 造成的，对 SSH 不了解（TODO）。

## 对于使用 Free Heroku 的用户需要注意

千万别忘了加 HEROHU_URL 变量
