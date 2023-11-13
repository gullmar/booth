DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS offers;

CREATE TABLE products (
	id TEXT PRIMARY KEY,
	name TEXT UNIQUE NOT NULL,
	description TEXT NOT NULL
);

CREATE TABLE offers (
	id TEXT PRIMARY KEY,
	product_id TEXT NON NULL,
	price INTEGER NOT NULL,
	items_in_stock INTEGER NOT NULL,
	FOREIGN KEY (product_id) REFERENCES products (id)
);
