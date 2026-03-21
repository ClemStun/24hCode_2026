create user 'boat'@'localhost' identified by 'boat';

CREATE DATABASE boat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON boat.* TO 'boat'@'localhost';
FLUSH PRIVILEGES;