-- Enable UUID generation functions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================
-- USERS TABLE
-- ==============================
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- USER DETAILS (1:1 with USERS)
-- ==============================
CREATE TABLE user_details (
    user_id UUID PRIMARY KEY,
    dob DATE,
    gender VARCHAR(20),
    aadhar_number VARCHAR(20),
    passport_number VARCHAR(20),
    driving_license_number VARCHAR(20),
    spoken_languages TEXT[],
    understood_languages TEXT[],
    native_language VARCHAR(50),
    hometown VARCHAR(100),
    current_city VARCHAR(100),
    address TEXT,
    phone_number VARCHAR(20),
    home_lat DECIMAL(9,6),
    home_lng DECIMAL(9,6),
    dietary_preferences TEXT[],
    CONSTRAINT fk_userdetails_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==============================
-- TRAVEL PREFERENCES (1:N with USERS)
-- ==============================
CREATE TABLE travel_preferences (
    pref_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    budget_min NUMERIC(10,2),
    budget_max NUMERIC(10,2),
    transport_pref VARCHAR(50),
    commute_pref VARCHAR(50),
    pace VARCHAR(20),
    travel_duration_preference VARCHAR(50),
    travel_group_preference VARCHAR(50),
    preferred_regions TEXT[],
    season_preference VARCHAR(50),
    accommodation_type VARCHAR(50),
    special_needs TEXT,
    frequent_travel BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_travelprefs_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==============================
-- USER INTERESTS (1:N with USERS)
-- ==============================
CREATE TABLE user_interests (
    interest_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    tag VARCHAR(100),
    sub_tag VARCHAR(100),
    preferred_vacation_type VARCHAR(50),
    activity_type VARCHAR(100),
    frequency_of_interest VARCHAR(50),
    special_notes TEXT,
    CONSTRAINT fk_userinterests_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==============================
-- TRIPS TABLE
-- ==============================
CREATE TABLE trips (
    trip_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    trip_type VARCHAR(50),
    total_budget NUMERIC(10,2),
    transport_mode_to_city VARCHAR(50),
    accommodation_type VARCHAR(50),
    tags JSONB,
    rating NUMERIC(3,2),
    favorite_locations JSONB
);

-- ==============================
-- TRIP JOURNALS TABLE
-- ==============================
CREATE TABLE trip_journals (
    journal_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL REFERENCES trips(trip_id) ON DELETE CASCADE,
    day INT,
    entry_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location JSONB,
    tags JSONB,
    expenses JSONB,
    visited_places JSONB,
    recommended_for_next_time TEXT,
    mood VARCHAR(50),
    travel_companions JSONB,
    transportation_used JSONB,
    summary_generated TEXT,
    recommendations_generated TEXT
);

-- ==============================
-- ITINERARIES TABLE
-- ==============================
CREATE TABLE itineraries (
    itinerary_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL REFERENCES trips(trip_id) ON DELETE CASCADE,
    days INT,
    pois JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
