from typing import Dict, List


class PricingError(Exception):
    pass


def calculate_extra_mattress(unit_config: Dict, adults: int, children_ages: List[int]) -> float:
    """
    Calculates extra mattress charges based on adults and children.
    """

    default_adults = unit_config["default_adults"]
    max_adults = unit_config["max_adults"]

    mattress_rules = unit_config["extra_mattress_price"]

    adult_price = mattress_rules["adult_price"]
    child_price = mattress_rules["child_price_under_12"]
    child_free = mattress_rules["child_under_5_free"]

    extra_cost = 0

    # Adults exceeding default
    if adults > default_adults:
        extra_adults = adults - default_adults
        extra_cost += extra_adults * adult_price

    # Children pricing
    for age in children_ages:

        if age < 5 and child_free:
            continue

        elif age < 12:
            extra_cost += child_price

        else:
            extra_cost += adult_price

    return extra_cost


def calculate_subtotal(unit_config: Dict, adults: int, children_ages: List[int]) -> float:

    base_price = unit_config["base_price"]

    extra_mattress_cost = calculate_extra_mattress(
        unit_config,
        adults,
        children_ages
    )

    subtotal = base_price + extra_mattress_cost

    return subtotal


def apply_discount(amount: float, discount_type=None, discount_value=0) -> float:
    """
    discount_type: 'flat' or 'percent'
    """

    if not discount_type:
        return amount

    if discount_type == "flat":
        return max(0, amount - discount_value)

    if discount_type == "percent":
        return amount * (1 - discount_value / 100)

    raise PricingError("Invalid discount type")


def calculate_gst(amount: float, gst_percent: int):

    gst_amount = round(amount * gst_percent / 100, 3)   #rounding gst and thus amnt

    return gst_amount

def validate_pax(unit_config, adults, children_ages):

    max_adults = unit_config["max_adults"]
    max_children = unit_config["max_children"]

    if adults > max_adults:
        raise ValueError(
            f"{unit_config['show_name']} allows max {max_adults} adults"
        )

    if children_ages and len(children_ages) > max_children:
        raise ValueError(
            f"{unit_config['show_name']} allows max {max_children} children")

def calculate_total(unit_config: Dict,
                    adults: int,
                    children_ages: List[int], nights, 
                    discount_type=None,
                    discount_value=0) -> Dict:
    
    
    # convert children >=12 into adults
    adult_children = [age for age in children_ages if age >= 12]
    young_children = [age for age in children_ages if age < 12]

    adults = adults + len(adult_children)
    children_ages = young_children
    validate_pax(unit_config, adults, children_ages)
    if adults > unit_config["max_adults"]:
        raise ValueError(
            f"{unit_config['show_name']} allows max {unit_config['max_adults']} adults"
        )

    if len(children_ages) > unit_config["max_children"]:
        raise ValueError(
            f"{unit_config['show_name']} allows max {unit_config['max_children']} children"
        )
    one_night = calculate_subtotal(unit_config, adults, children_ages)
    subtotal= one_night * nights

    discounted = apply_discount(subtotal, discount_type, discount_value)

    gst_percent = unit_config["gst_percent"]

    gst_amount = calculate_gst(discounted, gst_percent)

    total = discounted + gst_amount

    return {
        "base_price": unit_config["base_price"],
        "subtotal": subtotal,
        "after_discount": discounted,
        "gst_percent": gst_percent,
        "gst_amount": gst_amount,
        "total": total
    }