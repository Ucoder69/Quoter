from core.template_manager import get_template
# from core.date_formatter import format_stay_dates
from core.html_table import build_unit_table_html


def generate_email(template_name,
                   first_name,
                   surname,
                   check_in,
                   check_out,
                   units_data,
                   currency="₹"):

    template = get_template(template_name)

    # stay_dates = format_stay_dates(check_in, check_out)

    subject = template["subject"].format(name=first_name+ " " + surname)

    unit_table = build_unit_table_html(units_data, currency)

    body_html = template["body_html"].format(
        surname=surname or "Guest",
        check_in=check_in,
        check_out=check_out,
        price=unit_table
    )

    return {
        "subject": subject,
        "body_html": body_html
    }