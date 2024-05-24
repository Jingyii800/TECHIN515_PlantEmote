const { Pool } = require('pg');

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


// 连接到数据库
client.connect(err => {
    if (err) {
        console.error('连接数据库失败:', err.stack);
    } else {
        console.log('成功连接到数据库');
    }

    // 执行一个简单的 SQL 查询
    client.query('SELECT NOW()', (err, res) => {
        if (err) {
            console.error('查询失败:', err.stack);
        } else {
            console.log('当前时间:', res.rows[0].now); // 显示数据库服务器的当前时间
        }

        // 关闭数据库连接
        client.end();
    });
});
