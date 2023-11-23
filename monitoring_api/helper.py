import csv

from .models import BusinessHours, Store, StoreStatus, StoreStatusLog

with open("data/business_hours.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    i = 0
    for row in reader:
        print(row)
        store_id = store_id = row["store_id"]
        store_timing = BusinessHours.objects.create(
            store_id=store_id,
            day_of_week=row["day"],
            start_time_local=row["start_time_local"],
            end_time_local=row["end_time_local"],
        )
        print(store_timing)
        if i == 5000:
            break
        i += 1

row = None

with open("data/store_tz.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    i = 0
    for row in reader:
        print(row)
        Store.objects.create(
            id=row["store_id"],
            timezone_str=row["timezone_str"],
        )
        if i == 500:
            break
        i += 1

row = None

with open("data/store_status_logs.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    i = 0
    for row in reader:
        print(row)
        StoreStatusLog.objects.create(
            store_id=row["store_id"],
            status=StoreStatus.ACTIVE
            if row["status"] == "inactive"
            else StoreStatus.ACTIVE,
            timestamp=row["timestamp_utc"][: len(row["timestamp_utc"]) - 4],
        )
        if i == 500:
            break
        i += 1
