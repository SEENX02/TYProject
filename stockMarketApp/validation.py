from datetime import datetime

def is_difference_more_than_75(startDate, endDate) -> bool:
    format = "%Y-%m-%d"
    start = datetime.strptime(startDate, format)
    end = datetime.strptime(endDate, format)
    return (end - start).days > 75

def validate(startDate, endDate):

    if not is_difference_more_than_75(startDate, endDate):
        print("Invalid Company Symbol or No Data Available.")
        return False
    else:
        return True