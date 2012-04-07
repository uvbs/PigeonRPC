from xmpprpc import *

class RPCObject:
    def echo(self, *args):
        ret = ''
        for i in args:
            ret += i + ' '
        return ret

if __name__ == '__main__':
    rpcObj = RPCObject()
    srv = XmppRPCServer('c4pt0r.bot1@gmail.com', 'c4pt0r.bot1', rpcObj )
    srv.listen()