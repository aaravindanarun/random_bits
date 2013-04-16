#!/usr/bin/env python

"""A Tornado example of RPC.

Designed to work with rpc_server.py as found in RabbitMQ Tutorial #6:
http://www.rabbitmq.com/tutorials/tutorial-six-python.html

Some code is borrowed from pika's tornado example.
"""

import platform
import os
import sys
import time
import uuid

import pika
import tornado.ioloop
import tornado.httpserver
import tornado.httputil
import tornado.web
import log_class  
import json
import pdb
from pika.adapters.tornado_connection import TornadoConnection
from routes import Mapper
from pyrabbit.api import Client
import string
import random
## original author of the tornado rpc code
__author__ = 'Brian McFadden'
__email__ = 'brimcfadden+gist.github.com@gmail.com'

##  I modified things sig
HTML_HEADER = '<html><head><title>Tornado/Pika RPC</title></head><body>'
HTML_FOOTER = '</body></html>'
EXCHANGE = 'central'
g_port = 0; 

cl = Client('localhost:55672', 'guest', 'guest')
class MainHandler(tornado.web.RequestHandler):
    def test(self):
        N = 2048 
        return(''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N)))
    def get (self):
        self.write(str(g_port)) 
        self.write("\n")
        self.write('Hello Uma webpage ')        
        self.write(str(uuid.uuid4()))        
        self.write(self.test())        
    def post(self):
	self.write("fdsfa")

class SensorHandler(tornado.web.RequestHandler):
    """Uses an aysnchronous call to an RPC server to calculate fib(x).
    As with examples of asynchronous HTTP calls, this request will not finish
    until the remote response is received."""
    def get(self):
	self.write("fdsaf") 
    def post(self, number=''):
	self.write("fdsfsa")

class PikaClient(object):
    """A modified class as described in pika's demo_tornado.py.
    It handles the connection for the Tornado instance. Messaging/RPC
    callbacks are handled by the Tornado RequestHandler above."""
    def __init__(self):
        self.connecting = False
        self.connection = None
        self.channel = None
        #self.L = log_class.Logger() 
    def connect(self):
        if self.connecting:
            log.info('Already connecting to RabbitMQ.')
            return
        #self.L.logger.info("Connecting to RabbitMQ")
        self.connecting = True
        creds = pika.PlainCredentials('guest', 'guest')
        params = pika.ConnectionParameters(host='localhost', port=5672,
                                           virtual_host='/', credentials=creds)
        self.connection = TornadoConnection(params,
                                            on_open_callback=self.on_connect)
        self.connection.add_on_close_callback(self.on_closed)

    def on_connect(self, connection):
        self.connection = connection
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        #self.L.logger.info('Channel Open')
        self.channel = channel
        # I'm having trouble using named exchanges.
        ## channel.exchange_declare(exchange='rpc_ex', type='direct',
        ##                          auto_delete=True, durable=False,
        ##                          callback=self.on_exchange_declare)

    def on_exchange_declare(self, frame):
        log.info("Exchange declared.")

    def on_basic_cancel(self, frame):
        log.info('Basic Cancel Ok.')
        # If we don't have any more consumer processes running close
        self.connection.close()

    def on_closed(self, connection):
        # We've closed our pika connection so stop the demo
        tornado.ioloop.IOLoop.instance().stop()


def main():
    pika_client = PikaClient()
    application = tornado.web.Application(
    	[(r'/sensor/.*', SensorHandler),(r'/',MainHandler)],
	**{'pika_client': pika_client})
    try:
        port = int(sys.argv[1])  # $ python tornadoweb_pika.py 80
    except:
        port = 8000 
    g_port = port
    application.listen(port)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_timeout(time.time() + .1, pika_client.connect)
    ioloop.start()

if __name__ == '__main__':
    main()
