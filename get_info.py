import requests
from tabulate import tabulate
from const import API_URL


def get_tracking_information():
    try:
        resp = requests.get(f"{API_URL}tracking/counter")
        return ("EMAIL OPEN COUNT\n") + (
            tabulate(resp.json().get("data"), headers="keys", tablefmt="grid")
        )
    except requests.exceptions.RequestException as e:
        print(f"get_tracking_information error: {e}")
        raise e


def get_email_count_by_department():
    try:
        resp = requests.get(f"{API_URL}email-count-by-dept")
        return ("EMAIL COUNT BY DEPARTMENT\n") + (
            tabulate(resp.json().get("data"), headers="keys", tablefmt="grid")
        )
    except requests.exceptions.RequestException as e:
        print(f"get_email_count_by_department error: {e}")
        raise e
