const express = require('express');
const app = express();
const articlesRoutes = require('./routes/articlesRoutes');
const logger = require('./logger')
const cors = require('cors');
require('dotenv').config(); // Load environment variables from .env file

// Enable CORS for all routes
app.use(cors());

// Middleware to log requests
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.url}`);
  next();
});

// Middleware to parse JSON bodies
app.use(express.json());

// Mount articles routes
app.use('/articles', articlesRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error(err.stack);
  res.status(500).send('Something went wrong!');
});

// Start the server
const port = process.env.PORT || 3000;
app.listen(port, () => {
  logger.info(`Server is running on port ${port}`);
});
