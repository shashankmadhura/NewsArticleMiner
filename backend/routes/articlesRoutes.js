const express = require('express');
const router = express.Router();
const articlesController = require('../controllers/articlesController');

// Route to retrieve articles based on criteria
router.get('/', articlesController.getArticles);
router.get('/hourly_summary', articlesController.getHourlyReport);


module.exports = router;
