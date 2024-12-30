import datetime
import logging

def get_next_weekday(day_name: str):
    try:
        days_of_week = {
            "Lundi": 0,
            "Mardi": 1,
            "Mercredi": 2,
            "Jeudi": 3,
            "Vendredi": 4,
            "Samedi": 5,
            "Dimanche": 6
        }

        day_of_week = days_of_week.get(day_name)

        if day_of_week is None:
            raise ValueError("Jour de la semaine invalide.")

        today = datetime.date.today()
        today_weekday = today.weekday()

        days_until_next_day = (day_of_week - today_weekday + 7) % 7

        if days_until_next_day == 0:
            days_until_next_day = 7

        next_day_date = today + datetime.timedelta(days=days_until_next_day)

        return next_day_date

    except Exception as e:
        logging.critical(f"Problème d'exécution {e}", exc_info=True)
        return None

def get_time_from_string(time_str: str):
    try:
        time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
        return time_obj
    except Exception as e:
        logging.critical(f"Problème d'exécution {e}", exc_info=True)
        return None

def get_datetime_for_day_time(day_name: str, time_str: str):
    try:
        next_day = get_next_weekday(day_name)
        time_obj = get_time_from_string(time_str)
        if not next_day or not time_obj:
            return None
        target_datetime = datetime.datetime.combine(next_day, time_obj)
        return target_datetime
    except Exception as e:
        logging.critical(f"Problème d'exécution {e}", exc_info=True)
        return None

def datetime_to_day_string(dt: datetime.datetime):
    try:
        months = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        days_of_week = [
            "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"
        ]
        day_of_week = days_of_week[dt.weekday()]
        month_name = months[dt.month - 1]
        formatted_date = f"{day_of_week} {dt.day} {month_name} {dt.year}"

        return formatted_date
    except Exception as e:
        logging.critical(f"Problème d'exécution {e}", exc_info=True)
        return None