from dagster import asset

@asset(group_name="thomas")
def thomas_gcp():
    print("YIHAAA")
    return 1
