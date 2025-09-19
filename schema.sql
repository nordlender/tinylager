CREATE TABLE archive_orders (
    orderId INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL
);
CREATE TABLE inventory (
    itemId TEXT PRIMARY KEY,      -- unique identifier, e.g., "tent"
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    img TEXT,
    description TEXT,
    stock INTEGER NOT NULL
, max_stock INTEGER DEFAULT 0);
CREATE TABLE returns (
    returnId INTEGER PRIMARY KEY AUTOINCREMENT,
    orderId INTEGER NOT NULL,             -- original order
    timestamp TEXT NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY(orderId) REFERENCES orders(orderId)
);
CREATE TABLE orders (
    orderId INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL
);
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orderId INTEGER NOT NULL,
    itemId TEXT NOT NULL,
    lent INTEGER NOT NULL,
    returned INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(orderId) REFERENCES orders(orderId),
    FOREIGN KEY(itemId) REFERENCES inventory(itemId)
);
CREATE TABLE return_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    returnId INTEGER NOT NULL,
    itemId TEXT NOT NULL,
    returned INTEGER NOT NULL,            -- amount returned in this action
    FOREIGN KEY(returnId) REFERENCES returns(returnId),
    FOREIGN KEY(itemId) REFERENCES inventory(itemId)
);
CREATE TABLE archive_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orderId INTEGER NOT NULL,
    itemId TEXT NOT NULL,
    lent INTEGER NOT NULL,
    returned INTEGER NOT NULL,
    FOREIGN KEY (orderId) REFERENCES archive_orders(orderId)
);
