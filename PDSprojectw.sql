create database Project3f;
USE project3f;

-- User table for common login info
CREATE TABLE user (
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (username)
);

-- Staff table
CREATE TABLE staff (
    username VARCHAR(50),
    staff_details VARCHAR(255), -- Add role-specific fields as needed
    FOREIGN KEY (username) REFERENCES user (username)
);

-- Client table
CREATE TABLE client (
    username VARCHAR(50),
    client_details VARCHAR(255), -- Add role-specific fields as needed
    FOREIGN KEY (username) REFERENCES user (username)
);

-- Volunteer table
CREATE TABLE volunteer (
    username VARCHAR(50),
    volunteer_details VARCHAR(255), -- Add role-specific fields as needed
    FOREIGN KEY (username) REFERENCES user (username)
);


-- Create the Category table
CREATE TABLE Category (
    mainCategory VARCHAR(50),
    subCategory VARCHAR(50),
    catNotes VARCHAR(255),
    PRIMARY KEY (mainCategory, subCategory)
);

-- Create the Item table
CREATE TABLE Item (
    itemID INT PRIMARY KEY AUTO_INCREMENT,
    iDescription VARCHAR(255),
    photo VARCHAR(255),
    color VARCHAR(50),
    isNew BOOLEAN,
    hasPieces BOOLEAN,
    material VARCHAR(50),
    mainCategory VARCHAR(50),
    subCategory VARCHAR(50),
    FOREIGN KEY (mainCategory, subCategory) REFERENCES Category (mainCategory, subCategory)
);

-- Create the Location table
CREATE TABLE Location (
    roomNum INT NOT NULL,
    shelfNum INT NOT NULL,
    shelfDescription VARCHAR(255),
    PRIMARY KEY (roomNum, shelfNum)
);

-- Create the Piece table
CREATE TABLE Piece (
    itemID INT NOT NULL,
    pieceNum INT NOT NULL,
    pDescription VARCHAR(255),
    length DECIMAL(10, 2),
    width DECIMAL(10, 2),
    height DECIMAL(10, 2),
    roomNum INT NOT NULL,
    shelfNum INT NOT NULL,
    pNotes VARCHAR(255),
    PRIMARY KEY (itemID, pieceNum),
    FOREIGN KEY (itemID) REFERENCES Item (itemID),
    FOREIGN KEY (roomNum, shelfNum) REFERENCES Location (roomNum, shelfNum)
);
-- Ordered table
CREATE TABLE Ordered (
    orderID INT PRIMARY KEY AUTO_INCREMENT,
    orderDate DATE,
    orderNotes VARCHAR(255),
    supervisor VARCHAR(50), -- Username of staff supervising
    client VARCHAR(50),     -- Username of client
    FOREIGN KEY (supervisor) REFERENCES user (username),
    FOREIGN KEY (client) REFERENCES user (username)
);

-- ItemIn table
CREATE TABLE ItemIn (
    itemID INT,
    orderID INT,
    found BOOLEAN DEFAULT FALSE, -- Whether the item is ready for delivery
    PRIMARY KEY (itemID, orderID),
    FOREIGN KEY (itemID) REFERENCES Item (itemID),
    FOREIGN KEY (orderID) REFERENCES Ordered (orderID)
);

-- Delivered table (for tracking delivery status)
CREATE TABLE Delivered (
    username VARCHAR(50), -- Volunteer delivering the order
    orderID INT,
    status VARCHAR(50),
    deliveryDate DATE,
    PRIMARY KEY (username, orderID),
    FOREIGN KEY (username) REFERENCES user (username),
    FOREIGN KEY (orderID) REFERENCES Ordered (orderID)
);

-- Donation table (for tracking donations)
CREATE TABLE Donation (
    donationID INT PRIMARY KEY AUTO_INCREMENT,
    donorUsername VARCHAR(50),
    donationDate DATE,
    itemID INT,
    FOREIGN KEY (donorUsername) REFERENCES user (username),
    FOREIGN KEY (itemID) REFERENCES Item (itemID)
);

