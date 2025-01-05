const mysql = require('mysql2');

async function search(dbConnection, searchQuery) {
  return new Promise((resolve, reject) => {
    const cleanedSearchQuery = searchQuery.replace(/\s+/g, '').toLowerCase();

    const query = `
      SELECT w.url_id, w.word, w.frequency, p.title, p.url, p.pagerank, 
             SUBSTRING_INDEX(SUBSTRING_INDEX(p.text, ' ', 50), ' ', -50) AS preview
      FROM word_frequencies w
      JOIN webpages p ON w.url_id = p.id
      WHERE CONCAT(w.word) LIKE ?
      AND LOWER(REPLACE(p.title, ' ', '')) LIKE ?
      ORDER BY 
        CASE 
          WHEN LOWER(REPLACE(p.title, ' ', '')) LIKE ? THEN 1
          ELSE 2
        END, 
        p.pagerank DESC, w.frequency DESC
    `;

    const fullSearchQuery = `%${cleanedSearchQuery}%`;
    const titleSearchQuery = `%${cleanedSearchQuery}%`;

    dbConnection.execute(query, [fullSearchQuery, titleSearchQuery, titleSearchQuery], (err, results) => {
      if (err) {
        return reject(err);
      }

      resolve(results);
    });
  });
}

module.exports = { search };
