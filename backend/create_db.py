from db import get_connection

conn, cursor = get_connection()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT CHECK (char_length(username) BETWEEN 3 AND 50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    address TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS tenants (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    phone TEXT,

    monthly_rent NUMERIC(10,2) NOT NULL,

    rent_due_day INTEGER CHECK (
    rent_due_day BETWEEN 1 AND 31
) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS charges (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    charge_type TEXT CHECK (
    charge_type IN (
        'RENT',
        'ELECTRICITY',
        'GAS',
        'WATER',
        'INTERNET',
        'OTHER'
    )
) NOT NULL,

    description TEXT,

    billing_month DATE NOT NULL,

    amount NUMERIC(10,2) CHECK (amount > 0) NOT NULL,

    due_date DATE NOT NULL,

    status TEXT CHECK (
    status IN ('UNPAID', 'PARTIALLY_PAID', 'PAID')
) NOT NULL,

    created_at TIMESTAMP DEFAULT NOW(),

    updated_at TIMESTAMP DEFAULT NOW()
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    charge_id INTEGER NOT NULL REFERENCES charges(id) ON DELETE CASCADE,

    amount NUMERIC(10,2) CHECK (amount > 0) NOT NULL,

    payment_method TEXT CHECK (
    payment_method IN (
        'CASH',
        'BANK_TRANSFER',
        'EASYPAISA',
        'JAZZCASH',
        'OTHER'
    )
),

    payment_date DATE NOT NULL,

    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);
""")


conn.commit()

print("Database schema created successfully.")