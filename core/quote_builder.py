from core.parser import parse_booking_message, parse_units, parse_nights
from core.unit_mapper import map_units
from core.calculator import calculate_total
from core.email_generator import generate_email
from core.config_manager import ConfigManager


def build_quote(text):

    config = ConfigManager()

    units_config = config.get_all_units()

    allowed_keys = config.get_parser_keys()

    # --------------------------------
    # Parse message
    # --------------------------------
    parsed = parse_booking_message(text)
    nights=parse_nights(text)
    parsed_units = parse_units(text, allowed_keys)

    mapped_units = map_units(parsed_units, units_config)

    parsed["units"] = mapped_units

    # --------------------------------
    # Price calculation
    # --------------------------------
    units_data = []

    children = parsed["children_ages"] or []
    children_remaining = children.copy()

    for unit_id in mapped_units:

        unit_config = units_config[unit_id]

        max_children = unit_config["max_children"]

        # distribute children respecting room limits
        room_children = children_remaining[:max_children]

        children_remaining = children_remaining[max_children:]

        result = calculate_total(
            unit_config=unit_config,
            adults=parsed["adults"],
            children_ages=room_children,
            nights=parsed["nights"]
        )

        unit_data = {
            "display_name": unit_config["show_name"],
            "subtotal": result["subtotal"],
            "gst_percent": result["gst_percent"],
            "gst_amount": result["gst_amount"],
            "total": result["total"]
        }

        units_data.append(unit_data)


    # after loop check if children left
    if children_remaining:
        raise ValueError("Too many children for selected rooms")

    # --------------------------------
    # Generate email
    # --------------------------------
    email = generate_email(
        first_name=parsed["first_name"],
        template_name="default",
        surname=parsed["surname"],
        check_in=parsed["check_in"],
        check_out=parsed["check_out"],
        units_data=units_data
    )

    return {
        "parsed": parsed,
        "units_data": units_data,
        "email": email
    }