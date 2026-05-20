-- Create tables for the 64 frameworks and 13 principles
CREATE TABLE IF NOT EXISTS frameworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    title TEXT,
    author_date TEXT,
    publisher TEXT,
    doi_url TEXT,
    objective TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filename TEXT
);

CREATE TABLE IF NOT EXISTS principles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS indicator_matrix (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_id INTEGER REFERENCES frameworks(id),
    principle_id INTEGER REFERENCES principles(id),
    indicator_id INTEGER REFERENCES indicators(id),
    indicator_value NUMERIC,
    indicator_description TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_id INTEGER REFERENCES frameworks(id),
    filename TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    extracted_text TEXT,
    clustering_group INTEGER,
    processed_at TIMESTAMP
);

-- Indexing for performance
CREATE INDEX IF NOT EXISTS idx_framework_objective ON frameworks(objective);
CREATE INDEX IF NOT EXISTS idx_matrix_lookup ON indicator_matrix(framework_id, principle_id, indicator_id);

-- Seeding sample data for testing (only if principles are empty)
INSERT INTO principles (name) 
SELECT 'Soil Organic Matter' WHERE NOT EXISTS (SELECT 1 FROM principles WHERE name = 'Soil Organic Matter');
INSERT INTO principles (name) 
SELECT 'Nutrient Cycling' WHERE NOT EXISTS (SELECT 1 FROM principles WHERE name = 'Nutrient Cycling');
INSERT INTO principles (name) 
SELECT 'Soil Structure' WHERE NOT EXISTS (SELECT 1 FROM principles WHERE name = 'Soil Structure');
INSERT INTO principles (name) 
SELECT 'Biological Activity' WHERE NOT EXISTS (SELECT 1 FROM principles WHERE name = 'Biological Activity');
INSERT INTO principles (name) 
SELECT 'Water Regulation' WHERE NOT EXISTS (SELECT 1 FROM principles WHERE name = 'Water Regulation');

INSERT INTO indicators (name, description)
SELECT 'TOC', 'Total Organic Carbon' WHERE NOT EXISTS (SELECT 1 FROM indicators WHERE name = 'TOC');
INSERT INTO indicators (name, description)
SELECT 'PMN', 'Potentially Mineralizable Nitrogen' WHERE NOT EXISTS (SELECT 1 FROM indicators WHERE name = 'PMN');
INSERT INTO indicators (name, description)
SELECT 'Aggregate Stability', 'Resistance of soil aggregates to breakdown' WHERE NOT EXISTS (SELECT 1 FROM indicators WHERE name = 'Aggregate Stability');
INSERT INTO indicators (name, description)
SELECT 'Respiration', 'Microbial CO2 production' WHERE NOT EXISTS (SELECT 1 FROM indicators WHERE name = 'Respiration');

CREATE TABLE IF NOT EXISTS suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL, -- 'indicator_principle' or 'framework'
    action TEXT NOT NULL, -- 'addition' or 'deletion'
    target_name TEXT NOT NULL, -- Name of indicator/principle or framework
    parent_target TEXT, -- If indicator, this is the principle; if principle, this is null.
    evidence_url TEXT,
    contact_details TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'included', 'excluded', 'disregarded'
    dev_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
