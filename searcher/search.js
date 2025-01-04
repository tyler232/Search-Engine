const mysql = require('mysql2');

function search(dbConnection, searchQuery) {
  return new Promise((resolve, reject) => {
    const searchWords = searchQuery.split(' ');
    const placeholders = searchWords.map(() => '?').join(', ');

    const query = `
      SELECT w.url_id, w.word, w.frequency, p.title, p.url, p.pagerank
      FROM word_frequencies w
      JOIN webpages p ON w.url_id = p.id
      WHERE w.word IN (${placeholders})
      ORDER BY p.pagerank DESC, w.frequency DESC
    `;

    dbConnection.execute(query, searchWords, (err, results) => {
      if (err) {
        return reject(err);
      }
      
      resolve(results);
    });
  });
}

module.exports = { search };
