INSERT INTO users (username, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

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
