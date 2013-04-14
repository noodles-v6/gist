关于Java Exception的好实践
===========================

## Checked or Unchecked Exception

[Unchecked Exceptions -- The Controversy](http://docs.oracle.com/javase/tutorial/essential/exceptions/runtime.html)

传统的SUN建议用户使用Checked Exception, 除非自己是JVM, 才使用Unchecked. Effective Java 的作者原本也是这样认为的，可通过很多在大型项目后，他们甚至提出了完全的Unchecked Exception, 这种极端的建议。C#中异常都是Unchecked。

所以，Checked or Unchecked 还要自己在项目中好好体会，所谓有些东西是经验，不是能用定理规定死的。

## finally 里关闭或释放资源

虽然在Java 7中有 automatic resource management or ARM blocks, 但好的实践还是要记住，网络或IO处理都应该记得 close or release resource.

## catch 里处理异常信息时要带上相关的数据

message 1: "Incorrect argument for method"
message 2: "Illegal value for ${argument}: ${value}

## Converting Checked Exception into RuntimeException (??)

## 异常捕获是很昂贵的

## 参考

[10 Exception handing Best Practies in Java](http://javarevisited.blogspot.com/2013/03/0-exception-handling-best-practices-in-Java-Programming.html)

[检查型异常和非检查型异常 from CSDN](http://blog.csdn.net/always_my_fault/article/details/2113918)
