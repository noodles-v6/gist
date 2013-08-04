#WebSocket调研报告

*目前（2013-08-04），WebSocket协议的最新草案为[rfc6455](http://tools.ietf.org/html/rfc6455)，WebSocket API的最新规范[见这里](http://www.w3.org/TR/websockets/)。
标准是最具权威的报告，在这份调研报告中，我们将会多次引用标准里的段落。*

## 背景

TODO 介绍我们的业务场景

## 为什么不是HTTP

HTTP协议经过多年的使用，发现了一些不足，主要是性能方面的，包括：

* HTTP的连接问题，HTTP客户端和服务器之间的交互是采用请求/应答模式，在客户端请求时，会建立一个HTTP连接，然后发送请求消息，服务端给出应答消息，然后连接就关闭了。（后来的HTTP1.1支持持久连接）

	- 因为TCP连接的建立过程是有开销的，如果使用了SSL/TLS开销就更大。
	
	- 在浏览器里，一个网页包含许多资源，包括HTML，CSS，JavaScript，图片等等，这样在加载一个网页时要同时打开连接到同一服务器的多个连接。
	
* HTTP消息头问题，现在的客户端会发送大量的HTTP消息头，由于一个网页可能需要50-100个请求，就会有相当大的消息头的数据量。

* HTTP通信方式问题，HTTP的请求/应答方式的会话都是客户端发起的，缺乏服务器通知客户端的机制，在需要通知的场景，如聊天室，游戏，客户端应用需要不断地轮询服务器。

## WebSocket协议调研

### 介绍

引用标准：

>The WebSocket Protocol enables two-way communication between a client
running untrusted code in a controlled environment to a remote host
that has opted-in to communications from that code.  The security
model used for this is the origin-based security model commonly used
by web browsers.  The protocol consists of an opening handshake
followed by basic message framing, layered over TCP.  The goal of
this technology is to provide a mechanism for browser-based
applications that need two-way communication with servers that does
not rely on opening multiple HTTP connections.

WebSocket提供使用一个TCP连接进行双向通讯的机制，包括网络协议和API，取代网页和服务端采用HTTP轮询进行双向通讯的机制。由于WebSocket并不依赖于浏览器（浏览器只是实现了WebSocket协议），于是我们可以使用他到任何需要双向通讯的场景中。

### 一些WebSocket协议细节

这里主要是根据业务特性做的相关协议细节的调研。包括：

* 网络闪断情况下的客户端与服务端的反应；

* 网络故障情况下传输数据的完整性是否能够保证；

* 数据是否能够支持分片传输；

#### 网络闪断情况下的客户端与服务端的反应

引用标准：

>**1.7.  Relationship to TCP and HTTP**

> _This section is non-normative._

>The WebSocket Protocol is an independent TCP-based protocol.  Its
only relationship to HTTP is that its handshake is interpreted by
HTTP servers as an Upgrade request.

>By default, the WebSocket Protocol uses port 80 for regular WebSocket
connections and port 443 for WebSocket connections tunneled over
Transport Layer Security (TLS) [RFC2818].

WebSocket在握手阶段是走HTTP协议的，故在握手时出现网络故障，连接是不能被建立的，两端都会报错。在连接建立后，如果出现网络闪断的情况，**根据协议实现**，两端是不会有异常抛出的。为什么要强调**根据协议实现**？因为WebSocket连接后，它是一个纯粹的TCP连接，而对于一个TCP连接，就算断网，两端还是认为连接是保持的，特别的，如果系统设置了TCP keepalive，那么长时间（可以配置，但必须大于2小时）双方没有通讯，那么双方会发探帧去检测连接状态，这时就有可能关闭连接（一般地，客户端的keepalive是不开的，而服务端可以根据需要开启），更多内容请查看TCP相关知识。

如果应用需要实时知道连接的状态，那么就需要应用实现检测。不过最新的协议已经添加了类似的功能：

引用标准：

>**5.5.  Control Frames**

>Control frames are identified by opcodes where the most significant
bit of the opcode is 1.  Currently defined opcodes for control frames
include 0x8 (Close), 0x9 (Ping), and 0xA (Pong).  Opcodes 0xB-0xF are
reserved for further control frames yet to be defined.

>Control frames are used to communicate state about the WebSocket.
Control frames can be interjected in the middle of a fragmented
message.

>All control frames MUST have a payload length of 125 bytes or less
and MUST NOT be fragmented.

标准中提到，`Control frames`被使用于通讯WebSocket连接的状态。注意，Close, Ping, Pong的出现只是给应用（指实现WebSocket的库）提供了实现连接状态检测的方法，还是要应用自己去决定如何检测的，并且要注意Control frames不是单纯的用于状态检测。下面是来自[Ping/Pong frames被添加到标准里的过程](https://www.w3.org/Bugs/Public/show_bug.cgi?id=13104)：

引用讨论：

>Take into account that current WS Ping/Pong is just valid as a keep-alive but not as a heart-beat mechanism (see comment above in which is explained that a WS Pong could be received much later due to an existing long WS message being already carried from).

讨论里指出，Ping/Pong是作为keep-alive，而不是心跳检测，举个例子：Ping/Pong可能被比较繁重处理导致Pong延迟，见图：

![alt text](https://github.com/noodles-v6/gist/blob/master/image/websocket-1-pingpong.png "Ping/Pong延迟图")

这里仅仅是个例子，举它的目的是为了说明，要实现心跳这样的操作，要应用自己用Ping/Pong实现。

#### 网络故障情况下传输数据的完整性是否能够保证

答案是可以的，因为TCP传输是可靠的。

#### 数据是否能够支持分片传输

引用标准：

>
**5.4.  Fragmentation**

>   The primary purpose of fragmentation is to allow sending a message
   that is of unknown size when the message is started without having to
   buffer that message.  If messages couldn't be fragmented, then an
   endpoint would have to buffer the entire message so its length could
   be counted before the first byte is sent.  With fragmentation, a
   server or intermediary may choose a reasonable size buffer and, when
   the buffer is full, write a fragment to the network.

>   A secondary use-case for fragmentation is for multiplexing, where it
   is not desirable for a large message on one logical channel to
   monopolize the output channel, so the multiplexing needs to be free
   to split the message into smaller fragments to better share the
   output channel.  (Note that the multiplexing extension is not
   described in this document.)

>   Unless specified otherwise by an extension, frames have no semantic
   meaning.  An intermediary might coalesce and/or split frames, if no
   extensions were negotiated by the client and the server or if some
   extensions were negotiated, but the intermediary understood all the
   extensions negotiated and knows how to coalesce and/or split frames
   in the presence of these extensions.  One implication of this is that
   in absence of extensions, senders and receivers must not depend on
   the presence of specific frame boundaries.

>   The following rules apply to fragmentation:

>   ...

协议中有专门的一节是讲 Framgementation 的，其中 ... 的部分是具体规则，具体请查看标准。

特别指出，Control Frames能够插入到消息的多个分帧的中间。

引用标准：

> Control frames are used to communicate state about the WebSocket.
   Control frames can be interjected in the middle of a fragmented
   message.
   
>If an endpoint receives a Close frame and did not previously send a
   Close frame, the endpoint MUST send a Close frame in response.  (When
   sending a Close frame in response, the endpoint typically echos the
   status code it received.)  It SHOULD do so as soon as practical.  An
   endpoint MAY delay sending a Close frame until its current message is
   sent (for instance, if the majority of a fragmented message is
   already sent, an endpoint MAY send the remaining fragments before
   sending a Close frame).  However, there is no guarantee that the
   endpoint that has already sent a Close frame will continue to process
   data.
   
## WebSocket API调研

### 介绍

WebSocket API规范，主要是定义了一套接口。

引用规范:

	[Constructor(DOMString url, optional (DOMString or DOMString[]) protocols)]
	interface WebSocket : EventTarget {
	  readonly attribute DOMString url;

	  // ready state
	  const unsigned short CONNECTING = 0;
	  const unsigned short OPEN = 1;
	  const unsigned short CLOSING = 2;
	  const unsigned short CLOSED = 3;
	  readonly attribute unsigned short readyState;
	  readonly attribute unsigned long bufferedAmount;

	  // networking
	           attribute EventHandler onopen;
	           attribute EventHandler onerror;
	           attribute EventHandler onclose;
	  readonly attribute DOMString extensions;
	  readonly attribute DOMString protocol;
	  void close([Clamp] optional unsigned short code, optional DOMString reason);

	  // messaging
	           attribute EventHandler onmessage;
	           attribute DOMString binaryType;
	  void send(DOMString data);
	  void send(Blob data);
	  void send(ArrayBuffer data);
	  void send(ArrayBufferView data);
	};

接口主要包含了四个部分：

- url
- ready state
- networking
- messaging

其中：

现有的java语言实现，[看这里](https://java.net/projects/websocket-spec/pages/WebSocketAPIs)，有Java-WebSocket, Jetty-websocket等。python语言的实现有，[WebSocket-for-Python](https://github.com/Lawouach/WebSocket-for-Python)，[django-websocket](https://pypi.python.org/pypi/django-websocket)，[tornado websocket](https://github.com/facebook/tornado/blob/master/tornado/websocket.py)

### 一些现有实现调研结果

我们根据业务特征，对一些现有的接口实现做了简单的调研：

1. 网络正常情况下，WebSocket的双向通讯可以正常工作，TODO 数据分片发送需要测试。

2. 网络异常情况下：

	我们主要做了Java,IOS的WebSocket客户端实现和Python的服务端实现，下面调研结果都是基于WebSocket-for-Python编写服务端的：

 	 - Java-WebSocket客户端在网络异常的时候，不会报错；

	 - Jetty的客户端在网络异常时5min时提示网络异常，不管在这5min里是否有send数据给服务端，其中，5min是Jetty的默认设置；

	 - TODO ios端
	 
## 附件

### 参考文献

### 调研 Demo