DROP TABLE IF EXISTS Donor;

CREATE TABLE Donor (
    donorID INT PRIMARY KEY,
    username VARCHAR(50), -- No foreign key constraint here
    donorDetails VARCHAR(255)
);




CREATE TABLE PersonPhone (
    username VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    PRIMARY KEY (username, phone),
    FOREIGN KEY (username) REFERENCES user(username)
);


CREATE TABLE TransactionLog (
    logID INT AUTO_INCREMENT PRIMARY KEY,      -- Unique identifier for each log entry
    username VARCHAR(50) NOT NULL,             -- Username of the person performing the action
    role VARCHAR(20) NOT NULL,                 -- Role of the user (e.g., staff, volunteer, client)
    action VARCHAR(255) NOT NULL,              -- Description of the action performed
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, -- Time the action was performed
    FOREIGN KEY (username) REFERENCES user(username)
);



ALTER TABLE user
ADD COLUMN fname VARCHAR(50) NOT NULL,
ADD COLUMN lname VARCHAR(50) NOT NULL,
ADD COLUMN email VARCHAR(100) NOT NULL;

-- Insert sample data into Category
-- INSERT INTO Category (mainCategory, subCategory, catNotes)
-- VALUES 
-- ('Furniture', 'Sofa', 'Comfortable seating'),
-- ('Kitchenware', 'Cookware', 'Pots and pans for cooking');

-- Insert sample data into Item
-- INSERT INTO Item (iDescription, photo, color, isNew, hasPieces, material, mainCategory, subCategory)
-- VALUES
-- ('Yellow Sofa', 'sofa.jpg', 'Yellow', FALSE, TRUE, 'Fabric', 'Furniture', 'Sofa'),
-- ('Frying Pan', 'pan.jpg', 'Black', TRUE, FALSE, 'Metal', 'Kitchenware', 'Cookware');



-- Insert sample data into Location
-- INSERT INTO Location (roomNum, shelfNum, shelfDescription)
-- VALUES
-- (1, 1, 'Top-left shelf in Room 1'),
-- (1, 2, 'Top-right shelf in Room 1'),
-- (2, 1, 'Bottom-left shelf in Room 2');

-- Insert sample data into Piece
-- INSERT INTO Piece (itemID, pieceNum, pDescription, length, width, height, roomNum, shelfNum, pNotes)
-- VALUES
-- (1, 1, 'Sofa Body', 200.0, 80.0, 100.0, 1, 1, 'Main piece of sofa'),
-- (1, 2, 'Sofa Cushion', 50.0, 50.0, 20.0, 1, 2, 'Accessory for sofa'),
-- (2, 1, 'Frying Pan', 30.0, 30.0, 10.0, 2, 1, 'Single frying pan');



-- Insert role-specific data for testing
-- INSERT INTO staff (username, staff_details) VALUES ('staff1', 'Supervisor for orders');
-- INSERT INTO client (username, client_details) VALUES ('client1', 'Regular client');
-- INSERT INTO client (username, client_details) VALUES ('client2', 'Regular client');
-- INSERT INTO volunteer (username, volunteer_details) VALUES ('volunteer1', 'Delivery volunteer');
-- INSERT INTO staff (username, staff_details) VALUES ('staff2', 'Head for orders');
-- Insert sample orders
-- INSERT INTO Ordered (orderDate, orderNotes, supervisor, client)
-- VALUES ('2024-12-01', 'First order', 'staff1', 'client1');
-- INSERT INTO Ordered (orderDate, orderNotes, supervisor, client)
-- VALUES ('2024-12-01', 'First order', 'client1', 'client2');



-- Insert sample items in orders
-- INSERT INTO ItemIn (itemID, orderID, found) 
-- VALUES 
-- (1, 2, TRUE), 
-- (2, 2, FALSE);


