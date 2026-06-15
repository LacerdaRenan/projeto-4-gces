USE conjuntura_db;

CREATE TABLE IF NOT EXISTS fact_housing_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    catalog_id INT NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    year_reference INT NOT NULL,
    quarter_reference VARCHAR(2) NOT NULL,
    vgv_launched_millions DECIMAL(15, 2) NULL,
    units_sold INT NULL,
    net_revenue_millions DECIMAL(15, 2) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (catalog_id) REFERENCES catalog_ingestion(id) ON DELETE CASCADE,
    INDEX idx_company_period (company_name, year_reference, quarter_reference)
);