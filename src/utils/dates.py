from collections import defaultdict
from datetime import datetime, date, timedelta
from typing import Any, Dict


def get_future_dates(days) -> dict[Any, set]:
    """
    Method returns the information about next 'days' from today.
    :return: Dict of future days and months.
    """
    today_date = date.today()
    dates = defaultdict(set)
    for _day in range(days + 1):
        _date: datetime.date = today_date + timedelta(days=_day)
        dates["month"].add(_date.month)
        dates["day"].add(_date.day)
    return dict(dates)


# def get_birthdays_per_week(users: dict[str, Any]) -> dict[str, list]:
#     """
#     Method returns the dictionary where the key is a name of the day (Monday, Tuesday
#     etc.) and the value is a list of names (people who have birthdays in that day).
#     :param users: The list of users with names and their birtdays.
#     :return: The dictionary where the key is a name of the day (Monday, Tuesday
#     etc.) and the value is a list of names (people who have birthdays in that day).
#     """
#     week_info = get_week_dates_per_year(days=)
#     week_birthdays = defaultdict(list)
#     for user in users:
#         user_birthday: datetime = user.get("birthday")
#         user_birthday_info = week_info.get((user_birthday.day, user_birthday.month))
#         if user_birthday_info:
#             user_first_name = user.get("name").split()[0]
#             day_name: str = user_birthday_info.get("day_name")
#             day_name: str | DayNames = day_name if day_name not in (
#             DayNames.SATURDAY.value,
#             DayNames.SUNDAY.value) \
#                 else DayNames.MONDAY.value
#             week_birthdays[day_name].append(user_first_name)
#     return dict(week_birthdays)
