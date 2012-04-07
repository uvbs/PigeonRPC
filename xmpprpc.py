#encoding=utf-8
import os
import sys
import xmpp
import json
import threading
import Queue
import time
import inspect

# command names
CMD_LS = 'ls'
CMD_CALL = 'call'

## tricky, get function name list from a object
def getObjFuncs(obj):
    ret = []
    lst = dir(obj)
    for _attr_ in lst:
        try:
            if inspect.ismethod(getattr(obj, str(_attr_))):
                ret.append(str(_attr_))
        except:
            continue
    return ret
    
## a xmpp bot implement
class XmppBot:
    JID = ''
    PASSWORD = ''
    client = None
    def __init__ (self, jid, password):
        self.JID = xmpp.JID(jid)
        self.PASSWORD = password
        self.login()
        
    def login (self):         
        self.client = xmpp.Client(self.JID.getDomain(), debug=[])
        if self.client.connect() == '':
            raise 'bot not connected.'
        if self.client.auth(self.JID.getNode(), self.PASSWORD) == None:
            raise 'bot authentication failed.'
        self.client.RegisterHandler('message', self.message_callback)
        self.client.RegisterHandler('presence', self.presence_callback)
        self.client.sendInitPresence()
        
    def message_callback (self, client, message):
        pass
        
    def presence_callback (self, client, message):
        type = message.getType()
        who = message.getFrom().getStripped()
        if type == 'subscribe':
            self.subscribe(who)
        elif type == 'unsubscribe':
            self.unsubscribe(who)
        
    def subscribe (self, jid):
        self.client.send(xmpp.Presence(to=jid, typ='subscribed'))
        self.client.send(xmpp.Presence(to=jid, typ='subscribe'))
    
    def unsubscribe (self, jid):
        self.client.send(xmpp.Presence(to=jid, typ='unsubscribe'))
        self.client.send(xmpp.Presence(to=jid, typ='unsubscribed'))
    
    def send (self, jid, message):
        self.client.send(xmpp.protocol.Message(jid, message))
    
    def step (self):
        try:
            self.client.Process(1)
        except KeyboardInterrupt: 
            return False
        return True

class XmppRPCServer(XmppBot):
    def __init__(self, jid, password, controller):
        XmppBot.__init__(self, jid, password)
        self.controller_obj = controller
    
    def message_callback (self, client, msg):
        fromid = msg.getFrom().getStripped()
        cont = msg.getBody()
        try:
            cmd = json.loads(cont)
            ret = {'cmd':'ret'}
            if cmd['cmd'] == CMD_LS:
                ret['code'] = 0
                ret['ret'] = getObjFuncs(self.controller_obj)
                
            elif cmd['cmd'] == CMD_CALL:
                func = cmd['func']
                param = cmd['param']
                ret['code'] = 0
                ret['ret'] = getattr(self.controller_obj, func)(*param)
            self.send(fromid, json.dumps(ret))
        except:
            self.send(fromid, json.dumps({'code':-1, 'cmd':'ret', 'ret':'unknown error'}))
            pass
        
    def listen(self):
        while (self.step()): pass
    
class XmppRPCClient(XmppBot):
    def __init__(self, jid, password, srvjid ):
        XmppBot.__init__(self, jid, password)
        # subscribe other side
        self.client.send(xmpp.Presence(to=srvjid, typ='subscribe'))    
        self._srv_jid = srvjid
        # start message loop
        self._t = threading.Thread(target = self.__thread_func__, args = ())
        self._q = Queue.Queue()
        self._running = True
        self._t.start()
        
    def __thread_func__(self):
        while (self.step() and self._running == True):
            try:
                msg = self._q.get_nowait()
                self.send(self._srv_jid, json.dumps(msg))
            except Queue.Empty:
                pass
    
    def message_callback(self, client, msg):
        fromid = msg.getFrom().getStripped()
        cont = msg.getBody()
        cmd = json.loads(cont)
        if cmd['cmd'] == 'ret':
            self._ret_queue.put(cmd.get('ret', {}))
    
    def getMethods(self):
        self._ret_queue = Queue.Queue()
        self._q.put({'cmd': CMD_LS})
        ret = self._ret_queue.get()
        return ret
    
    def getRemoteObj(self):
        ret = XmppRemoteObject(self)
        return ret
    
    def stop(self):
        self._running = False

    def remoteCall(self, func, params):
        self._ret_queue = Queue.Queue()
        self._q.put({'cmd': CMD_CALL, 'func':func, 'param':params })
        ret = self._ret_queue.get()
        return ret

# remote object
class XmppRemoteObject:
    def __init__(self, client):
        self._client = client
        self._methods = client.getMethods()
        
        # gen lambda list
        lambs = [(lambda x: 
                      lambda *param: self.dispatch(x, *param))(method_name) 
                  for method_name in self._methods]
        
        for i in range(0, len(self._methods)):
            setattr(self, self._methods[i], lambs[i])

    def dispatch(self, func, *param):
        return self._client.remoteCall(func, param)
