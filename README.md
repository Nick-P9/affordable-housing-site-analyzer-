# affordable-housing-site-analyzer-

This project provides a simple, repeatable pipeline for processing and scoring land parcel data in Florida based on proximity to key infrastructure (schools, transit, grocery stores, and medical facilities).

## 🔧 Overview

The project consists of two main scripts:

---

### 1. `UC.py` — Filter by Land Use

Filters a raw property dataset to only include parcels that match specific land use codes (DOR_UC values).

- **Input**: `Osceola County (59), 3.5to10.0 Acre.csv`
- **Output**: `osceola.csv`
- **Logic**: Only includes parcels where the `DOR_UC` field matches one of the following values: `[0, 10, 11, 17, 28, 40]`

---

### 2. `grossPoints.py` — Geographic Enrichment and Scoring

Enriches parcel data with geographic coordinates and scores each property based on nearby community and transit amenities.

- **Input**: `osceola.csv`
- **Output**: `Osceola59Points.csv`

#### Features:
- Geocodes each parcel using OpenStreetMap's Nominatim API
- Identifies nearby:
  - 🏫 Schools
  - 🛒 Grocery stores
  - 🚌 Transit stations & bus stops
  - 🏥 Medical facilities
- Calculates a simple scoring model based on Flordia LIHTC affordable housing program:
  - +1 point for each amenity type within 2 miles
  - Separate totals for **transit** and **community** points
- Adds `LATITUDE`, `LONGITUDE`, `OSM_ADDRESS_LINK`, `GROSS_TRANSIT_POINTS`, `GROSS_COMMUNITY_POINTS` columns

---

## 🗂 Output Columns

The final `Osceola59Points.csv` includes the following:

- **Parcel Info**: `OBJECTID`, `PARCEL_ID`, `LND_VAL`, etc.
- **Address Fields**: `OWN_ADDR1`, `OWN_CITY`, `OWN_ZIPCD`, etc.
- **Geocoded**: `LATITUDE`, `LONGITUDE`, `OSM_ADDRESS_LINK`
- **Scoring**:
  - `GROSS_TRANSIT_POINTS`
  - `GROSS_COMMUNITY_POINTS`

---

## 📦 Requirements

- Python 3.7+
- `pandas`, `requests`, `math`, `re`

Install via pip:

```bash
pip install pandas requests
