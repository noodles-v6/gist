#WebSocket调研报告

## 1 业务背景

在 Vobile Sync 产品中，SDK 与 ACR 之间通讯采用 HTTP 1.1 协议。SDK 与 ACR 之间存在多种业务协议。如：init service, init session, start query, submit sample, listen result 等。SDK 需要与 ACR 多次交互才能完成一次查询工作。例如，在一次 Video 模式查询中，SDK 需要如下步骤来完成查询：

1. Start Query，告知 ACR 查询类型，并请求 Request ID。
2. Submit Sample，SDK 每秒向 ACR 提交一张 Base64 编码后的图片。
3. Listen Result，SDK 侦听结果。如果第一次 Listen 无结果，且查询未结束，则再次向 ACR 发起 Listen，直到查询结束或 ACR 返回结果。
	
最优情况下，SDK 的每次查询工作中，至少需要 4 次 HTTP 请求。而根据我们的经验和 QA 的测试报告，实际的 HTTP 请求数在 6 ~ 14 次之间。这还不包括 Session Timeout、Service Busy 等异常场景。

因此，我们希望通过引入 WebSocket 协议，来减少使用 HTTP 交互过程中带来的部分性能损耗，以及达到简化 SDK 和 ACR 业务协议的目的。
	
## 2 WebSocket是什么

### 2.1 介绍

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

WebSocket提供使用一个TCP连接进行双向通讯的机制，包括网络协议和API，取代网页和Server采用HTTP轮询进行双向通讯的机制。由于WebSocket并不依赖于浏览器（浏览器只是实现了WebSocket协议），于是我们可以使用他到任何需要双向通讯的场景中。

### 2.2 WebSocket是如何工作的

WebSocket通信包括需要两个端点：Client和Server，通信包括两个部分：握手和数据传输。

Client和Server的握手是基于HTTP的，看起来像这样：

![](/Users/Noodles/GoogleDisk/websocket-handshake.png)

在request header中会指明一个`Upgrade: websocket`，Server收到请求后会把连接升级为基于TCP的WebSocket连接。一旦连接建立，双方则可以通过一个TCP连接完成数据传输。

