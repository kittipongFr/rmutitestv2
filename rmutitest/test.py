from influxdb_client import InfluxDBClient
import pexpect
print(pexpect.__version__)
host = 'vpn.kkc.rmuti.ac.th'
username = 'kittipong.pa'
password = '081244fr'

child = pexpect.spawn('sudo xl2tpd', logfile=None)

child.expect('pppd\[\d+\]: .*')
child.sendline('c')
child.expect('Enter username for '+host+':')
child.sendline(username)
child.expect('Enter password for '+username+'@'+host+':')
child.sendline(password)
child.expect('Connection established to '+host+',', timeout=60)
print('Connected to VPN')



url = "http://172.25.10.14:8086/"
token = "my-super-secret-auth-token"
org = "eng.rmuti"
bucket = "envmon_bucket"
client = InfluxDBClient(url=url, token=token, org=org, bucket=bucket)

try:
    client.ping()
    print("Connected to InfluxDB!")
except Exception as e:
    print("Failed to connect to InfluxDB:", e)

# สร้าง query โดยระบุ Measurement ที่ต้องการ
query = f'from(bucket:"{bucket}") \
             |> range(start: -1m) \
             |> filter(fn: (r) => r._measurement == "rmuti_kkc_csb_01") \
             |> filter(fn: (r) => r._field == "pm10") \
             |> last()'
tables = client.query_api().query(query, org=org)

# นำผลลัพธ์มาเก็บไว้ใน list และ return ออกไป
# result = []
for table in tables:
    for record in table.records:
        result = round(record.values['_value'], 2)
        # print(result)
        print(result)