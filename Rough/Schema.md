-- Required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS postgis;     -- spatial types & indexes

-- ENUMs
CREATE TYPE trip_status AS ENUM ('draft','scheduled','active','completed','cancelled');
CREATE TYPE privacy_level AS ENUM ('public','private','invite_only');
CREATE TYPE trip_type AS ENUM ('personal','meetup','city_tour','event','guided');
CREATE TYPE rsvp_status AS ENUM ('invited','pending','confirmed','declined','cancelled');
CREATE TYPE itinerary_status AS ENUM ('draft','finalized','archived');
CREATE TYPE booking_type AS ENUM ('flight','train','hotel','restaurant','activity','other');

--------------------------------------------------------------------
-- Core: Users
--------------------------------------------------------------------
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,                 -- hashed with bcrypt/scrypt/argon2
  phone TEXT,
  locale VARCHAR(10) DEFAULT 'en',
  timezone TEXT,                               -- e.g. 'Asia/Kolkata'
  profile_picture TEXT,                        -- URL or storage key
  bio TEXT,
  is_email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  last_login TIMESTAMPTZ
);
CREATE INDEX idx_users_email ON users(email);

--------------------------------------------------------------------
-- User preferences (1:1 with users)
--------------------------------------------------------------------
CREATE TABLE user_preferences (
  user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
  preferred_languages TEXT[],       -- e.g. ['en','hi']
  interest_tags TEXT[],             -- free-form tags for quick preference filtering
  budget_min NUMERIC(10,2),
  budget_max NUMERIC(10,2),
  currency VARCHAR(8) DEFAULT 'USD',
  transport_preference TEXT[],      -- e.g. ['walking','bike','car','public_transit']
  pace VARCHAR(20),                 -- relaxed, balanced, fast
  accessibility_needs TEXT[],       -- wheelchair, stroller, low_light
  notification_preferences JSONB,   -- email/push toggles
  home_location GEOGRAPHY(POINT,4326), -- optional home point
  metadata JSONB,                   -- any extra stuff
  updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_userprefs_interest_tags ON user_preferences USING gin(interest_tags);
CREATE INDEX idx_userprefs_langs_gin ON user_preferences USING gin(preferred_languages);

--------------------------------------------------------------------
-- Normalized Interests (master list) & user -> interest mapping
--------------------------------------------------------------------
CREATE TABLE interests (
  interest_id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,        -- 'heritage', 'food', 'nature', etc
  description TEXT,
  category TEXT,
  icon TEXT
);

CREATE TABLE user_interests (
  user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
  interest_id INT REFERENCES interests(interest_id) ON DELETE CASCADE,
  weight SMALLINT DEFAULT 1,        -- user's personal weight/priority
  created_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, interest_id)
);

--------------------------------------------------------------------
-- Points of Interest (POIs) - core map entities
--------------------------------------------------------------------
CREATE TABLE poi_categories (
  category_id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  parent_id INT REFERENCES poi_categories(category_id)
);

