INSERT INTO products (id, name, description)
VALUES
	('a', 'Onion', 'A vegetable.'),
	('b', 'Carrot', 'Another vegetable.');

INSERT INTO offers (id, product_id, price, items_in_stock)
VALUES
	('1', 'a', 100, 10),
	('2', 'a', 200, 12),
	('3', 'a', 300, 17),
	('4', 'b', 50, 8);
