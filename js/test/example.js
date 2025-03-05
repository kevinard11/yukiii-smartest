#!/home/utils/node-v14.5.0/bin/node

fetch('https://api.example.com/data')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));

const axios = require('axios'); // Jika di Node.js, tidak perlu jika di browser

axios.get('https://api.example.com/data/eeeee')
  .then(response => console.log(response.data))
  .catch(error => console.error('Error:', error));

const got = require('got');

(async () => {
  try {
    const response = await got('https://api.example.com/data/asdasdasdasd').json();
    console.log(response);
  } catch (error) {
    console.error(error);
  }
})();

const amqp = require('amqplib');

async function sendMessage() {
    const connection = await amqp.connect('amqp://localhost');
    const channel = await connection.createChannel();
    const queue = 'agent_queue';

    await channel.assertQueue(queue, { durable: false });
    channel.sendToQueue(queue, Buffer.from('Hello, RabbitMQ!'));

    console.log(" [x] Sent 'Hello, RabbitMQ!'");
    setTimeout(() => {
        connection.close();
    }, 500);
}

sendMessage();

const { Kafka } = require('kafkajs');

const kafka = new Kafka({
    clientId: 'my-app',
    brokers: ['localhost:9092']
});

const producer = kafka.producer();

async function sendMessages() {
    await producer.connect();
    await producer.send({
        topic: 'agent_queue',
        messages: [{ value: 'Hello, Kafka!' }],
    });

    console.log(" [x] Sent 'Hello, Kafka!'");
    await producer.disconnect();
};

sendMessage();
