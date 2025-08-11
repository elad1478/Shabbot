"""
QR Code Generation Tool (simplified)
"""
import os
from datetime import datetime

import qrcode
from langchain_core.tools import tool


OUTPUT_DIR = os.path.join("outputs", "qr_codes")
os.makedirs(OUTPUT_DIR, exist_ok=True)


@tool
def generate_qr_code(data: str, filename: str | None = None) -> str:
    """
    Generate a QR code from the given data (URL, text, etc.).

    Args:
        data: The data to encode in the QR code
        filename: Optional filename for the QR code image ('.png' will be added if missing)

    Returns:
        Path to the generated QR code image
    """
    if not data:
        raise ValueError("data is required to generate a QR code")

    if not filename:
        filename = f"qr_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    elif not filename.endswith(".png"):
        filename += ".png"

    filepath = os.path.join(OUTPUT_DIR, filename)

    # Create and save the QR image using qrcode's simple API
    img = qrcode.make(data)
    img.save(filepath)

    return filepath