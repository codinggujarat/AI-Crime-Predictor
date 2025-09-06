import csv
import random
from datetime import datetime, timedelta
import os

# File path for single combined CSV
combined_csv = os.path.join("data", "crime_data.csv")

# Example data
crime_types = ["Theft", "Burglary", "Assault", "Robbery"]
grid_ids = ["Grid 1", "Grid 2", "Grid 3", "Grid 4"]
officers = [
    "John Smith", "Emily Johnson", "Michael Brown", "Sarah Davis", "David Wilson",
    "Jessica Martinez", "Daniel Anderson", "Laura Thomas", "James Taylor", "Olivia Moore"
]
statuses = ["Open", "Investigating", "Closed"]

# Number of records to generate
num_records = 50

# Generate fake data
combined_rows = []

for i in range(1, num_records + 1):
    crime_type = random.choice(crime_types)
    location = random.choice(grid_ids)
    date_obj = datetime.now() - timedelta(days=random.randint(0, 30))
    date_str = date_obj.strftime("%Y-%m-%d")
    time_str = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"
    latitude = round(random.uniform(12.9000, 13.1000), 6)   # Example lat
    longitude = round(random.uniform(77.5000, 77.7000), 6)  # Example long
    reported_by = random.choice(officers)
    predicted_severity = random.choice(["Low", "Medium", "High"])
    severity_score = random.randint(1, 10)
    status = random.choice(statuses)
    notes = "N/A"

    # Combined CSV row
    combined_rows.append({
        "id": i,
        "type": crime_type,
        "location": location,
        "date": date_str,
        "time": time_str,
        "reported_by": reported_by,
        "predicted_severity": predicted_severity,
        "severity_score": severity_score,
        "status": status,
        "notes": notes,
        "Latitude": latitude,
        "Longitude": longitude,
        "CrimeType": crime_type
    })

# Write combined CSV
with open(combined_csv, "w", newline="", encoding="utf-8") as f:
    fieldnames = [
        "id", "type", "location", "date", "time", "reported_by",
        "predicted_severity", "severity_score", "status", "notes",
        "Latitude", "Longitude", "CrimeType"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(combined_rows)

print(f"Generated {num_records} fake records in:")
print(f"- {combined_csv}")
