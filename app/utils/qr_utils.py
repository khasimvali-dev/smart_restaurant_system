"""
Generates a QR code for a bill and returns it as a base64 data-URI so it can
be embedded directly in the printable receipt template with no extra file
storage or static-file route needed.
"""
import base64
import io

import qrcode


def bill_qr_data_uri(bill) -> str:
    payload = (
        f"Bill:{bill.bill_number}\n"
        f"Date:{bill.bill_date.strftime('%Y-%m-%d %H:%M')}\n"
        f"Total:{bill.grand_total}"
    )
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
