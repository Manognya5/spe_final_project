import requests
import psycopg2
import os
import logging
import json
from datetime import datetime

# Fetch API URL from environment variable
api_key = '579b464db66ec23bdd0000012480e2afea3a46d35bcad4d927ee3849'

# --- Database credentials from environment variables ---
db_host = os.getenv("DB_HOST", "postgres-service") 
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")


def fetch_and_store():
    states_cities = [["West_Bengal", "Kolkata"], ["Karnataka", "Bengaluru"], ["Delhi", "Delhi"]]
    limit = 1000
    preprocessed = {"Kolkata": dict(), "Bengaluru": dict(), "Delhi": dict()}
    preprocessed_stations = {"Kolkata": [], "Bengaluru": [], "Delhi": []}
    last_updated = ""

    for state, city in states_cities:
        API_URL = (
            f"https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
            f"?api-key={api_key}&format=json&limit={limit}&filters%5Bstate%5D={state}&filters%5Bcity%5D={city}"
        )
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            print(f"{city}: total={data['total']}, limit={data['limit']}, count={data['count']}, offset={data['offset']}")

            for entry in data['records']:
                station = entry['station']
                pollutant = entry['pollutant_id']
                if station in preprocessed[city]:
                    preprocessed[city][station].update({
                        f"{pollutant}_max": entry['max_value'],
                        f"{pollutant}_min": entry['min_value'],
                        f"{pollutant}_avg": entry['avg_value'],
                    })
                else:
                    
                    preprocessed_stations[city].append(station)
                    
                    preprocessed[city][station] = {
                        "last_updated": entry.get("last_update", None),
                        f"{pollutant}_max": entry['max_value'],
                        f"{pollutant}_min": entry['min_value'],
                        f"{pollutant}_avg": entry['avg_value'],
                    }
                    print(last_updated)
        else:
            print(f"Failed to fetch data for {city}. Status code: {response.status_code}")
            continue

    # # Save for debugging if needed
    with open("output.json", "w") as f:
        json.dump(preprocessed, f, indent=4)
    # --- Connect to PostgreSQL ---
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host
        )
        cursor = conn.cursor()
        print("Connected to database.")

        # --- Insert data into PostgreSQL ---
        count = 0
        for city, stations in preprocessed.items():
            for station, values in stations.items():
                state = next(s for s, c in states_cities if c == city)

                print("last here", last_updated, state)
                raw_date = values.get("last_updated")
                try:
                    last_updated = datetime.strptime(raw_date, "%d-%m-%Y %H:%M:%S") if raw_date else None
                except Exception as e:
                    print(f"Date parsing failed for {raw_date}: {e}")
                    last_updated = None

                insert_query = """
                INSERT INTO aqi_data_24hr (
                    state, city, station, last_updated,
                    PM10_max, PM10_min, PM10_avg,
                    PM2_max, PM2_min, PM2_avg,
                    NO2_max, NO2_min, NO2_avg,
                    NH3_min, NH3_max, NH3_avg,
                    SO2_min, SO2_max, SO2_avg,
                    CO_min, CO_max, CO_avg,
                    OZONE_min, OZONE_max, OZONE_avg
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
                ON CONFLICT (city, last_updated, station) DO NOTHING;
                """

                # Prepare values — safely get each field or None
                row_values = (
                    state, city, station, last_updated,
                    values.get("PM10_max"), values.get("PM10_min"), values.get("PM10_avg"),
                    values.get("PM2_max"), values.get("PM2_min"), values.get("PM2_avg"),
                    values.get("NO2_max"), values.get("NO2_min"), values.get("NO2_avg"),
                    values.get("NH3_min"), values.get("NH3_max"), values.get("NH3_avg"),
                    values.get("SO2_min"), values.get("SO2_max"), values.get("SO2_avg"),
                    values.get("CO_min"), values.get("CO_max"), values.get("CO_avg"),
                    values.get("OZONE_min"), values.get("OZONE_max"), values.get("OZONE_avg"),
                )

                cursor.execute(insert_query, row_values)
                count += 1

        conn.commit()
        print(f"Data {count} inserted into database successfully.")
        cursor.close()
        conn.close()

    except Exception as e:
        print("Database error:", e)

if __name__ == "__main__":
    fetch_and_store()
