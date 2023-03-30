from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# กำหนดข้อมูลการเชื่อมต่อ InfluxDB

url = "http://172.25.10.14:8086/"
token = "my-super-secret-auth-token"
org = "eng.rmuti"
bucket = "my_bucket"
client = InfluxDBClient(url=url, token=token, org=org, bucket=bucket)
try:
    client.ping()
    print("Connected to InfluxDB!")
except Exception as e:
    print("Failed to connect to InfluxDB:", e)

#
#
# url = "https://<influxdb_host>:<influxdb_port>"
# org = "<influxdb_org>"
# token = "<influxdb_bucket_token>"
# bucket = "<influxdb_database_name>/<influxdb_bucket_name>

# สร้าง query โดยระบุ Measurement ที่ต้องการ
query = f'from(bucket:"{bucket}") \
              |> range(start: -1m) \
              |> filter(fn: (r) => r._measurement == "kbide") \
              |> filter(fn: (r) => r._field == "TEMP") \
             '

tables = client.query_api().query(query, org=org)

# แสดงผลข้อมูล
for table in tables:
    for record in table.records:
        result = record.values['_value']
        print(result)

