require('dotenv').config();
const express = require('express');
const mysql = require('mysql2');
const path = require('path');
const { search } = require('./searcher/search');

const app = express();

// Connect MySQL
const getDbConnection = () => {
  return mysql.createConnection({
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASS
  });
};

// set view engine for ejs
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// middleware to serve static files
app.use(express.static(path.join(__dirname, 'public')));

// route to search page
app.get('/', (req, res) => {
  res.render('index');  // render index.ejs
});

// route to search results
app.get('/search', (req, res) => {
  const searchQuery = req.query.query;

  if (!searchQuery) {
    return res.status(400).send('Search query is required');
  }

  const dbConnection = getDbConnection();
  search(dbConnection, searchQuery)
    .then(results => {
      dbConnection.end();
      res.render('results', { searchQuery, results });
    })
    .catch(err => {
      dbConnection.end();
      console.error(err);
      res.status(500).send('Error occurred while searching');
    });
});

// start the server
const IP = process.env.SERVER_IP || 'localhost';
const PORT = process.env.SERVER_PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on http://${IP}:${PORT}`);
});
