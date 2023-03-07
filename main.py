import ipdb

import crosschex.adapter as adapter
import crosschex.ops as utils

if __name__ == "__main__":
    workers = utils.get_workers()
    for worker in workers:
        utils.calculate_shifts(utils.get_timesheets_df(date_from="2022-01-01", date_to="2023-06-22", department_id=0, internal_id=worker["workno"]))