def build_unit_table_html(units_data, currency="₹"):

    rows = []
    grand_total = 0

    for unit in units_data:

        name = unit["display_name"]
        subtotal = unit["subtotal"]
        gst = unit["gst_amount"]
        total = unit["total"]
        gst_percent = unit["gst_percent"]

        grand_total += total

        rows.append(
            f"""
            <tr>
                <td><b>{name}</b></td>
                <td>{currency}{subtotal}</td>
                <td>{gst_percent}%</td>
                <td>{currency}{gst}</td>
                <td><b>{currency}{total}</b></td>
            </tr>
            """
        )

    table = f"""
    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Unit</th>
            <th>Room Price</th>
            <th>GST</th>
            <th>GST Amount</th>
            <th>Total</th>
        </tr>
        {''.join(rows)}
    </table>

    <p><b>Grand Total: {currency}{grand_total}</b></p>
    """

    return table
