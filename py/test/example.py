#!/usr/bin/python

class Publisher:
    HOST = os.getenv('AMQP_HOST', 'rabbitmq')
    VIRTUAL_HOST = '/'
    EXCHANGE='robot-shop'
    TYPE='direct'
    ROUTING_KEY = 'orders'

    # def __init__(self, logger):
    #     self._logger = logger
    #     self._params = pika.connection.ConnectionParameters(
    #         host=self.HOST,
    #         virtual_host=self.VIRTUAL_HOST,
    #         credentials=pika.credentials.PlainCredentials('guest', 'guest'))
    #     self._conn = None
    #     self._channel = None
    #     bar()

    # def _connect(self):
    #     if not self._conn or self._conn.is_closed or self._channel is None or self._channel.is_closed:
    #         self._conn = pika.BlockingConnection(self._params)
    #         self._channel = self._conn.channel()
    #         self._channel.exchange_declare(exchange=self.EXCHANGE, exchange_type=self.TYPE, durable=True)
    #         self._logger.info('connected to broker')

def foo():

    for i in [1,2]:
        arg1 = 'a'
        c = test('aasda')
        bar(globalList)
    
    return c

# def bar( myList ):
#     global globalRunCount
#     globalRunCount = (globalRunCount + 1) * 2
#     if globalRunCount < 2:
#         bar(myList)
#     print("hello")
#     baz()
# def baz():
#     # intentionally put no space above this def
#     print("world %s" % globalList)

# def test(s):
#     b = 120
#     return b, 'asdasd'

# def health():
#     return 'OK'

# # main program
globalRunCount = 10
globalList = ['a', 'b']
test = True
foo()
baz()
exit(0)



