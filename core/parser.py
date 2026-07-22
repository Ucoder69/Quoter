import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional


MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


# ---------------------------
# Date formatting
# ---------------------------
def ordinal(n: int) -> str:

    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")

    return f"{n}{suffix}"


def format_date(date_obj: datetime) -> str:

    day = ordinal(date_obj.day)
    month = date_obj.strftime("%B")
    year = date_obj.year

    return f"{day} {month}, {year}"


# ---------------------------
# Email
# ---------------------------
def parse_email(text: str) -> Optional[str]:

    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)

    return match.group(0) if match else None


# ---------------------------
# Name
# ---------------------------
def parse_name(text: str):

    match = re.search(r'name[-:\s]*([A-Za-z ]+)', text, re.IGNORECASE)

    if not match:
        return None, None

    parts = match.group(1).strip().split()

    if len(parts) == 1:
        return parts[0], None

    return parts[0], parts[-1]


# ---------------------------
# Units
# ---------------------------
def parse_units(text: str, allowed_keys=None):
    """
    Extract unit keys like: room1, room2, hut1, kb
    Only keep keys that exist in allowed_keys (from config).
    """

    text = text.lower()
    units = []

    # ---------------------------
    # room numbers: room 1,2,10
    # ---------------------------
    room_match = re.search(r'room\s*([\d,\s]+)', text)
    if room_match:
        numbers = re.findall(r'\d+', room_match.group(1))
        for n in numbers:
            units.append(f"room{n}")

    # ---------------------------
    # hut numbers: hut 1,2
    # ---------------------------
    hut_match = re.search(r'hut\s*([\d,\s]+)', text)
    if hut_match:
        numbers = re.findall(r'\d+', hut_match.group(1))
        for n in numbers:
            units.append(f"hut{n}")

    # ---------------------------
    # codes like KB, BB etc
    # ---------------------------
    codes = re.findall(r'\b[a-z]{2,3}\b', text)
    for code in codes:
        units.append(code)

    # ---------------------------
    # Filter against config keys
    # ---------------------------
    if allowed_keys:
        allowed = set(k.lower() for k in allowed_keys)
        units = [u for u in units if u in allowed]

    return sorted(set(units))



# ---------------------------
# Adults
# ---------------------------
def parse_adults(text: str) -> Optional[int]:

    match = re.search(r'(\d+)\s*adult', text, re.IGNORECASE)

    if match:
        return int(match.group(1))

    pax = re.search(r'(\d+)\s*pax', text, re.IGNORECASE)

    if pax:
        return int(pax.group(1))

    return None


# ---------------------------
# Children
# ---------------------------
def parse_children(text: str) -> Optional[List[int]]:

    text = text.lower()

    # case: 6,9years
    match = re.search(r'childs?\s*(\d+,\d+)\s*years?', text)

    if match:
        ages = match.group(1).split(',')
        return [int(a) for a in ages]

    # case: 2 kids 6years each
    match = re.search(r'(\d+)\s*childs?\s*(\d+)\s*years?\s*each', text)

    if match:
        count = int(match.group(1))
        age = int(match.group(2))
        return [age] * count

    # case: 1 child 6years
    match = re.search(r'child\s*(\d+)\s*years?', text)

    if match:
        return [int(match.group(1))]

    return []


# ---------------------------
# Nights
# ---------------------------
def parse_nights(text: str) -> int:

    match = re.search(r'(\d+)\s*night', text, re.IGNORECASE)

    if match:
        return int(match.group(1))

    return 1


# ---------------------------
# Stay Date
# ---------------------------
def parse_stay_date(text: str) -> Optional[datetime]:

    match = re.search(r'(\d{1,2})(st|nd|rd|th)?\s*([A-Za-z]{3,})', text)

    if not match:
        return None

    day = int(match.group(1))
    month_str = match.group(3).lower()[:3]

    if month_str not in MONTH_MAP:
        return None

    month = MONTH_MAP[month_str]

    today = datetime.today()

    year = today.year

    try:
        stay_date = datetime(year, month, day)
    except ValueError:
        return None

    # if date already passed this year → next year
    if stay_date.date() <= today.date():
        stay_date = datetime(year + 1, month, day)

    return stay_date


# ---------------------------
# Compute Check-in / Check-out
# ---------------------------
def compute_stay_dates(text: str):

    check_in = parse_stay_date(text)

    if not check_in:
        return None, None

    nights = parse_nights(text)

    check_out = check_in + timedelta(days=nights)

    return check_in, check_out


# ---------------------------
# Main Parser
# ---------------------------
def parse_booking_message(text: str, valid_units=None) -> Dict:

    check_in, check_out = compute_stay_dates(text)

    first, surname = parse_name(text)

    return {

        "units": parse_units(text, valid_units),

        "check_in": format_date(check_in) if check_in else None,

        "check_out": format_date(check_out) if check_out else None,

        "first_name": first,

        "surname": surname,

        "email": parse_email(text),

        "adults": parse_adults(text),

        "children_ages": parse_children(text),

        "nights": parse_nights(text)

    }