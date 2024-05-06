from dagster import asset
from time import sleep
import logging

@asset(group_name="thomas")
def cherie():
    sleep(10)
    logging.info("YIHAA")
    return 1

@asset(group_name="thomas")
def lala():
    return 2

@asset(group_name="thomas")
def lalalaback():
    return 3