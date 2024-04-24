from dagster import asset
from time import sleep

@asset(group_name="thomas")
def thomas_gcp():
    sleep(20)
    print("YIHAAA im running on gcp")
    print("PEDALE")
    return 1
