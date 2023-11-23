import csv
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from pytz import timezone as pytz_timezone

from .models import (
    BusinessHours,
    Report,
    ReportStatus,
    Store,
    StoreStatus,
    StoreStatusLog,
)

ONE_HOUR = 1 * 1
ONE_DAY = 24 * 1
ONE_WEEK = 24 * 7 * 1

HOUR = "hours"
MINUTES = "minutes"


def trigger_report_generation(report_id):
    csv_data = []

    # we will query stores based on batch size, assuming there are huge number of stores.
    batch_size = 1000
    unique_store_ids = set()

    # hard coding current time as max of all the logs
    max_time = StoreStatusLog.objects.all().order_by("-timestamp").first().timestamp

    try:
        for offset in range(0, StoreStatusLog.objects.count(), batch_size):
            batch = StoreStatusLog.objects.values_list(
                "store_id", flat=True
            ).distinct()[offset : offset + batch_size]
            unique_store_ids.update(batch)

        for store_id in unique_store_ids:
            store_data = generate_report_data_for_a_store(
                store_id=store_id, max_time=max_time
            )
            csv_data.append(store_data)

        generate_csv_file(report_id, csv_data)
    except Exception as e:
        # add logger here later on for debugging purpose
        print(e)
        report = Report.objects.get(id=report_id)
        report.status = ReportStatus.FAILED


def generate_report_data_for_a_store(store_id, max_time):
    tz = get_store_timezone(store_id)
    target_timezone = pytz_timezone(tz)

    utc_timezone = pytz_timezone("UTC")
    utc_time = max_time.astimezone(utc_timezone)

    # last one hour
    last_one_hour_data = get_uptime_downtime_data(
        store_id, utc_time, target_timezone, ONE_HOUR, MINUTES
    )
    # last one day
    last_one_day_data = get_uptime_downtime_data(
        store_id, utc_time, target_timezone, ONE_DAY, HOUR
    )

    # last one week
    last_one_week_data = get_uptime_downtime_data(
        store_id, utc_time, target_timezone, ONE_WEEK, HOUR
    )
    json_data = {
        "store_id": store_id,
        "last_one_hour_uptime": last_one_hour_data["uptime"],
        "last_one_hour_downtime": last_one_hour_data["downtime"],
        "last_one_hour_unit": last_one_hour_data["unit"],
        "last_one_day_uptime": last_one_day_data["uptime"],
        "last_one_day_downtime": last_one_day_data["downtime"],
        "last_one_day_unit": last_one_day_data["unit"],
        "last_one_week_uptime": last_one_week_data["uptime"],
        "last_one_week_downtime": last_one_week_data["downtime"],
        "last_one_week_unit": last_one_week_data["unit"],
    }
    return json_data


def generate_csv_file(report_id, csv_data):
    file_name = f"data/{report_id}.csv"

    with open(file_name, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            [
                "store_id",
                "last_one_hour uptime",
                "last_one_hour downtime",
                "last_one_hour unit",
                "last_one_day uptime",
                "last_one_day downtime",
                "last_one_day unit",
                "last_one_week uptime",
                "last_one_week downtime",
                "last_one_week unit",
            ]
        )
        for data in csv_data:
            csv_writer.writerow(
                [
                    data["store_id"],
                    data["last_one_hour_uptime"],
                    data["last_one_hour_downtime"],
                    data["last_one_hour_unit"],
                    data["last_one_day_uptime"],
                    data["last_one_day_downtime"],
                    data["last_one_day_unit"],
                    data["last_one_week_uptime"],
                    data["last_one_week_downtime"],
                    data["last_one_week_unit"],
                ]
            )
    report = Report.objects.get(id=report_id)
    report.status = ReportStatus.COMPLETED
    report.save()


def get_uptime_downtime_data(
    store_id, utc_time, store_tz, timegap_in_hours: int, unit: str
):
    data = {"uptime": 0, "downtime": 0, "unit": unit}
    business_hours = get_store_business_hours(store_id)

    # getting all the logs in the time gap
    all_logs_in_the_time_gap = StoreStatusLog.objects.filter(
        timestamp__gte=utc_time - timedelta(hours=timegap_in_hours), store_id=store_id
    ).order_by("timestamp")

    batch_size = 1000

    for log in all_logs_in_the_time_gap.iterator(chunk_size=batch_size):
        # checkig if log is in store business hours
        log_ts = log.timestamp
        local_time = log_ts.astimezone(store_tz)

        # Converting utc time to local for comparision of log time with business hours
        log_is_in_business_hours = is_within_business_hours(local_time, business_hours)

        # checking if log is in store business hours and status is active
        if not log_is_in_business_hours:
            continue

        if log.status == StoreStatus.ACTIVE:
            data["uptime"] += 60 if unit == MINUTES else 1
        else:
            data["downtime"] += 60 if unit == MINUTES else 1
    return data


def get_store_timezone(store_id):
    try:
        store = Store.objects.get(id=store_id)
        return store.timezone_str
    except ObjectDoesNotExist:
        return "America/Chicago"


def get_store_business_hours(store_id):
    store_business_hours = BusinessHours.objects.filter(store_id=store_id).all()

    # If the store is open 24/7, consider all hours as business hours
    if not store_business_hours:
        return None
    business_hours = {}
    for bh in store_business_hours:
        business_hours[bh.day_of_week] = {
            "start_time_local": bh.start_time_local,
            "end_time_local": bh.end_time_local,
        }
    return business_hours


def is_within_business_hours(store_timestamp, business_hours: dict):
    # Check if the timestamp is within the specified business hours for the store
    if not business_hours:  # If no business hours is present, it means it is open 24/7
        return True

    day_of_week = store_timestamp.weekday()
    business_hours_entry = business_hours.get(day_of_week)

    if business_hours_entry:
        start_time = business_hours_entry["start_time_local"]
        end_time = business_hours_entry["end_time_local"]
        return (
            start_time <= store_timestamp.time() and store_timestamp.time() <= end_time
        )
    return False
