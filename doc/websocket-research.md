#WebSocket调研报告

## 1 背景

TODO 介绍我们的业务场景

## 2 为什么不是HTTP

HTTP协议经过多年的使用，发现了一些不足，主要是性能方面的，包括：

* HTTP的连接问题，HTTP客户端和服务器之间的交互是采用请求/应答模式，在客户端请求时，会建立一个HTTP连接，然后发送请求消息，服务端给出应答消息，然后连接就关闭了。到HTTP1.1，开始支持持久连接。

	- 因为TCP连接的建立过程是有开销的，如果使用了SSL/TLS开销就更大。
	
	- 在浏览器里，一个网页包含许多资源，包括HTML，CSS，JavaScript，图片等等，这样在加载一个网页时要同时打开连接到同一服务器的多个连接。
	
* HTTP通信方式问题，HTTP是半双工传输的（half-duplex），请求/应答方式的会话都是客户端发起的，缺乏服务器通知客户端的机制，在需要通知的场景，如聊天室，游戏，客户端应用需要不断地轮询服务器。

	- Polling(Ajax) 短轮询
	
	![](/Users/Noodles/GoogleDisk/polling.png)
	
	- Long polling(Comet) 长轮询
	
	![](/Users/Noodles/GoogleDisk/long-polling.png)

* HTTP消息头问题，现在的客户端会发送大量的HTTP消息头。大量请求就会有相当大的消息头的数据量。
	
	分析下HTTP请求/响应的开销：

		GET / HTTP/1.1
		Host: localhost:9000
		User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0
		Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
		Accept-Language: zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3
		Accept-Encoding: gzip, deflate
		Connection: keep-alive
		Cache-Control: max-age=0
		HTTP/1.1 200 OK
		Date: Sun, 04 Aug 2013 14:00:45 GMT
		Content-Length: 9
		Content-Type: text/html;charset=utf-8
		Server: CherryPy/3.2.2

	一次请求头和响应头总共耗去464个字节，那么：

	1. 如果每60秒10000个客户端polling，那么网络吞吐量为 (464*10000)/60 = 77334 bytes = 618667 bits/s = 0.6 Mbps
	2. 如果每秒10000个客户端polling，那么网络吞吐量为 (464*10000)/1 = 4640000 bytes = 37120000 bits/s = 36.25 Mbps
	
	
## 3 WebSocket协议调研

### 3.1 介绍

