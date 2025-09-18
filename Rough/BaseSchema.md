-- Only 6 core tables

-- 1. Users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    timezone TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. User Preferences
CREATE TABLE user_preferences (
    pref_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    budget_min INT,
    budget_max INT,
    transport_pref TEXT,       -- e.g. car, train, walking
    pace TEXT,                 -- relaxed, fast, balanced
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. User Interests
CREATE TABLE user_interests (
    interest_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    tag TEXT NOT NULL           -- e.g. 'heritage', 'food', 'nature'
);

-- 4. Trips
CREATE TABLE trips (
    trip_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    title TEXT,
    city TEXT,
    start_date DATE,
    end_date DATE,
    status TEXT DEFAULT 'draft',   -- draft, active, completed
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Itineraries
CREATE TABLE itineraries (
    itinerary_id SERIAL PRIMARY KEY,
    trip_id INT REFERENCES trips(trip_id) ON DELETE CASCADE,
    day INT,
    order_index INT,
    poi_name TEXT,               -- name of the place/POI
    poi_address TEXT,            -- optional
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. Trip Journals
CREATE TABLE trip_journals (
    journal_id SERIAL PRIMARY KEY,
    trip_id INT REFERENCES trips(trip_id) ON DELETE CASCADE,
    day INT,
    entry_text TEXT,
    photos JSONB,                 -- store URLs or metadata
    created_at TIMESTAMP DEFAULT NOW()
);
