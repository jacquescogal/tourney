from datetime import datetime,timedelta

def ddmm_to_day_of_year(ddmm: str) -> int:
    """
    Converts a date in DD/MM format to Unix time, assuming the first year is 1970.

    Args:
    ddmm: str: Date in DD/MM format.

    Returns:
    day_of_year: int: Day of the year
    """
    # from first leap year after 1970
    dt = datetime.strptime(ddmm + "/1972", "%d/%m/%Y")
    
    # Get the day of the year
    day_of_year = dt.timetuple().tm_yday
    
    return day_of_year

def day_of_year_to_ddmm(day_of_year: int) -> str:
    """
    Converts Unix time to DD/MM format using timezone-aware datetime objects.

    Args:
    day_of_year: int: Day of the year.

    Returns:
    date_str: str: Date in DD/MM format.
    """
    # Convert day of the year to a specific date (dd/mm) for the year 1972 (first lear year after epoch)
    year = 1972

    # Get the date corresponding to the day of the year
    dt = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)

    # Format the date as dd/mm
    ddmm = dt.strftime("%d/%m")

    return ddmm