CREATE TABLE census_values (
    year,
    table_id,
    table_name,
    date_name,
    geography_name,
    geography_code,
    geography_type,
    geography_typecode,
    cell,
    cell_name,
    cell_type,
    measures,
    measures_name,
    obs_value,
    obs_status_name,
    UNIQUE(year,table_id,geography_code,cell,measures)
);

CREATE INDEX idx_values_geocode ON census_values(geography_code);
CREATE INDEX idx_values_table_id ON census_values(table_id);