-- ALTER TABLE Donation DROP FOREIGN KEY Donation_ibfk_1; -- Drop the existing foreign key
-- ALTER TABLE Donation ADD FOREIGN KEY (donorUsername) REFERENCES staff (username); -- Add a new foreign key to staff

-- INSERT INTO Donation (donorUsername, donationDate, itemID)
-- VALUES ('staff1', CURDATE(), 1);

-- INSERT INTO Delivered (username, orderID, status, deliveryDate)
-- VALUES ('volunteer1', 2, 'In Progress', '2024-12-10');


-- INSERT INTO Donor (username, donorDetails) VALUES 
-- ('staff1', 'Frequent furniture donor');


-- select * from PersonPhone;


-- UPDATE Ordered
-- SET status = 'Completed'
-- WHERE orderID = 2;





SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE Delivered;
TRUNCATE TABLE ItemIn;
TRUNCATE TABLE Ordered;
TRUNCATE TABLE Piece;
TRUNCATE TABLE Location;
TRUNCATE TABLE Donation;
TRUNCATE TABLE Donor;
TRUNCATE TABLE Item;
TRUNCATE TABLE Category;



SET FOREIGN_KEY_CHECKS = 1;

UPDATE staff
SET staff_details = 'Logistics Supervisor'
WHERE username = 'staff1';

UPDATE staff
SET staff_details = 'Inventory Manager'
WHERE username = 'staff2';

UPDATE staff
SET staff_details = 'Operations Head'
WHERE username = 'staff3';

UPDATE staff
SET staff_details = 'Warehouse Supervisor'
WHERE username = 'staff4';

UPDATE staff
SET staff_details = 'Procurement Manager'
WHERE username = 'staff5';

UPDATE client
SET client_details = 'Regular buyer for non-profits'
WHERE username = 'client1';

UPDATE client
SET client_details = 'Corporate client for bulk orders'
WHERE username = 'client2';

UPDATE client
SET client_details = 'Individual donor for electronics'
WHERE username = 'client3';

UPDATE client
SET client_details = 'Charity organization focusing on education'
WHERE username = 'client4';

UPDATE client
SET client_details = 'Occasional buyer for community events'
WHERE username = 'client5';



UPDATE volunteer
SET volunteer_details = 'Lead Driver for deliveries'
WHERE username = 'volunteer1';

UPDATE volunteer
SET volunteer_details = 'Packing specialist for fragile items'
WHERE username = 'volunteer2';

UPDATE volunteer
SET volunteer_details = 'Coordinator for delivery schedules'
WHERE username = 'volunteer3';

UPDATE volunteer
SET volunteer_details = 'Delivery supervisor for high-priority orders'
WHERE username = 'volunteer4';

UPDATE volunteer
SET volunteer_details = 'Warehouse assistant for inventory management'
WHERE username = 'volunteer5';





INSERT INTO Category (mainCategory, subCategory, catNotes) VALUES
('Furniture', 'Chair', 'Various types of chairs'),
('Furniture', 'Table', 'Various types of tables'),
('Electronics', 'Phone', 'Various phone models'),
('Electronics', 'Laptop', 'Variety of laptops'),
('Clothing', 'Shirts', 'Men and women shirts');


INSERT INTO Item (iDescription, photo, color, isNew, hasPieces, material, mainCategory, subCategory) VALUES
('Office Chair', 'chair1.jpg', 'Black', FALSE, FALSE, 'Metal', 'Furniture', 'Chair'),
('Dining Table', 'table1.jpg', 'Brown', TRUE, TRUE, 'Wood', 'Furniture', 'Table'),
('Smartphone', 'phone1.jpg', 'Gray', TRUE, FALSE, 'Plastic', 'Electronics', 'Phone'),
('Laptop', 'laptop1.jpg', 'Silver', TRUE, FALSE, 'Metal', 'Electronics', 'Laptop'),
('Cotton Shirt', 'shirt1.jpg', 'Blue', TRUE, FALSE, 'Cotton', 'Clothing', 'Shirts');


