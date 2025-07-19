#!/usr/bin/env python3
"""
Generate QR codes in red/black colorscheme for the red page.
"""

import qrcode
from PIL import Image

def create_red_qr_code(url, filename, label):
    """Create a QR code with red/black colorscheme."""
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create image with red/black colorscheme
    qr_image = qr.make_image(fill_color="red", back_color="black")
    
    # Resize to a reasonable size
    qr_image = qr_image.resize((200, 200), Image.Resampling.NEAREST)
    
    # Save the QR code
    qr_image.save(filename)
    print(f"Generated {filename} for {label}")

def main():
    """Generate QR codes for all links."""
    links = [
        {
            "url": "https://wakenmake.shop/projects/primitive_obsession/red.html",
            "filename": "qr_this_page.png",
            "label": "THIS PAGE"
        },
        {
            "url": "https://www.gofundme.com/f/help-us-create-interactive-art-in-sf",
            "filename": "qr_donate.png", 
            "label": "DONATE"
        },
        {
            "url": "https://discord.gg/yTFjYmhmZD",
            "filename": "qr_get_involved.png",
            "label": "GET INVOLVED"
        }
    ]
    
    for link in links:
        create_red_qr_code(link["url"], link["filename"], link["label"])

if __name__ == "__main__":
    main() 