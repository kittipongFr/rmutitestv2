from datetime import timedelta

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from influxdb_client import InfluxDBClient
import pandas as pd
from django.urls import reverse
import requests

def get_data():
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

    # สร้าง query โดยระบุ Measurement ที่ต้องการ
    query = f'from(bucket:"{bucket}") \
              |> range(start: -1m) \
              |> filter(fn: (r) => r._measurement == "kbide") \
              |> filter(fn: (r) => r._field == "TEMP") \
              |> last()'


    tables = client.query_api().query(query, org=org)

    # นำผลลัพธ์มาเก็บไว้ใน list และ return ออกไป
    # result = []
    for table in tables:
        for record in table.records:
            result = round(record.values['_value'], 2)
            # print(result)
            return  result




def get_average_data():
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

    # สร้าง query โดยระบุ Measurement ที่ต้องการ
    query = f'from(bucket:"{bucket}") \
              |> range(start: -24h) \
              |> filter(fn: (r) => r._measurement == "kbide") \
              |> filter(fn: (r) => r._field == "TEMP") \
              |> mean()'
    # การคำนวณเฉลี่ยใน query ของ InfluxDB โดยใช้ฟังก์ชัน mean()
    # และระบุช่วงเวลาที่ต้องการคำนวณด้วย range(start: -24h) ที่หมายถึงย้อนหลัง 24 ชั่วโมง โดยเริ่มนับเวลาจากปัจจุบันโดยใช้ timezone.now()
    # และหักไป 24 ชั่วโมงด้วย timedelta(hours=24) ก่อนนำไปใช้ใน range(start: ...)

    tables = client.query_api().query(query, org=org)

    # นำผลลัพธ์มาเก็บไว้ใน list และ return ออกไป
    for table in tables:
        for record in table.records:
            result = round(record.values['_value'], 2)
            # print(result)
            return  result


def index(request):
    # สร้าง URL ของ view get_data
    data = get_data()
    if data > 30.5:
        val = 1
    else:
        val = 0

    # เรียกใช้ API โดยใช้ requests
    # แสดงผลลัพธ์ใน HTML template
    context = {'data': data,'val':val}
    return render(request, 'index.html', context)


def chart_view(request):
    # เรียกใช้งานฟังก์ชัน get_data() เพื่อรับค่าอุณหภูมิล่าสุด
    temperature = get_data()

    # สร้าง list เพื่อเก็บข้อมูลการวัดอุณหภูมิในแต่ละครั้ง
    temperature_list = []

    # ระบุจำนวนการวัดอุณหภูมิที่ต้องการแสดงบนกราฟ
    num_of_temperature = 10

    # เพิ่มค่าอุณหภูมิใน list และเก็บเฉพาะจำนวนค่าตามที่กำหนดไว้ใน num_of_temperature
    for i in range(num_of_temperature):
        temperature_list.append(temperature)
        temperature = get_data()


    return render(request,'chart.html',{'temperature_list': temperature_list})



def showaqi(request):
    # สร้าง URL ของ view get_data
    data = get_data()
    if data > 30.5:
        val = 1
    else:
        val = 0

    # เรียกใช้ API โดยใช้ requests
    # แสดงผลลัพธ์ใน HTML template
    context = {'data': data,'val':val}
    return render(request, 'desktop3.html', context)

def show(request):
    data = get_data()
    return HttpResponse(data)