-- Drop tables if they exist
DROP TABLE IF EXISTS email_recipient;
DROP TABLE IF EXISTS checklist_item;
DROP TABLE IF EXISTS daily_checklist;
DROP TABLE IF EXISTS template_item;
DROP TABLE IF EXISTS checklist_template;

-- Create tables
CREATE TABLE checklist_template (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE template_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    group_name TEXT NOT NULL,
    item TEXT NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (template_id) REFERENCES checklist_template (id) ON DELETE CASCADE
);

CREATE TABLE daily_checklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed BOOLEAN NOT NULL DEFAULT 0,
    sent BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (template_id) REFERENCES checklist_template (id) ON DELETE CASCADE
);

CREATE TABLE checklist_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checklist_id INTEGER NOT NULL,
    group_name TEXT NOT NULL,
    item TEXT NOT NULL,
    time TEXT,
    status TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (checklist_id) REFERENCES daily_checklist (id) ON DELETE CASCADE
);

CREATE TABLE email_recipient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    active BOOLEAN NOT NULL DEFAULT 1
);

-- Create indexes
CREATE INDEX idx_template_item_template_id ON template_item (template_id);
CREATE INDEX idx_daily_checklist_template_id ON daily_checklist (template_id);
CREATE INDEX idx_daily_checklist_date ON daily_checklist (date);
CREATE INDEX idx_checklist_item_checklist_id ON checklist_item (checklist_id);
