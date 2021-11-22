#!/bin/bash

set -euo pipefail

sqlite3 big-census.db < create-db.sql