WebSocket是W3C/IETF标准，是全双工传输（full-duplex）。目前（2013-08-04），WebSocket协议的最新草案为[rfc6455](http://tools.ietf.org/html/rfc6455)。它不是一个raw TCP socket。

引用协议标准：

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

### 3.2 WebSocket协议细节

本调研报告没有特别起一个章节介绍协议的基础内容（可以直接阅读协议文档）。我们的调研是根据业务中我们比较关心的问题进行的，其中会牵扯到相关的协议细节。

我们关心：

* 是否能减少网络交换；
* 数据传输是否安全；
* 网络闪断情况下的客户端与服务端的反应；
* 网络故障情况下传输数据的完整性是否能够保证;
* 数据是否能够支持分片传输；

#### 3.2.1 是否能减少网络交换

TOTO 引用相关文献

WebSocket的每个message frame只会消耗 2 bytes，没有polling带来的消耗（只需要发送message，没有HTTP那么多的头消息）。

对比下上面的HTTP polling方式，简单地计算下网络吞吐量：

1. 如果每60秒10000个frames，那么网络吞吐量为 (2*10000)/60 = 333 bytes = 2664 bits/s = 2.6 Kbps （而HTTP polling要0.6 Mbps）
2. 如果每秒10000个客户端polling，那么网络吞吐量为 (2*10000)/1 = 20000 bytes = 160000 bits/s = 156 Kbps（而HTTP polling要36.25 Mbps）

#### 3.2.2 数据传输是否安全

WebSocket是运行在80/443端口上的，能友好地使用代理和防火墙。

- HTTP兼容的握手；
- 集成基于Cookie的认证；
- 加密传输的WebSockets（wss://host:port/）

#### 3.2.3 网络闪断情况下的客户端与服务端的反应

引用协议标准：

>**1.7.  Relationship to TCP and HTTP**

> _This section is non-normative._

>The WebSocket Protocol is an independent TCP-based protocol.  Its
only relationship to HTTP is that its handshake is interpreted by
HTTP servers as an Upgrade request.

>By default, the WebSocket Protocol uses port 80 for regular WebSocket
connections and port 443 for WebSocket connections tunneled over
Transport Layer Security (TLS) [RFC2818].

WebSocket在握手阶段是走HTTP协议的，故在握手时出现网络故障，连接是不能被建立的，两端都会报错。在连接建立后，如果出现网络闪断的情况，**根据协议实现**，两端是不会有异常抛出的。为什么要强调**根据协议实现**？因为WebSocket连接后，它是一个纯粹的TCP连接，而对于一个TCP连接，就算断网，连接依旧是建立。特别地，如果系统设置了TCP keepalive，那么长时间（可以配置，但必须大于2小时）双方没有通讯，那么双方会发探帧去检测连接状态，这时就有可能关闭连接（一般地，客户端的keepalive是不开的，而服务端可以根据需要开启），更多内容请查看TCP相关知识。

如果应用需要实时知道连接的状态，那么就需要应用实现检测。协议里已经添加了类似供暖的说明（但未在API中暴露出来）：

引用协议标准：

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

协议中提到，`Control frames`被使用于通讯WebSocket连接的状态。

注意：Ping/Pong还没有从`WebSocket API`中暴露出来。

引用[API说明](http://www.w3.org/TR/websockets/)：

>6 Ping and Pong frames

>The WebSocket protocol specification defines Ping and Pong frames that can be used for keep-alive, heart-beats, network status probing, latency instrumentation, and so forth. These are not currently exposed in the API.

>User agents may send ping and unsolicited pong frames as desired, for example in an attempt to maintain local network NAT mappings, to detect failed connections, or to display latency metrics to the user. User agents must not use pings or unsolicited pongs to aid the server; it is assumed that servers will solicit pongs whenever appropriate for the server's needs.

下面有段来自[Ping/Pong frames被添加到API里但为暴露里的讨论过程](https://www.w3.org/Bugs/Public/show_bug.cgi?id=13104)：

引用讨论：

>Take into account that current WS Ping/Pong is just valid as a keep-alive but not as a heart-beat mechanism (see comment above in which is explained that a WS Pong could be received much later due to an existing long WS message being already carried from).

讨论里指出，Ping/Pong是作为keep-alive，而不是心跳检测，比如，Ping/Pong可能被比较繁重处理导致Pong延迟。

#### 3.2.4 网络故障情况下传输数据的完整性是否能够保证

可以的。因为TCP传输是可靠的，具体查看TCP相关文献。

#### 3.2.5 数据是否能够支持分片传输

是可以支持的。

引用协议标准：

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
   
## 4 WebSocket API调研

### 4.1 介绍

WebSocket API是一套定义好的接口，最新规范[见这里](http://www.w3.org/TR/websockets/)。

引用API标准:

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

* url
* ready state
* networking 
	- 连接建立触发onopen
	- 协议不匹配，帧解析错误等会触发onerror
	- 关闭连接触发onclose

* messaging 
	- 可以发送文本，二进制，大数据可以fragmented后发送。

### 4.2 现有的实现

Java语言的实现[看这里](https://java.net/projects/websocket-spec/pages/WebSocketAPIs)，有Java-WebSocket, Jetty-websocket等；Python语言的实现有 [WebSocket-for-Python](https://github.com/Lawouach/WebSocket-for-Python)，[django-websocket](https://pypi.python.org/pypi/django-websocket)，[tornado websocket](https://github.com/facebook/tornado/blob/master/tornado/websocket.py) 等。

根据我们的业务特征，对一些现有的实现做了简单的调研（我们主要做了Java,IOS的WebSocket客户端实现和Python的服务端实现）：

1. 网络正常情况下
	
	- WebSocket的双向通讯可以正常工作；
	
	- 使用WebSocket-for-Python开发的客户端和服务端，数据分包发送是可以的；
	
	- 无论是否采用分包发送，发送的文件过大时，服务器端内存都会吃的很厉害（因为在文件整个完成发送前，服务端都是把接收到的数据保存在内存里的）。
	
	- 分包发送的主要目的是（协议里已经指出）
		
		* 可以让客户端不用buffer消息。
		
		* 多路复用。

2. 网络异常情况下

 	 - Java-WebSocket客户端在网络异常的时候，不会报错，即onerror不会被触发，网络恢复后消息仍然可以被发出；

	 - Jetty的客户端在网络异常时5min时提示网络异常，无论这5min内是否有send数据给服务端（其中，5min是Jetty的默认设置），5min内恢复网络消息仍然可以被发出；

	 - iOS WebSocket API 实现，采用 [SocketRocket](https://github.com/square/SocketRocket)，SocketRocket 底层采用 NSStream 来与 Server 通讯。
	 以下情况将调用 onerror：
	 	
		* Http handshake, response code >= 400, 抛出“received bad response code from server”。
	 	* 效验 secKey 失败，抛出“Invalid Sec-WebSocket-Accept response”。
	 	* 效验 HTTP Header 失败，抛出“Server specified Sec-WebSocket-Protocol that wasn't requested”。
	 	* NSOutoutStream write 数据时返回 -1，抛出“Error writing to stream”。
	 	* NSStreamEventErrorOccurred 事件。
	 	* NSStreamEventEndEncountered 事件，如果 streamError 不为 nil。
	 	* NSInputStream bytes_read 小于 0。
	 	* wws 协议时，服务器证书无效，抛出“Invalid server cert”。
	 	
		备注：事件 onerror 触发后，不会触发 onclose。
	 
3. TODO 服务端性能调研

4. 目前Java-WebSoceket的wss很薄弱。TODO 测试安全。

## 5 附件

### 5.1 参考文献

### 5.2 调研 Demo