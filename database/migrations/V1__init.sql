CREATE DATABASE IF NOT EXISTS conjuntura_db;
USE conjuntura_db;

CREATE TABLE IF NOT EXISTS catalog_ingestion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    document_url TEXT NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    status ENUM('PENDING', 'PROCESSED', 'ERROR') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_company (company_name)
);