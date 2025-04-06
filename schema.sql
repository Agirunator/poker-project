CREATE TABLE IF NOT EXISTS users (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK(username GLOB '[A-Za-z0-9]*')  -- Ensures the username is alphanumeric
);

CREATE TABLE IF NOT EXISTS balance (
    USER_ID INTEGER PRIMARY KEY REFERENCES users (ID),  -- Foreign key to 'users' table
    balance REAL NOT NULL DEFAULT 0.0  -- Default balance is 0
);

CREATE TABLE IF NOT EXISTS transactions (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    USER_ID INTEGER REFERENCES users (ID),  -- Foreign key to 'users' table
    amount REAL NOT NULL,
    transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
