import requests
import os
from tabulate import tabulate
from const import API_URL
from dotenv import load_dotenv

load_dotenv()

headers = {"Authorization": f"Bearer {os.environ.get("APP_KEY")}"}


def get_tracking_information():
    try:
        resp = requests.get(f"{API_URL}tracking/counter", headers=headers)
        resp.raise_for_status()
        return ("EMAIL OPEN COUNT\n") + (
            tabulate(resp.json().get("data"), headers="keys", tablefmt="grid")
        )
    except requests.exceptions.HTTPError as e:
        print(f"get_tracking_information error: {e}")
        raise e


def get_email_count_by_department():
    try:
        resp = requests.get(f"{API_URL}email-count-by-dept", headers=headers)
        resp.raise_for_status()
        return ("EMAIL COUNT BY DEPARTMENT\n") + (
            tabulate(resp.json().get("data"), headers="keys", tablefmt="grid")
        )
    except requests.exceptions.HTTPError as e:
        print(f"get_email_count_by_department error: {e}")
        raise e
