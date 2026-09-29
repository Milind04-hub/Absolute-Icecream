from io import BytesIO

import qrcode


def generate_qr_code(data):
    """Create a PNG QR code for the supplied URL or text."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image()

    output = BytesIO()

    image.save(
        output,
        format="PNG"
    )

    output.seek(0)

    return output