import re


def normalize(text):
    text = text.lower()
    text = re.sub(r"\s+", "", text)
    return text


def map_units(parsed_units, config_units):

    matched = []

    for parsed in parsed_units:

        parsed_norm = normalize(parsed)

        for unit_id, unit_data in config_units.items():

            display = unit_data["parser_key"]

            display_norm = normalize(display)

            if parsed_norm == display_norm:
                matched.append(unit_id)

            # also allow "room1" == "room 1"
            elif parsed_norm in display_norm:
                matched.append(unit_id)

    return list(set(matched))