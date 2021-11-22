#!/usr/bin/env python
# coding: utf-8

import csv
import os
import json
import sqlite3
import sys

from census.cache import get_page

api_codelist_url = "https://www.nomisweb.co.uk/api/v01/dataset/{DATASET}/{CELL}.def.sdmx.json"
api_data_url = "https://www.nomisweb.co.uk/api/v01/dataset/{DATASET}.data.csv?date=latest&geography={GEO_TYPES}&{CELL}={CELLS}&measures={MEASURES}&select=date_name,geography_name,geography_code,geography_type,geography_typecode,{CELL},{CELL}_name,{CELL}_type,measures,measures_name,obs_value,obs_status_name?uid={UID}"
geo_types_2011 = "TYPE464,TYPE480,TYPE499"
record_limit = 100000

p = get_page('https://www.nomisweb.co.uk/api/v01/dataset/def.sdmx.json')

dataset_defs = json.loads(p)

keyfamilies = dataset_defs["structure"]["keyfamilies"]["keyfamily"]

def is_correct_year(keyfamily, year):
    annotations = keyfamily["annotations"]["annotation"]
    for a in annotations:
        if (
            a["annotationtitle"] == "contenttype/sources" and
            "census_{}".format(year) in a["annotationtext"]
        ):
            return True
    return False

def filtered_by_year(keyfamilies, year):
    return [f for f in keyfamilies if is_correct_year(f, year)]

def check_expected_dimensions(dims):
    if len(dims) != 4:
        return False
    for dim in ['GEOGRAPHY', 'MEASURES', 'FREQ']:
        if dim not in dims:
            return False
    return True

def get_cell_dim(dims):
    for dim in dims:
        if dim not in ['GEOGRAPHY', 'MEASURES', 'FREQ']:
            return dim

def get_codes_from_nomis_api(table_code, codelist_name):
    url = api_codelist_url.format(DATASET=table_code, CELL=codelist_name)
    codes = [
        code["value"] for code in
        json.loads(get_page(url))["structure"]["codelists"]["codelist"][0]["code"]
    ]
    return codes

def get_csvs_and_add_to_db(year, table_code, table_name, cell_dim, cell_codes, measure_codes, cur, con):
    sql = '''INSERT OR IGNORE INTO census_values (
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
        obs_status_name
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    record_offset = 0
    while True:
        url = api_data_url.format(
            DATASET=table_code,
            GEO_TYPES=geo_types_2011,
            CELL=cell_dim,
            CELLS=cell_codes,
            MEASURES=measure_codes,
            UID=os.environ['NOMIS_UID']
        ) + '&RecordLimit={}&RecordOffset={}'.format(record_limit, record_offset)
        dataset_csv = get_page(url)
        lines = dataset_csv.splitlines()
        db_lines = []
        for i, line in enumerate(csv.reader(lines)):
            if i == 0:
                continue
            db_line = [year, table_code, table_name] + line
            db_line = [None if item == "" else item for item in db_line]
            db_lines.append(db_line)
        cur.executemany(sql, db_lines)
        if i == 0:
            break   # No records returned in this CSV, so we're done.
        record_offset += record_limit
    con.commit()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    # https://stackoverflow.com/a/312464/3347737
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def add_dataset_to_db(ds, year, cur, con):
    table_code = ds["id"]
    print(table_code)
    table_name = ds["name"]["value"]
    dims = [d["conceptref"] for d in ds["components"]["dimension"]]
    if not check_expected_dimensions(dims):
        print("Skipping {}; unexpected dimensions.".format(table_name))
        return
    cell_dim = get_cell_dim(dims)

    measure_codes = ",".join(str(c) for c in get_codes_from_nomis_api(table_code, 'MEASURES'))
    cell_codes = get_codes_from_nomis_api(table_code, cell_dim)

    for cell_codes_chunk in chunks(cell_codes, 10):
        get_csvs_and_add_to_db(year, table_code, table_name, cell_dim, ",".join(str(c) for c in cell_codes_chunk), measure_codes, cur, con)

def main():
    con = sqlite3.connect('big-census.db')
    cur = con.cursor()

    datasets_uv_ks_2001 = [
        ds for ds in filtered_by_year(keyfamilies, 2001)
        if (
            ds["name"]["value"][:2] == "UV" or
            ds["name"]["value"][:2] == "KS"
        )
    ]
    for ds in datasets_uv_ks_2001:
        add_dataset_to_db(ds, 2001, cur, con)

    dataset_lbs_1991 = [
        ds for ds in filtered_by_year(keyfamilies, 1991)
        if ds["name"]["value"] == "1991 census - local base statistics"
    ][0]
    add_dataset_to_db(dataset_lbs_1991, 1991, cur, con)

    con.close()

if __name__ == "__main__":
    main()
