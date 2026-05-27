require("dotenv").config();

console.log("URL:", process.env.TURSO_DATABASE_URL);
console.log("TOKEN EXISTS:", !!process.env.TURSO_AUTH_TOKEN);

const { createClient } = require("@libsql/client");

const db = createClient({
  url: process.env.TURSO_DATABASE_URL,
  authToken: process.env.TURSO_AUTH_TOKEN,
});

async function testDatabase() {
  try {
    await db.execute(`
      CREATE TABLE IF NOT EXISTS test_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL
      )
    `);

    await db.execute({
      sql: "INSERT INTO test_messages (message) VALUES (?)",
      args: ["Hello from Turso"],
    });

    const result = await db.execute("SELECT * FROM test_messages");

    console.log("Database connected successfully!");
    console.log(result.rows);
  } catch (error) {
    console.error("Database error:", error);
  }
}

testDatabase();