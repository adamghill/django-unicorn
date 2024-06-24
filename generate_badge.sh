#!/bin/sh
poetry run coverage run -m pytest
poetry run coverage xml
poetry run genbadge coverage -i coverage.xml -o badges/coverage.svg
