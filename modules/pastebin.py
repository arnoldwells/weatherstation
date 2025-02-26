def get_birthday_list():
    import logging
    import requests 
    from datetime import datetime, date
    from data.config import PASTEBIN_URL
    
    logger = logging.getLogger(__name__)

    def mmdd_to_date(mmdd_str, year=2024):                                              # add default year 
        date_str = f"{year}{mmdd_str}"
        date_obj = datetime.strptime(date_str, "%Y%m%d").date()                         # parse string into date object
        return date_obj

    try:
        now = date.today()
        birthday_list = []
        response = requests.get(PASTEBIN_URL)   
        birthday_dict = response.json()
        assert 'dates' in birthday_dict.keys()
    except Exception as e:
        logger.error(e)
        birthday_list = [(-1, "Error", "icons/past.png")]
    else:
        for date_key, person in birthday_dict['dates'].items():
            date_value = mmdd_to_date(date_key, now.year)
            delta = (date_value - now).days
            if delta == 0:
                birthday_list.append((0, person, "icons/present.png"))
            elif 0 < delta < 15:
                birthday_list.append((delta, person, "icons/future.png"))
            elif delta == -1:
                birthday_list.append((delta, person, "icons/past.png"))
        birthday_list.sort()
        logger.info(f"birthday list: {birthday_list}")
    finally:
        try: logger.info(f"pastebin response status code: {response.status_code}")
        except: pass
        return birthday_list[:2]                                                        # truncate to 2 enties

if __name__ == "__main__":
    print("should be run from main.py; test using: python -m modules.pastebin")
    print(get_birthday_list())