CREATE TABLE pois (
  poi_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  external_source TEXT,             -- e.g. 'google_places', 'osm', 'yelp'
  external_id TEXT,                 -- external provider id
  name TEXT NOT NULL,
  short_description TEXT,
  category_id INT REFERENCES poi_categories(category_id),
  location GEOGRAPHY(POINT,4326) NOT NULL,  -- lat/lon
  city TEXT,
  region TEXT,
  country TEXT,
  address TEXT,
  phone TEXT,
  website TEXT,
  avg_visit_duration INTERVAL,      -- e.g. '01:00:00'
  price_level SMALLINT,             -- 0..4 like google
  rating_avg NUMERIC(3,2),
  rating_count INT DEFAULT 0,
  opening_hours JSONB,              -- flexible format
  attributes JSONB,                 -- e.g. cuisine, tags, wheelchair
  metadata JSONB,                   -- raw provider payload
  last_synced TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Spatial index for map queries:
CREATE INDEX poi_location_gist ON pois USING GIST(location);

-- Quick search index (text search)
ALTER TABLE pois ADD COLUMN tsv tsvector;
-- populate tsv with trigger in production; index:
CREATE INDEX poi_tsv_gin ON pois USING GIN(tsv);

-- helpful GIN for metadata
CREATE INDEX poi_metadata_gin ON pois USING GIN(metadata);

--------------------------------------------------------------------
-- Saved places / favorites
--------------------------------------------------------------------
CREATE TABLE saved_places (
  saved_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
  poi_id UUID REFERENCES pois(poi_id) ON DELETE CASCADE,
  label TEXT,                        -- e.g. "Anniversary dinner"
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_saved_user ON saved_places(user_id);

--------------------------------------------------------------------
-- Trips (local meetups, city tours, personal trips)
--------------------------------------------------------------------
CREATE TABLE trips (
  trip_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
  title TEXT,
  description TEXT,
  trip_type trip_type DEFAULT 'personal',
  city TEXT,
  region TEXT,
  country TEXT,
  center_location GEOGRAPHY(POINT,4326),   -- optional meetup center
  meetup_radius_meters INT,                -- if meetup: radius that defines "nearby"
  start_date DATE,
  end_date DATE,
  status trip_status DEFAULT 'draft',
  privacy privacy_level DEFAULT 'private',
  capacity INT,                            -- max attendees (for meetups)
  price_estimate NUMERIC(10,2),
  currency VARCHAR(10) DEFAULT 'USD',
  cover_photo TEXT,                        -- URL / key
  tags TEXT[],                             -- quick tags for filtering
  extra JSONB,                             -- flexible data (e.g., agenda preview)
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_trips_city ON trips(city);
CREATE INDEX idx_trips_tags_gin ON trips USING gin(tags);

--------------------------------------------------------------------
-- Trip Attendees / RSVPs (for meetups & local events)
--------------------------------------------------------------------
CREATE TABLE trip_attendees (
  trip_id UUID REFERENCES trips(trip_id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
  rsvp rsvp_status DEFAULT 'pending',
  is_confirmed BOOLEAN DEFAULT FALSE,
  joined_at TIMESTAMPTZ,
  note TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (trip_id, user_id)
);

CREATE INDEX idx_trip_attendee_status ON trip_attendees(trip_id, rsvp);

--------------------------------------------------------------------
-- Itineraries: versioned (history) + entries
--------------------------------------------------------------------
CREATE TABLE itinerary_versions (
  itinerary_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id UUID REFERENCES trips(trip_id) ON DELETE CASCADE,
  created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  name TEXT,
  version_number INT NOT NULL DEFAULT 1,
  status itinerary_status DEFAULT 'draft',
  is_current BOOLEAN DEFAULT FALSE,     -- indicates the active (latest) version
  notes TEXT,
  metadata JSONB
);
CREATE UNIQUE INDEX ux_itinerary_trip_version ON itinerary_versions(trip_id, version_number);

CREATE TABLE itinerary_entries (
  entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  itinerary_id UUID REFERENCES itinerary_versions(itinerary_id) ON DELETE CASCADE,
  poi_id UUID REFERENCES pois(poi_id),
  day INT,                              -- day number relative to trip start (1..n)
  order_index INT,                      -- order within that day
  start_time TIMESTAMPTZ,
  end_time TIMESTAMPTZ,
  transport_mode TEXT,
  estimated_travel_time INTERVAL,
  estimated_cost NUMERIC(10,2),
  notes TEXT,
  location_override GEOGRAPHY(POINT,4326), -- allow manual override location
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_itin_by_trip ON itinerary_versions(trip_id);
CREATE INDEX idx_itin_entries_itin ON itinerary_entries(itinerary_id);

--------------------------------------------------------------------
-- Trip Journal & Media
--------------------------------------------------------------------
CREATE TABLE trip_journals (
  journal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id UUID REFERENCES trips(trip_id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
  title TEXT,
  entry_text TEXT,
  day INT,                              -- optional
  location GEOGRAPHY(POINT,4326),
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE media (
  media_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
  trip_id UUID REFERENCES trips(trip_id) ON DELETE CASCADE,
  ref_type TEXT,                        -- 'journal','itinerary_entry','poi'...
  ref_id UUID,
  url TEXT NOT NULL,
  mime_type TEXT,
  width INT,
  height INT,
  size_bytes BIGINT,
  exif JSONB,
  location GEOGRAPHY(POINT,4326),
  taken_at TIMESTAMPTZ,
  uploaded_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_media_trip ON media(trip_id);
CREATE INDEX idx_media_owner ON media(owner_user_id);

--------------------------------------------------------------------
-- Bookings (flights/hotels/activities linked to trips)
--------------------------------------------------------------------
CREATE TABLE bookings (
  booking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id UUID REFERENCES trips(trip_id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
  type booking_type,
  provider TEXT,
  provider_reference TEXT,
  cost NUMERIC(12,2),
  currency VARCHAR(8) DEFAULT 'USD',
  start_time TIMESTAMPTZ,
  end_time TIMESTAMPTZ,
  status TEXT,
  raw_payload JSONB,      -- raw response from provider
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_bookings_trip ON bookings(trip_id);

--------------------------------------------------------------------
-- Reviews & Ratings (user feedback for POIs or trips)
--------------------------------------------------------------------
CREATE TABLE reviews (
  review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
  poi_id UUID REFERENCES pois(poi_id) ON DELETE CASCADE,
  trip_id UUID REFERENCES trips(trip_id) ON DELETE CASCADE,
  rating SMALLINT CHECK (rating >= 1 AND rating <= 5),
  title TEXT,
  body TEXT,
  photos JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_reviews_poi ON reviews(poi_id);

--------------------------------------------------------------------
-- Routes cache (store computed routes for reuse)
--------------------------------------------------------------------
CREATE TABLE routes (
  route_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin GEOGRAPHY(POINT,4326),
  destination GEOGRAPHY(POINT,4326),
  polyline GEOGRAPHY(LINESTRING,4326),
  transport_mode TEXT,
  distance_meters NUMERIC,
  duration_seconds INT,
  computed_by UUID REFERENCES users(user_id),
  params JSONB,          -- routing parameters (avoid_restricted, preferences)
  created_at TIMESTAMPTZ DEFAULT now(),
  last_used_at TIMESTAMPTZ
);
CREATE INDEX idx_routes_origin ON routes USING gist(origin);
CREATE INDEX idx_routes_dest ON routes USING gist(destination);

CREATE TABLE route_legs (
  leg_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  route_id UUID REFERENCES routes(route_id) ON DELETE CASCADE,
  leg_index INT,
  start_location GEOGRAPHY(POINT,4326),
  end_location GEOGRAPHY(POINT,4326),
  distance_meters NUMERIC,
  duration_seconds INT,
  instruction TEXT
);

--------------------------------------------------------------------
-- Search history, activity logging, notifications
--------------------------------------------------------------------
CREATE TABLE search_history (
  search_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
  query TEXT,
  params JSONB,
  result_count INT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE activity_logs (
  log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(user_id),
  action TEXT,
  entity_type TEXT,
  entity_id UUID,
  payload JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE notifications (
  notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
  channel TEXT,         -- 'push', 'email', 'sms'
  title TEXT,
  body TEXT,
  data JSONB,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now()
);

--------------------------------------------------------------------
-- Helpful indexes & maintenance hints
--------------------------------------------------------------------
-- Full text population example (application should keep it in sync):
-- UPDATE pois SET tsv = to_tsvector('english', coalesce(name,'') || ' ' || coalesce(short_description,'') || ' ' || coalesce(address,''));

-- GIN/GIN-like indexes already included where helpful (arrays, jsonb, tsvector, postgis gist).
