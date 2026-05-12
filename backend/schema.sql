
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT,
    icon TEXT,
    sortOrder INTEGER DEFAULT 0,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS spaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    photoUrl TEXT,
    hint TEXT,
    parentId TEXT,
    gridPosition INTEGER DEFAULT 0,
    recentlyOperatedAt DATETIME,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(parentId) REFERENCES spaces(id)
);

CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    categoryId TEXT,
    imageUrl TEXT,
    quantity INTEGER DEFAULT 1,
    spaceId TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'stored', 'taken', 'archived')),
    tags TEXT DEFAULT '[]',
    deadline DATETIME,
    notes TEXT,
    source TEXT DEFAULT 'manual' CHECK(source IN ('manual', 'receipt_import', 'demo')),
    sourceId TEXT,
    lastTakenAt DATETIME,
    lastReturnedAt DATETIME,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(categoryId) REFERENCES categories(id),
    FOREIGN KEY(spaceId) REFERENCES spaces(id)
);

CREATE TABLE IF NOT EXISTS logs (
    id TEXT PRIMARY KEY,
    itemId TEXT,
    actionType TEXT NOT NULL CHECK(actionType IN ('create', 'update', 'move', 'store', 'take', 'return', 'quantity_adjust', 'archive', 'delete')),
    quantityDelta INTEGER,
    fromSpaceId TEXT,
    toSpaceId TEXT,
    fromStatus TEXT,
    toStatus TEXT,
    detail TEXT,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(itemId) REFERENCES items(id)
);

CREATE TABLE IF NOT EXISTS receipt_imports (
    id TEXT PRIMARY KEY,
    originalFilename TEXT,
    imageUrl TEXT NOT NULL,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'confirmed')),
    rawText TEXT,
    draftJson TEXT NOT NULL,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    confirmedAt DATETIME
);

CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);
CREATE INDEX IF NOT EXISTS idx_items_space_id ON items(spaceId);
CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
CREATE INDEX IF NOT EXISTS idx_logs_item_id ON logs(itemId);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(createdAt);
CREATE INDEX IF NOT EXISTS idx_receipt_imports_status ON receipt_imports(status);
