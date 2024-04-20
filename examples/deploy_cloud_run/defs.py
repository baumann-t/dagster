from dagster import asset

@asset(group_name="thomas")
def thomas_gcp():
    print("YIHAAA im running on gcp")
    return 1
