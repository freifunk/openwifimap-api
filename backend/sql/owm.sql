CREATE EXTENSION IF NOT EXISTS earthdistance CASCADE;

CREATE TABLE nodes (
    id VARCHAR PRIMARY KEY,
    hostname VARCHAR NOT NULL,
    lat double precision NOT NULL,
    lng double precision NOT NULL,
    links VARCHAR NOT NULL,
    ctime TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    mtime TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX idx_nodes_id ON nodes (id);
CREATE INDEX idx_nodes_lat ON nodes (lat);
CREATE INDEX idx_nodes_lng ON nodes (lng);
CREATE INDEX idx_nodes_mtime ON nodes (mtime);
CREATE INDEX idx_nodes_location ON nodes USING gist (ll_to_earth(lat, lng));
