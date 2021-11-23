CREATE TABLE IF NOT EXISTS census_tables (
    table_id UNIQUE,
    table_name,
    year integer
);

CREATE TABLE IF NOT EXISTS census_cells (
    table_id,
    cell_id integer,
    cell_name,
    UNIQUE(table_id, cell_id)
);

CREATE TABLE IF NOT EXISTS census_values (
    year integer,
    table_id,
    date_name,
    geography_name,
    geography_code,
    geography_typecode,
    cell integer,
    cell_type,
    measures integer,
    measures_name,
    obs_value,
    obs_status_name,
    UNIQUE(year,table_id,geography_code,cell,measures)
);

CREATE INDEX idx_cells ON census_cells(table_id, cell_id);
CREATE INDEX idx_tables_id ON census_tables(table_id);
CREATE INDEX idx_values_geocode ON census_values(geography_code);
CREATE INDEX idx_values_table_id ON census_values(table_id);
