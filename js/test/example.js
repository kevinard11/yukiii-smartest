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