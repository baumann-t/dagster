import logging
from time import sleep

from dagster import asset


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
