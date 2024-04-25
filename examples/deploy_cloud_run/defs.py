from dagster import asset
from time import sleep
import logging

@asset(group_name="thomas")
def thomas_gcp():
    sleep(50)
    logging.info("YIHAA")
    return 1
