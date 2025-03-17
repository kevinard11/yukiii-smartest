#!/usr/bin/python

# ROUTING_KEY = 'https://microservices.dev.bravo.bfi.co.id/master'
# class Publisher:
#     HOST = os.getenv('AMQP_HOST', 'rabbitmq')
#     VIRTUAL_HOST = '/'
#     EXCHANGE='robot-shop'
#     TYPE='direct'
#     ROUTING_KEY = 'https://microservices.dev.bravo.bfi.co.id/master'

#     def __init__(self, logger):
#         self._logger = logger
#         self._params = pika.connection.ConnectionParameters(
#             host=self.HOST,
#             virtual_host=self.VIRTUAL_HOST,
#             credentials=pika.credentials.PlainCredentials('guest', 'guest'))
#         self._conn = None
#         self._channel = None
#         bar()

#     def _connect(self):
#         if not self._conn or self._conn.is_closed or self._channel is None or self._channel.is_closed:
#             self._conn = pika.BlockingConnection(self._params)
#             self._channel = self._conn.channel()
#             self._channel.exchange_declare(exchange=self.EXCHANGE, exchange_type=self.TYPE, durable=True)
#             self._logger.info('connected to broker')
    # def foo():
    #     base_url = 'https://microservices.dev.bravo.bfi.co.id/master'
    #     response = requests.get(base_url)
    #     response = requests.get('https://gateway-gc.bfi.co.id/confins')
    #     print(response.status_code)
    #     for i in [1,2]:
    #         arg1 = 'a'
    #         c = test('aasda')
    #         bar(globalList)


# # import requests
# import httpx

# # Synchronous
# response = httpx.get("https://microservices.dev.bravo.bfi.co.id/master/asdad")
# print(response.json())

# async def fetch():
#     async with httpx.AsyncClient() as client:
#         response = await client.get("https://jsonplaceholder.typicode.com/posts/1")
#         print(response.json())

# def foo():
#     base_url = 'https://microservices.dev.bravo.bfi.co.id/master'
#     response = requests.get(base_url)
#     response = requests.get('https://gateway-gc.bfi.co.id/confins')
#     print(response.status_code)
#     for i in [1,2]:
#         arg1 = 'a'
#         c = test('aasda')
#         bar(globalList)

# import urllib.request
# import json

# url = "https://jsonplaceholder.typicode.com/posts/2"
# with urllib.request.urlopen(url) as responses:
#         data = json.loads(responses.read().decode())
#         print(data)

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
class Publisher:
    HOST = os.getenv('AMQP_HOST', 'rabbitmq')
    VIRTUAL_HOST = '/'
    EXCHANGE='robot-shop'
    TYPE='direct'
    ROUTING_KEY = 'orders'

    def _publish(self, msg, headers):
        self._channel.basic_publish(exchange=self.EXCHANGE,
                                    routing_key=self.ROUTING_KEY,
                                    properties=pika.BasicProperties(headers=headers),
                                    body=json.dumps(msg).encode())
        self._logger.info('message sent')
def test(s):
    req = requests.get('http://{user}:8080/check/{id}'.format(user='user', id=id))
    publisher._publish(order, headers)

# def health():
#     return 'OK'

# # main program
# globalRunCount = 10
# globalList = ['a', 'b']
# test = True
# foo()
# baz()
# exit(0)

# import pycurl
# from io import BytesIO
# buffer = BytesIO()
# c = pycurl.Curl()
# c.setopt(c.URL, "https://jsonplaceholder.typicode.com/posts/1")
# c.setopt(c.WRITEDATA, buffer)
# c.perform()
# c.close()

# import aiohttp
# import asyncio

# async def fetch():
#     async with aiohttp.ClientSession() as session:
#         async with session.get("https://jsonplaceholder.typicode.com/posts/1") as response:
#             print(await response.json())

# import grequests

# url = "https://microservices.dev.bravo.bfi.co.id/master/sdad/adddd/wwsdasda/sdsdsd"

# requests_list = grequests.get(url)
# responses = grequests.map(requests_list)

# import pika

# # Connect to RabbitMQ
# def publishMessage(queue, exchange, routing_key, body):
#     connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
#     channel = connection.channel()

#     # Declare a queue
#     channel.queue_declare(queue)

#     # Publish a message
#     channel.basic_publish(queue, routing_key, body)
#     channel.basic_publish('agent_queue', routing_key, body)
#     print("Message sent")
#     connection.close()

# publishMessage('master_queue', 'master-queue', 'routing-key', 'Hello')

# import asyncio
# import aio_pika

# async def main(routing_key):
#     connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
#     async with connection:
#         channel = await connection.channel()
#         await channel.default_exchange.publish(
#             aio_pika.Message(body=b"Hello Async RabbitMQ"),
#             routing_key="master_queue",
#         )
#         print("Message sent")

# main()

# from confluent_kafka import Producer

# conf = {"bootstrap.servers": "localhost:9092"}
# producer = Producer(conf)

# producer.produce("agent_queue", key="key1", value="Hello, Kafka!")
# producer.flush()
# print("Message sent")

# import asyncio
# from aiokafka import AIOKafkaProducer

# async def send():
#     producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
#     await producer.start()
#     try:
#         await producer.send_and_wait("agent_queue", b"Hello, Async Kafka!")
#         print("Message sent")
#     finally:
#         await producer.stop()

# asyncio.run(send())

# from kafka import KafkaProducer

# # Create Kafka producer
# producer = KafkaProducer(
#     bootstrap_servers="localhost:9092",
#     key_serializer=lambda k: k.encode() if k else None,  # Serialize keys (optional)
#     value_serializer=lambda v: v.encode() if v else None  # Serialize values
# )

# # Send message
# producer.send("agent_queue", key="message-key", value="Hello, Kafka!")

# # Ensure messages are sent
# producer.flush()
# print("Message sent successfully")

# # Close the producer
# producer.close()

# Prometheus
@app.route('/metrics', methods=['POST'])
def metrics():
    res = []
    for m in PromMetrics.values():
        res.append(prometheus_client.generate_latest(m))

    return Response(res, mimetype='text/plain')