并且，W3C起草了`WebSocket API 标准`，最新草案[见这里](http://www.w3.org/TR/websockets/)。

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
	
有了WebSocket API，Client和Server可以通过API的方式完成交互。请看下面的交互图：

![](/Users/Noodles/GoogleDisk/WebSocket_Client_Server_Communication.jpg)

1. Client通过HTTP GET请求Server建立WebSocket连接，Server触发onOpen；
2. Server响应Client，Client收到握手后触发onopen，连接建立成功；
3. Client通过send接口发送数据（文本或二进制）给Server；
4. Server端接收到数据后触发OnMessage处理数据；
5. 同样，Server可以给Client发送数据，Client触发onmessage；
6. 最后Client通过close接口关闭连接，Server收到关闭消息触发onClose；
7. 同样，Server可以通过close接口关闭连接，Client端触发onclose。

## 3 为什么是WebSocket而不是HTTP


### 3.1 HTTP与WebSocket比较

HTTP协议经过多年的使用，发现了一些不足，主要是性能方面的，包括：

* HTTP的连接问题，HTTPClient和Server之间的交互是采用请求/应答模式，在Client请求时，会建立一个HTTP连接，然后发送请求消息，Server给出应答消息，然后连接就关闭了。到HTTP1.1，开始支持持久连接。

	- 因为TCP连接的建立过程是有开销的，如果使用了SSL/TLS开销就更大。
	
	- 在浏览器里，一个网页包含许多资源，包括HTML，CSS，JavaScript，图片等等，这样在加载一个网页时要同时打开连接到同一Server的多个连接。
	
* HTTP通信方式问题，HTTP是半双工传输的（half-duplex），请求/应答方式的会话都是Client发起的，缺乏Server通知Client的机制。

	- Polling(Ajax) 短轮询
	
	![](/Users/Noodles/GoogleDisk/polling.png)
	
	- Long polling(Comet) 长轮询
	
	![](/Users/Noodles/GoogleDisk/long-polling.png)

* HTTP消息头问题，现在的Client会发送大量的HTTP消息头。大量请求就会有相当大的消息头的数据量。
	
然而，WebSocket不像HTTP那样每次传输数据都带上很多的Header：

![](/Users/Noodles/GoogleDisk/websocket.png)


### 3.2 基于业务场景的HTTTP和WebSocket开销比较

#### 假设

假设在Vobile Sync，每次Query需要上传4次媒体文件。

#### 分析
	
1. HTTP请求/响应的开销

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

	一次请求头和响应头总共耗去464个字节，那么，假如现有基于HTTP的一次Query需要10次请求，则：

	100次Query的 overhead = 464 * 10 * 100 = 464000 bytes

2. WebSocket的开销

	WebSocket建立连接后，每个message frame只会消耗 2 bytes，没有polling带来的消耗（只需要发送message，没有HTTP那么多的头消息），则：
	
	100次Query的 overhead = (464 + 2 * 4) * 100 = 1274 bytes
	
#### 结论

比较后很明显地发现HTTP的overhead远高于WebSocket（数量级上的差别），而且还是我们的请求中没有Cookie等信息的情况下。

## 4 我们还关心以下WebSocket特性

* 数据传输是否安全；
* 网络闪断情况下的Client与Server的反应；
* 网络故障情况下传输数据的完整性是否能够保证;

### 4.1 数据传输是否安全

协议标准中明确指出了安全性。

引用协议标准：

>**10  Security Considerations**

>This section describes some security considerations applicable to the
WebSocket Protocol.  Specific security considerations are described
in subsections of this section.

>10.1.  Non-Browser Clients

>10.2.  Origin Considerations

>10.3.  Attacks On Infrastructure (Masking)

>10.4.  Implementation-Specific Limits

>10.5.  WebSocket Client Authentication

>10.6.  Connection Confidentiality and Integrity

>10.7.  Handling of Invalid Data

>10.8.  Use of SHA-1 by the WebSocket Handshake


### 4.2 网络闪断情况下的Client与Server的反应

引用协议标准：

>**1.7.  Relationship to TCP and HTTP**

> _This section is non-normative._

>The WebSocket Protocol is an independent TCP-based protocol.  Its
only relationship to HTTP is that its handshake is interpreted by
HTTP servers as an Upgrade request.

>By default, the WebSocket Protocol uses port 80 for regular WebSocket
connections and port 443 for WebSocket connections tunneled over
Transport Layer Security (TLS) [RFC2818].

WebSocket在握手阶段是走HTTP协议的，故在握手时出现网络故障，连接是不能被建立的，两端都会报错。在连接建立后，如果出现网络闪断的情况，**根据协议实现**，两端是不会有异常抛出的。为什么要强调**根据协议实现**？因为WebSocket连接后，它是一个纯粹的TCP连接，而对于一个TCP连接，就算断网，连接依旧是建立。特别地，如果系统设置了TCP keepalive，那么长时间（可以配置，但必须大于2小时）双方没有通讯，那么双方会发探帧去检测连接状态，这时就有可能关闭连接（一般地，Client的keepalive是不开的，而Server可以根据需要开启），更多内容请查看TCP相关知识。

如果应用需要实时知道连接的状态，那么就需要应用实现检测。协议里已经添加了类似检测的说明（但未在API中暴露出来）：

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

### 4.3 网络故障情况下传输数据的完整性是否能够保证

WebSocket基于TCP的，TCP传输中如果丢包，则会超时重传，故认为WebSocket的传输是可靠的。TCP相关知识可以查看[Wiki](http://en.wikipedia.org/wiki/Transmission_Control_Protocol)。

引用Wiki:

>Reliable transmission
TCP uses a sequence number to identify each byte of data. The sequence number identifies the order of the bytes sent from each computer so that the data can be reconstructed in order, regardless of any fragmentation, disordering, or packet loss that may occur during transmission. For every payload byte transmitted, the sequence number must be incremented. In the first two steps of the 3-way handshake, both computers exchange an initial sequence number (ISN). This number can be arbitrary, and should in fact be unpredictable to defend against TCP sequence prediction attacks.
TCP primarily uses a cumulative acknowledgment scheme, where the receiver sends an acknowledgment signifying that the receiver has received all data preceding the acknowledged sequence number. The sender sets the sequence number field to the sequence number of the first payload byte in the segment's data field, and the receiver sends an acknowledgment specifying the sequence number of the next byte they expect to receive. For example, if a sending computer sends a packet containing four payload bytes with a sequence number field of 100, then the sequence numbers of the four payload bytes are 100, 101, 102 and 103. When this packet arrives at the receiving computer, it would send back an acknowledgment number of 104 since that is the sequence number of the next byte it expects to receive in the next packet.
In addition to cumulative acknowledgments, TCP receivers can also send selective acknowledgments to provide further information.
If the sender infers that data has been lost in the network, it retransmits the data.

并且，做了如下的验证：

1. 建立WebSocket Client与Server连接；

2. Client向Server发送多个40MB文件，在发送的过程中我们不定时的插拔网线多次，以模拟网络闪断；

3. 最终Client收到Server返回的文件收到消息，并且Server收到了完全一样的文件。

结论：网络故障情况下，数据完整性可以保证。

## 5 基于Demo的试验性分析

根据以上的工作，我们调研了现有的Java、Java和Objective-C的API实现。

Java语言的实现[看这里](https://java.net/projects/websocket-spec/pages/WebSocketAPIs)，有Java-WebSocket, Jetty-websocket等；
Python语言的实现有 [WebSocket-for-Python](https://github.com/Lawouach/WebSocket-for-Python)，[django-websocket](https://pypi.python.org/pypi/django-websocket)，[tornado websocket](https://github.com/facebook/tornado/blob/master/tornado/websocket.py) 等；
Objective-C的实现有[SocketRocket](https://github.com/square/SocketRocket)等。

我们选用了WebSocket-for-Python实现的Server，Java-WebSocket和SocketRocket实现的Client，开发了两个Demo：

* 基于文本传输的EchoServer

* 基于二进制传输的文件上传Demo

并测试了在网络正常、网络闪断和网络故障三种情况下的Demo Client & Server的反应和文件上传Demo的服务器压力，得到以下现象与结论。

1. 网络正常情况下，Echo Server & Client 可以很好地完成文本消息的请求应答；文件上传可以正常地从Client机器上传至Server机器。
	
	
2. 网络闪断情况（人为插拔网线模拟）下：

 	- 采用Java-WebSocket和Jetty实现的EchoClient不会报错，网络恢复后消息仍然可以被发出(包括故障期间发送的文本)；
	 
	- 采用[SocketRocket](https://github.com/square/SocketRocket)实现的Client，网络断开，Client会立刻报错。
	
	 	SocketRocket 底层采用 NSStream 来与 Server 通讯。
	 	以下情况将调用 onerror：
	 	
		* Http handshake, response code >= 400, 抛出“received bad response code from server”。
	 	* 效验 secKey 失败，抛出“Invalid Sec-WebSocket-Accept response”。
	 	* 效验 HTTP Header 失败，抛出“Server specified Sec-WebSocket-Protocol that wasn't requested”。
	 	* NSOutoutStream write 数据时返回 -1，抛出“Error writing to stream”。
	 	* NSStreamEventErrorOccurred 事件。
	 	* NSStreamEventEndEncountered 事件，如果 streamError 不为 nil。
	 	* NSInputStream bytes_read 小于 0。
	 	* wws 协议时，Server证书无效，抛出“Invalid server cert”。
	 	
		备注：事件 onerror 触发后，不会触发 onclose。
		
3. 网络故障情况（连接建立后断开网络）下：

	- 采用Java-WebSocket实现的Client一直不会报错（其内部没有监测网络连接的功能），而采用Jetty实现的则会在5min（默认配置）时报TimeoutException，即Jetty的实现是有连接检测的；
	
	- 采用SocketRocket实现的Client，网络断开，Client会立刻报错。
	 
3. 文件上传Demo性能调研

	Demo的功能： Client不断地把本地的2MB文件发送给Server，Server收到后重新开启一个线程把文件写到本地。

	- 场景一
	
		设置：两台Client机器各建立60个websocket连接，每个连接每隔2秒/5秒/20秒三种情况发送2MB文件给Server，Server启用200个线程的线程池

		现象：文件写入正常，不过Server内存持续增长。

	- 场景二
	
		设置：将场景一中的每2/5/20改为60秒，其他一样
		
		现象：文件写入正常，Server内存增长速度减缓。
		
		推断：WebSocket连接后，消息从Client不断发出，Server的写入文件动作由于受到硬盘读写速度的影响，会找出大量文件数据存在内存中，从而导致内存持续增长。故在实际的场景中，需要权衡Server的处理能力，如果Server处理不过来，可能要友好地通知Server忙等消息。


## 6 结论

WebSocket可以满足Vobile Sync产品的业务场景，并且相比较HTTP，能够减少大量的Overhead，缩短客户端Query时间，而且还可以简化现有的业务协议。

## 7 附件

参考资料

- [http://seals.vobile.cn/trac/vdna/wiki/tvsync1.1/optimizing_sdk1.1](http://seals.vobile.cn/trac/vdna/wiki/tvsync1.1/optimizing_sdk1.1)

- [http://seals.vobile.cn/trac/QA/wiki/vdna/websdk/test_reports/v1.1.4?version=24](http://seals.vobile.cn/trac/QA/wiki/vdna/websdk/test_reports/v1.1.4?version=24)

- [http://seals.vobile.cn/trac/vdna/wiki/tvsync1.0/detaildesigen_sdk1.0](http://seals.vobile.cn/trac/vdna/wiki/tvsync1.0/detaildesigen_sdk1.0)

- [http://seals.vobile.cn/trac/ACR/wiki/2.0/sdk/detaildesign_2.0](http://seals.vobile.cn/trac/ACR/wiki/2.0/sdk/detaildesign_2.0)

- [WebSocket协议的最新草案rfc6455](http://tools.ietf.org/html/rfc6455)；

- [WebSocket API最新规范](http://www.w3.org/TR/websockets/)。

调研 Demo

- Server Demo: ws://192.168.10.62:9000/ws

- Client Demo（略）