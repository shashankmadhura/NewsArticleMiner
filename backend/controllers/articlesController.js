const { getConnection, executeQuery } = require('../db');
const logger = require('../logger')


const getArticles = async (req, res) => {
  try {
    const publisher = req.query.publisher;
    const publicationDate = req.query.publicationDate;
    const pgIndex = parseInt(req.query.pgIndex) || 0;
    const pgItems = parseInt(req.query.pgItems) || 20;
    const publicationDateStart = req.query.publicationDateStart
    const publicationDateEnd = req.query.publicationDateEnd
    const authorName = req.query.authorName

    // let sql = 'SELECT * FROM articles';
    const params = [];

    let sql = 'SELECT articles.*, publishers.name AS publisher, GROUP_CONCAT(authors.name SEPARATOR ", ") AS authors FROM articles';
    sql += ' INNER JOIN publishers ON articles.publisher_id = publishers.id';
    sql += ' LEFT JOIN article_authors ON articles.id = article_authors.article_id';
    sql += ' LEFT JOIN authors ON article_authors.author_id = authors.id';
    
    let whereClauseAdded = false;
    
    if (publisher) {
      sql += ' WHERE publishers.name = ?';
      params.push(publisher);
      whereClauseAdded = true;
    }
    
    if (authorName) {
      if (whereClauseAdded) {
        sql += ' AND authors.name LIKE ?';
      } else {
        sql += ' WHERE authors.name LIKE ?';
        whereClauseAdded = true;
      }
      params.push(`%${authorName}%`);
    }
    
    if (publicationDateStart && publicationDateEnd) {
      if (whereClauseAdded) {
        sql += ' AND articles.published_date BETWEEN FROM_UNIXTIME(?) AND FROM_UNIXTIME(?)';
      } else {
        sql += ' WHERE articles.published_date BETWEEN FROM_UNIXTIME(?) AND FROM_UNIXTIME(?)';
        whereClauseAdded = true;
      }
      params.push(publicationDateStart);
      params.push(publicationDateEnd);
    } else if (publicationDate) {
      if (whereClauseAdded) {
        sql += ' AND articles.published_date = FROM_UNIXTIME(?)';
      } else {
        sql += ' WHERE articles.published_date = FROM_UNIXTIME(?)';
        whereClauseAdded = true;
      }
      params.push(publicationDate);
    }
    
    sql += ' GROUP BY articles.id';

    sql += ' LIMIT ?, ?';
    params.push(pgIndex);
    params.push(pgItems);

    const connection = await getConnection();
    const results = await executeQuery(connection, sql, params);
    connection.release();
    res.json(results);
  } catch (error) {
    logger.error(`Error retrieving articles: ${error}`)
    console.error(`Error retrieving articles: ${error}`);
    res.status(500).json({ error: 'Internal Server Error' });
  }
};


const getHourlyReport = async (req, res) => {
  try {
    let publisher = req.query.publisher;
    let date = req.query.date //2023-02-01
    if(!date) {
      return res.status(500).json({ error: 'Missing query params date' });
    }
    if(!publisher) {
      return res.status(500).json({ error: 'Missing query params publisher' });
    }

    let sql = 'SELECT hs.publication_hour, p.name AS publisher_name, hs.article_count FROM hourly_summary hs JOIN publishers p ON hs.publisher_id = p.id WHERE p.name = ? AND DATE(hs.publication_hour) = ? ORDER BY hs.publication_hour ASC'
    const connection = await getConnection();
    const results = await executeQuery(connection, sql, [publisher, date]);
    connection.release();
    res.json(results);
  } catch (error) {
    logger.error(`Error retrieving articles: ${error}`)
    console.error(`Error retrieving articles: ${error}`);
    res.status(500).json({ error: 'Internal Server Error' });
  }
};

module.exports = {
  getArticles,
  getHourlyReport

}