INSERT INTO Location (roomNum, shelfNum, shelfDescription) VALUES 
(1, 1, 'Top shelf near entrance'),
(2, 3, 'Right shelf next to windows'),
(3, 2, 'Bottom shelf by the wall'),
(4, 4, 'Left shelf in back'),
(5, 0, 'No specific shelf assigned');


INSERT INTO Piece (itemID, pieceNum, pDescription, length, width, height, pNotes, roomNum, shelfNum) VALUES
(1, 3, 'Chair armrest', 40.00, 10.00, 5.00, 'Comfortable armrest', 1, 1),
(2, 3, 'Table drawer', 50.00, 30.00, 10.00, 'Wooden table drawer', 2, 3),
(4, 3, 'Laptop battery', 15.00, 10.00, 2.00, 'Rechargeable battery', 3, 2),
(4, 4, 'Laptop adapter', 20.00, 10.00, 5.00, 'Power adapter', 3, 2),
(5, 1, 'Shirt pocket', 10.00, 10.00, 1.00, 'Extra soft pocket', 4, 4);





INSERT INTO Ordered (orderDate, orderNotes, supervisor, client) VALUES
('2023-08-15', 'Order for sofa and table', 'staff1', 'client1'),
('2023-08-16', 'Order for electronics', 'staff2', 'client2'),
('2023-08-17', 'Order for appliances', 'staff3', 'client3'),
('2023-08-18', 'Order for miscellaneous items', 'staff4', 'client4'),
('2023-08-19', 'Order for kitchen items', 'staff5', 'client5'),
('2023-08-20', 'Order for home decor', 'staff1', 'client2'),
('2023-08-21', 'Order for office furniture', 'staff2', 'client1'),
('2023-08-22', 'Order for educational supplies', 'staff3', 'client4'),
('2023-08-23', 'Order for community event', 'staff4', 'client3'),
('2023-08-24', 'Order for corporate event', 'staff5', 'client5');



INSERT INTO ItemIn (itemID, orderID, found) VALUES
(1, 1, TRUE), 
(2, 1, TRUE), 
(3, 2, TRUE), 
(4, 2, FALSE), 
(5, 3, TRUE), 
(1, 4, FALSE), 
(2, 5, TRUE), 
(3, 6, FALSE), 
(4, 7, TRUE), 
(5, 8, FALSE), 
(1, 9, TRUE), 
(2, 10, TRUE);



INSERT INTO Delivered (username, orderID, status, deliveryDate) VALUES
('volunteer1', 1, 'Delivered', '2023-08-16'), -- Order 1 delivered by volunteer1
('volunteer2', 2, 'Delivered', '2023-08-17'), -- Order 2 delivered by volunteer2
('volunteer3', 3, 'Pending', NULL),           -- Order 3 is still pending
('volunteer4', 4, 'Delivered', '2023-08-19'), -- Order 4 delivered by volunteer4
('volunteer5', 5, 'Pending', NULL),           -- Order 5 is still pending
('volunteer1', 6, 'Delivered', '2023-08-21'), -- Order 6 delivered by volunteer1
('volunteer2', 7, 'Delivered', '2023-08-22'), -- Order 7 delivered by volunteer2
('volunteer3', 8, 'Pending', NULL),           -- Order 8 is still pending
('volunteer4', 9, 'Delivered', '2023-08-25'), -- Order 9 delivered by volunteer4
('volunteer5', 10, 'Delivered', '2023-08-26'); -- Order 10 delivered by volunteer5


INSERT INTO Donation (donorUsername, donationDate, itemID) VALUES
('client1', '2023-08-10', 1), -- Donation of Office Chair by client1
('client2', '2023-08-11', 2), -- Donation of Dining Table by client2
('client3', '2023-08-12', 3), -- Donation of Smartphone by client3
('client4', '2023-08-13', 4), -- Donation of Laptop by client4
('client5', '2023-08-14', 5); -- Donation of Cotton Shirt by client5



