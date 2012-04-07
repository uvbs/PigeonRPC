#encoding=utf-8
from xmpprpc import *

if __name__ =='__main__':
    client = XmppRPCClient('c4pt0r.bot2@gmail.com','c4pt0r.bot2', 'c4pt0r.bot1@gmail.com')
    remote_obj = client.getRemoteObj()
    # `echo` was defined in ./sample_srv.py
    print remote_obj.echo('hello','world!')
    print remote_obj.echo('hello world')
    client.stop()