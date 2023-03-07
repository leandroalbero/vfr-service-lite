import datetime
from typing import List, Tuple

from termcolor import colored
import crosschex.adapter as cx
import polars as pl

API_EMPLOYEE_TIMESHEET = "record/grid"
API_WORKER_LIST = "employee/grid"
DATE_FORMAT = "%Y-%m-%d"


def get_companies() -> []:
    """Get companies from Anviz Cloud API"""
    adapter = cx.CrossChexCloudAdapter()
    response = adapter.post('company/list', {})
    return [response for response in response['data']]


def get_workers() -> []:
    """Get workers from Anviz Cloud API"""
    adapter = cx.CrossChexCloudAdapter()
    page = 1
    page_count = 1
    workers = []
    while page <= page_count:
        response = adapter.post(path=API_WORKER_LIST, body={"page": page, "perPage": 20})
        if response["code"] == 200:
            for worker in response["data"]["list"]:
                workers.append(worker)
            page_count = response["data"]["pageCount"]
            page += 1
        else:
            workers = []
            page_count = 0
    return workers


def get_workers_page(page: int, keyword: str) -> Tuple[list, int]:
    body = {
        "page": page,
        "perPage": 20,
        "keyword": keyword,
        "order_col": "workno",
        "order_dir": "ASC",
    }
    response = cx.CrossChexCloudAdapter().post(path=API_WORKER_LIST, body=body)
    if response["code"] == 200:
        return response["data"]["list"], response["data"]["pageCount"]
    else:
        return [], 0


def get_timesheets_page(
        page: int,
        keyword: str,
        date_from: datetime.datetime,
        date_to: datetime.date,
        department_id: int,
) -> Tuple[list, int]:
    body = {
        "page": page,
        "perPage": 20,
        "keyword": keyword,
        "department_id": department_id,
        "startdate": date_from.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
        "enddate": date_to.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
        "order_col": "checktime",
        "order_dir": "DESC",
    }
    response = cx.CrossChexCloudAdapter().post(path=API_EMPLOYEE_TIMESHEET, body=body)
    if response["code"] == 200:
        return response["data"]["list"], response["data"]["pageCount"]
    else:
        print(f"[ERR] Anviz API Cloud: download_timesheets ERR:{response['code']}")
        return [], 0


def get_timesheets(date_from: str, date_to: str, department_id: int, internal_id: int) -> list:
    _date_from = datetime.datetime.strptime(date_from, DATE_FORMAT)
    _date_to = datetime.datetime.strptime(date_to, DATE_FORMAT)
    page = 1
    page_count = 1
    timesheets = []
    while page <= page_count:
        page_timesheets, page_count = get_timesheets_page(page, str(internal_id), _date_from, _date_to, department_id)
        timesheets += page_timesheets
        page += 1
    return timesheets


def get_timesheets_df(date_from: str, date_to: str, department_id: int, internal_id: int) -> pl.DataFrame:
    timesheets = get_timesheets(date_from, date_to, department_id, internal_id)
    for timesheet in timesheets:
        timesheet["checktime"] = datetime.datetime.fromisoformat(timesheet["checktime"])
    return pl.DataFrame(timesheets)


def print_report(pairs: list, unique: list, employee_id: int) -> None:
    print(colored(f"Employee: {pairs[0][0][1]} | ID: {employee_id}", "red"))
    print(colored("--------------------------------------------------------------", "grey"))
    for shift in pairs:
        start = shift[0][0]
        end = shift[-1][0]
        print(f"{start} -> {end}, | {end - start} hours | {len(shift)} punches")
    for shift in unique:
        start = shift[0][0]
        print(f"{colored(start, 'yellow')} missing punch")
    print(colored("--------------------------------------------------------------", "grey"))


def calculate_shifts(dataframe):
    if dataframe.height == 0:
        return [], []
    shifts = [
        y.rows()
        for x, y in dataframe.sort("checktime")
        .select("checktime", "name")  # type: ignore
        .groupby_rolling(index_column="checktime", period="12h")
    ]
    pairs = list(filter(lambda x: len(x) > 1, shifts))
    unique = list(filter(lambda x: len(x) == 1, shifts))
    if len(pairs) != 0:
        unique = [u for u in unique if not any(u[0][0] == p[0][0] or u[0][0] == p[0][1] for p in pairs)]
        pairs = [p for i, p in enumerate(pairs) if i == 0 or p[1][0] != pairs[i - 1][0][0]]
        print_report(pairs, unique, dataframe["workno"][0])
    return pairs, unique
