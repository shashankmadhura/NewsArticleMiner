const mysql = require('mysql');
require('dotenv').config(); 

console.log("process.env.DB_USER", process.env.DB_USER, process.env.DB_PASSWORD)

const pool = mysql.createPool({
  connectionLimit: 10,
  host: process.env.DB_HOST,
  user: 'user1',
  password: '1234',
  database: process.env.DB_NAME
});

console.log("database pool created")

// Helper function to get a database connection from the pool
const getConnection = () => {
  return new Promise((resolve, reject) => {
    pool.getConnection((err, connection) => {
      if (err) {
        reject(err);
      } else {
        resolve(connection);
      }
    });
  });
};

// Helper function to execute a query
const executeQuery = (connection, query, params) => {
  return new Promise((resolve, reject) => {
    connection.query(query, params, (err, results) => {
      if (err) {
        reject(err);
      } else {
        resolve(results);
      }
    });
  });
};

module.exports = {
  getConnection,
  executeQuery
};
