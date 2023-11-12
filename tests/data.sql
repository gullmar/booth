INSERT INTO products (id, name, description)
VALUES
	('97170a30-6550-4684-ae1e-6b31f81f2511', 'Onion', 'A vegetable.'),
	('1562d569-8eee-4555-b991-79b32576b5b0', 'Carrot', 'Another vegetable.');

INSERT INTO offers (product_id, price, items_in_stock)
VALUES
	('97170a30-6550-4684-ae1e-6b31f81f2511', 100, 10),
	('97170a30-6550-4684-ae1e-6b31f81f2511', 200, 12),
	('97170a30-6550-4684-ae1e-6b31f81f2511', 300, 17),
	('1562d569-8eee-4555-b991-79b32576b5b0', 50, 8);
