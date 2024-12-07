cd..
cd..
cd xampp\mysql\bin
CREATE DATABASE ecogrow_db;
USE ecogrow_db;
CREATE TABLE donators (
    donator_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(15),
    registration_date DATE NOT NULL
);
CREATE TABLE donators_tree (
    tree_id INT(11) NOT NULL AUTO_INCREMENT,
    tree_choice VARCHAR(255) NOT NULL,
    PRIMARY KEY (tree_id)
);
CREATE TABLE tree_types (
    tree_type_id INT(11) NOT NULL AUTO_INCREMENT,
    tree_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (tree_type_id)
);
CREATE TABLE donation_location (
    location_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    location_choice VARCHAR(255) NOT NULL
);
CREATE TABLE donation_history (
    history_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    donator_id INT(11) NOT NULL,
    tree_id INT(11) NOT NULL,
    location_id INT(11) NOT NULL,
    donation_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (donator_id) REFERENCES donators(donator_id),
    FOREIGN KEY (tree_id) REFERENCES donators_tree(tree_id),
    FOREIGN KEY (location_id) REFERENCES donation_location(location_id)
);
INSERT INTO donators_tree (tree_choice) VALUES
('Narra'),
('Mahogany'),
('Bamboo'),
('Mango'),
('Acacia'),
('Pine'),
('Coconut'),
('Jackfruit'),
('Santol'),
('Banana');
INSERT INTO tree_types (tree_name, description, price) VALUES
('Narra', 'A native tree known for its hardwood and strong presence.', 150.00),
('Mahogany', 'A tall tree that provides valuable timber used in furniture.', 120.00),
('Bamboo', 'A fast-growing tree known for its eco-friendly properties.', 100.00),
('Mango', 'A tropical fruit tree that produces sweet and juicy fruits.', 180.00),
('Acacia', 'A tree that is known for its fast growth and useful wood.', 140.00),
('Pine', 'An evergreen tree often planted in forests for timber.', 160.00),
('Coconut', 'A tropical tree that produces coconuts used in various products.', 110.00),
('Jackfruit', 'A tropical tree that produces large, sweet fruit.', 130.00),
('Santol', 'A tropical tree producing sweet and tangy fruits.', 115.00),
('Banana', 'A fruit-bearing tree that grows in tropical climates.', 90.00);

INSERT INTO donation_location (location_choice) VALUES
('Manila'),
('Cebu'),
('Davao'),
('Iloilo'),
('Cagayan de Oro'),
('Zamboanga'),
('Dumaguete'),
('Tacloban'),
('Tagbilaran'),
('Tarlac');
