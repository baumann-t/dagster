from dagster import asset

@asset(group_name="thomas")
def thomas_gcp():
    print("YIHAAA im running on gcp")
    print("PEDALE")
    return 1
