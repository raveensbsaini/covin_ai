CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "phone" TEXT UNIQUE ,
    "email" TEXT UNIQUE ,
    "password" TEXT UNIQUE,
    "amount" INTEGER DEFAULT(0)
);
CREATE TABLE IF NOT EXISTS "expenses" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "amount" INTEGER DEFAULT(0),
    "time" REAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "method" TEXT NOT NULL,
    "split_data" TEXT DEFAULT(NULL),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS "loans" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "expense_id" INTEGER NOT NULL,
    "borrower_id" INTEGER NOT NULL,
    "lender_id" INTEGER,"amount" INTEGER NOT NULL,
    FOREIGN KEY(borrower_id) REFERENCES users(id),
    FOREIGN KEY(expense_id) REFERENCE expenses(id),
    FOREIGN KEY(lender_id) REFERENCES users(id)
);
