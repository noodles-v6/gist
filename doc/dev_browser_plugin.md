浏览器插件开发
==============

打印插件这是我来佑软后的第一个的任务，这大半个月来基本搞的差不多了，今天就来做个小结。

# IE插件开发

开发工具：VS2010

## MFC ActiveX

我来的时候，IE插件是用`MFC ActiveX`开发的，后来我改用了`ATL Control`，原因是由于要异步调用JS，
而好多网上的例子都是用`ATL`工程的。

略。

## ATL Control

[这里有篇很完整的文章：使用ATL开发ActiveX控件](http://www.cnblogs.com/chinadhf/archive/2010/09/03/1817336.html)。

不过异步调用这块我不是用*事件*来实现的，具体原因：我希望调用方使用如下方式编写代码

    var isRunning = pluginObj.invokeAsyncInterface(params, function(data) {
        alert(data);
    });
    
而基于事件的实现是做不到如此简洁的，因为它还要添加事件。

非事件方式实现的流程是：

    --> [js调用控件接口时传入callback函数] 
    --> [控件获取callback函数的IDispatch指针] 
    --> [启用子线程处理业务逻辑，主线程结束]
    --> [子线程处理完业务后，PostMessage给主线程]
    --> [主线程接受到消息后，使用IDispatch指针回调JS]
    
使用IDispatch指针回调的核心代码为：

    <code>
    </code>
  
# Firefox/Chrome等插件开发

这些浏览器都是使用NPAPI做插件开发的。

NPAPI异步调用JS的主要接口为：NPP_Invoke_Default。

# 注意点

1. 异步调用JS的动作必须在主线程里做。因此不管是IE还是Firefox等，都使用了消息机制，把子线程
处理结果通知给主线程，在回调js。

2. windows下启子线程就是`_beginthreadx/_endthreadex`，不推荐使用`CreateThread`。
