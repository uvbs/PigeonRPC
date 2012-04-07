#PigeonRPC 

###这是什么？

PigeonRPC这是一个简单的基于XMPP信道的python rpc框架, 目标完全不是象传统的RPC框架那样追求高并发，低延迟和跨平台，且能传输的信息量也不多，唯一的目标是是简单易用并且能通过XMPP服务器曲线实现内网穿透 :)

###能做什么？

目前只支持Python, 这个框架是[我](http://c4pt0r.github.com/about.html)的一个用来远程控制家中电脑的蛋疼项目的一部分，基于BSD licence开源，借用XMPP服务实现内网穿透，也就是在双方在任何网络环境下都能互相通信。例如很多geek都碰到的情况：在上班的时候，突然想让家中的电脑下载个啥东西或者干点什么事情浪费一下家中的带宽，但是家中的电脑在自家的路由后边，又是动态ip，所以无法直接连接；对于这种情况，可以在家中电脑用PigeonRPC搭个服务，然后就可以在任何地方进行rpc调用了, 你只需要为它申请一个Google Account (使用gtalk服务的话)

###Architecture

![Icon](http://c4pt0r.github.com/images/peieonRPC.png)


###How To Use

创建一个echo服务, 然后将这个对象绑到XMPPServer服务上, XmppRPCServer的构造函数第一个参数是gtalk id, 第二个是密码, 第三个是一个object，用于提供rpc服务.
*sample_server.py*

{% highlight python %}
from xmpprpc import *

class RPCObject:
    def echo(self, *args):
        ret = ''
        for i in args:
            ret += i + ' '
        return ret

if __name__ == '__main__':
    rpcObj = RPCObject()
    srv = XmppRPCServer('c4pt0r.bot1@gmail.com', 'password.secret', rpcObj )
    srv.listen()

{% endhighlight %}


*sample_client.py*
{% highlight python %}

from xmpprpc import *

if __name__ =='__main__':
    client = XmppRPCClient('c4pt0r.bot2@gmail.com','secret.password', 'c4pt0r.bot1@gmail.com') # 第三个参数是rpc服务的gtalk id
    remote_obj = client.getRemoteObj() # 从远程服务器拿到obj
    # `echo` was defined in ./sample_srv.py
    print remote_obj.echo('hello','world!')
    print remote_obj.echo('hello world')
    client.stop() #需要在结束之前调用下，让bot下线

{% endhighlight %}

###Source

	git clone …


PigeonRPC依赖pydns和xmpppy

	sudo easy_install pydns
	sudo easy_install xmpppy

###Enjoy it!