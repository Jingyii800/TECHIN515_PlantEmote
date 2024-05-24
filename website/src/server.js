const express = require('express');
const path = require('path');
const { Pool } = require('pg');

const app = express();
const port = process.env.PORT || 3000;

// Enable parsing of JSON bodies in POST requests
app.use(express.json());

// Serve static files from the 'public' directory
// 确保路径是从 'server.js' 的位置正确引用 'public' 文件夹
app.use(express.static(path.join(__dirname, '..', 'public')));

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_DATABASE,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
  ssl: {
    rejectUnauthorized: false,
  }
});


// Endpoint to test database connection
app.get('/test-db', async (req, res) => {
  try {
    const data = await pool.query('SELECT * FROM telemetry_data');
    console.log('Connection successful. Server time is:', data.rows[0].now);
    res.status(200).json({
      message: "Connection successful",
      time: data.rows[0].now
    });
  } catch (err) {
    console.error('Database connection error', err.stack);
    res.status(500).json({
      message: "Failed to connect to the database",
      error: err.message
    });
  }
});



 // Root route to handle GET requests to '/'
 app.get('/', (req, res) => {
   res.sendFile(path.join(__dirname, '..', 'public', 'index.html'));
 });

 app.listen(port, () => {
   console.log(`Server running on http://localhost:${port}`);
 });

 // Endpoint to retrieve data from the database
 app.get('/plant-data', async (req, res) => {
   try {
     const query = 'SELECT soil_moisture, standard_plot_url, artistic_image_url FROM telemetry_data';
     const data = await pool.query(query);
     res.json(data.rows);
   } catch (err) {
     console.error('Database query error', err.stack);
     res.status(500).send('Failed to retrieve data from the database');
   }
 });
