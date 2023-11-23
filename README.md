# Store-Monitoring

## Solution

> Tech Used: Django & Django restframework

### Steps followed

- We create a Report object, with status as "Running"
- The report id of the object, is sent in the response, for future reference.
- Firstly we are fetching all the unique store ids using the Store Status Logs, keeping the logs as the **source of truth**.
- We are also keeping a **max_time** which will be the maximum timestamp in the status log file.
- Now we will loop through the store ids.
- For each store id, we will calculate the uptime/downtime data for last hour, last day, and last week.
- We will fetch the business hours for that store id, and convert the data into a dictionary with the key as **day_of_week** and the value will be a dictionary with data of **start_time** and **end_time**.
  > eg:{
  > "a": {
  > "start_time_local": "timestamp",
  >  "end_time_local": "timestamp"
  >}
  >}
- If no data is found for a store, then it means that the store is open 24/7.
- Now, for calculating the data, we will first fetch all the status logs for a store within the time difference (1 hour, 1 day and 7 days respectively).
- Now we will process these logs in batches (I have taken batch size as 1000, as the data may be huge)
- For each log, we will first convert the UTC log timestamp to the local time, and check if the log is within the business hours of store.
- If the log is in business hours, we will calculate the data as follows:
  - If the log status is active, we will update the uptime by 60 (if unit is in minutes) or 1 (if unit is in hours)
  - If the log status is inactive, we will update the downtime by 60 (if unit is in minutes) or 1 (if unit is in hours)
- If the log is not within business hours, we will discard this data, as it is not required according to the problem statement.
- After gathering all the data, we combine the data into a json, and then create a csv file locally, which will be sent later on.
- After all the steps are completed without any exception, we change the status of the report to "Completed".

## Improvements we can do

- Use Celery for report generation, which will not block the main thread. This will also reduce the response time of the trigger_report endpoint, as everything will be working in the background.
- I have created scripts in helpers.py to inject data in the DB, but that can be improved using threads (I dont have much knowledge in this).

## Endpoint curls

1. curl --location --request POST 'http://127.0.0.1:8000/trigger_report'

2. curl --location --request GET 'http://127.0.0.1:8000/get_report?report_id=1946b531-f4f7-452f-a073-6f0bbf116beb'

