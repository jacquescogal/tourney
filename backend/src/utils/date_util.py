from datetime import datetime, timezone

def ddmm_to_unix(ddmm: str) -> int:
    """
    Converts a date in DD/MM format to Unix time, assuming the first year is 1970.

    Args:
    ddmm: str: Date in DD/MM format.

    Returns:
    unix_time: int: Corresponding Unix timestamp.
    """
    # from first leap year after 1970
    dt = datetime.strptime(ddmm + "/1972", "%d/%m/%Y")
    
    unix_time = int(dt.timestamp())
    
    return unix_time

def unix_to_ddmm(unix_time: int) -> str:
    """
    Converts Unix time to DD/MM format using timezone-aware datetime objects.

    Args:
    unix_time: int: Unix timestamp.

    Returns:
    date_str: str: Date in DD/MM format.
    """
    dt = datetime.fromtimestamp(unix_time)
    
    date_str = dt.strftime("%d/%m")
    
    return date_str