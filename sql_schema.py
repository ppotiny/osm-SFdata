# Schema for OSM csv import to database

# This code was sourced from:
# https://gist.github.com/swwelch/f1144229848b407e0a5d13fcb7fbbd6f

schema_keys = {'nodes': ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp', 'type'],
               'nodes_tags': ['id', 'key', 'value', 'type'],
               'ways': ['id', 'user', 'uid', 'version', 'changeset', 'timestamp', 'type'],
               'ways_tags': ['id', 'key', 'value', 'type'],
               'ways_nodes': ['id', 'node_id', 'position', 'type']}

nodes = """CREATE TABLE IF NOT EXISTS nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
);"""

nodes_tags = """CREATE TABLE IF NOT EXISTS nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
);"""

ways = """CREATE TABLE IF NOT EXISTS ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
);"""

ways_tags = """CREATE TABLE IF NOT EXISTS ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);"""

ways_nodes = """CREATE TABLE IF NOT EXISTS ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);"""