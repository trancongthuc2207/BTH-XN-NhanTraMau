import re
from django.utils.timezone import now
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import qrcode
from general_utils.banking import VietQRGenerator
from general_utils.GetConfig.UtilsConfigSystem import GET_VALUE_ACTION_SYSTEM
import unicodedata

# ---------------------------- #
# ---------------------------- #
# ---------- Utils ----------- #
# ---------------------------- #
# ---------------------------- #


def generate_qr_base64(data):
    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to a BytesIO stream
    buffered = BytesIO()
    img.save(buffered, format="PNG")

    # Encode the image to base64
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_base64


def generate_qr_base64_custom(data, box_size=10, border=4):
    # Generate the QR code
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create QR code image
    qr_image = qr.make_image(
        fill_color="black", back_color="white").convert("RGB")

    # Save the QR code to a BytesIO stream
    buffered = BytesIO()
    qr_image.save(buffered, format="PNG")

    # Convert the image to base64 string (without data URI prefix)
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_base64


def generate_qr_with_logo_base64(data, logo_path, box_size=5):
    # Generate the QR code
    qr = qrcode.QRCode(
        version=4,  # Adjust version to support more data if necessary
        # High error correction to support the logo
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create QR code image
    qr_image = qr.make_image(
        fill_color="black", back_color="white").convert("RGB")

    # Open the logo image
    logo = Image.open(logo_path)

    # Resize the logo to fit in the center of the QR code
    qr_width, qr_height = qr_image.size
    # Adjust the logo size (1/5th of the QR code width)
    logo_size = qr_width // 5
    logo = logo.resize((logo_size, logo_size),
                       Image.Resampling.LANCZOS)  # Updated here

    # Calculate the position to paste the logo
    logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

    # Paste the logo onto the QR code
    qr_image.paste(logo, logo_pos, mask=logo if logo.mode == "RGBA" else None)

    # Save the QR code with the logo to a BytesIO stream
    buffered = BytesIO()
    qr_image.save(buffered, format="PNG")

    # Convert the QR code image to a Base64 string
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_base64


def generate_qr_with_logo_and_resized_text(
    data,
    logo_path,
    bottom_text,
    text_color="red",
    text_width=200,
    text_height=50,
    font_size=20,
):
    # Generate the QR code
    qr = qrcode.QRCode(
        version=4,  # Adjust version for more data
        # High error correction to accommodate logo
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create QR code image
    qr_image = qr.make_image(
        fill_color="black", back_color="white").convert("RGB")

    # Open the logo image
    logo = Image.open(logo_path)

    # Resize the logo to fit in the center of the QR code
    qr_width, qr_height = qr_image.size
    logo_size = qr_width // 5  # Logo size is 1/5th of QR code's width
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

    # Calculate the position to paste the logo
    logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

    # Paste the logo onto the QR code
    qr_image.paste(logo, logo_pos, mask=logo if logo.mode == "RGBA" else None)

    # Create an image for the text (resized)
    text_image = Image.new("RGB", (text_width, text_height), "white")
    draw = ImageDraw.Draw(text_image)

    # Use the default font
    font = ImageFont.load_default()

    # Scale the text by drawing it at a larger size
    scale_factor = font_size / 10  # Based on the default font size of 10
    larger_font = ImageFont.truetype(
        "arial.ttf", int(10 * scale_factor)
    )  # We use a scaled version of a default font
    text_bbox = larger_font.getbbox(bottom_text)

    # Calculate the position to center the text
    text_width_actual = text_bbox[2] - text_bbox[0]
    text_height_actual = text_bbox[3] - text_bbox[1]

    # Ensure the text fits within the specified width and height
    text_position = (
        (text_width - text_width_actual) // 2,
        (text_height - text_height_actual) // 2,
    )

    # Draw the text with the resized default font
    draw.text(text_position, bottom_text, fill=text_color, font=larger_font)

    # Combine QR code and text (no gap between QR and text)
    final_height = qr_height + text_height  # Final image height (QR + text)
    final_image = Image.new("RGB", (qr_width, final_height), "white")

    # Paste QR code at the top of the final image
    final_image.paste(qr_image, (0, 0))

    # Paste text image directly below the QR code (no gap)
    final_image.paste(text_image, (0, qr_height))  # `qr_height` ensures no gap

    # Save the final image to a BytesIO stream
    buffered = BytesIO()
    final_image.save(buffered, format="PNG")

    # Convert the final image to a Base64 string
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_base64


def remove_vietnamese_accents(text):
    """
    Removes Vietnamese diacritics (accents) from a UTF-8 string.
    """
    try:
        # Normalize the text to decomposed form (NFD)
        normalized = unicodedata.normalize('NFD', text)
        # Filter out combining marks
        ascii_text = ''.join(
            c for c in normalized if unicodedata.category(c) != 'Mn'
        )
        # Replace specific characters not covered by NFD
        ascii_text = ascii_text.replace('đ', 'd').replace('Đ', 'D')
        return ascii_text
    except Exception as e:
        print(f"Error in remove_vietnamese_accents: {e}")
        return text


def create_qr_banking_custom(request_payment, thanhvien_upload, hoinghi):
    try:
        # Generate QR code with logo
        amount = int(round(request_payment.amount))
        if not GET_VALUE_ACTION_SYSTEM("SET_RAW_PREFIX_BANKING"):
            # Return error if no active prices found
            raise Exception(f"Không tìm thấy Prefix QR code!")
        qr_gen = VietQRGenerator(
            RAW_PREFIX=GET_VALUE_ACTION_SYSTEM("SET_RAW_PREFIX_BANKING"))

        description_text = ""
        template_text = GET_VALUE_ACTION_SYSTEM(
            "SET_DESCRIPTION_TV_UPLOAD_BANKING")
        if template_text:
            description_text = template_text.format(hoten=remove_vietnamese_accents(thanhvien_upload.hoten), rq_id=str(
                request_payment.request_id)[-5:], tv_id=thanhvien_upload.pk, name_viettat=hoinghi.name_viettat)
        else:
            description_text = f"{remove_vietnamese_accents(thanhvien_upload.hoten)}-{str(request_payment.request_id)[-5:]}-{thanhvien_upload.pk}-{hoinghi.name_viettat}"
        qr_text = qr_gen.generate_qr_text(
            amount=amount,
            description=description_text,
        )

        qr_base64_text = "data:image/png;base64," + generate_qr_with_logo_base64(
            qr_text,
            r"static\others\image\logo.png")
        price_image_hn = qr_base64_text

        return price_image_hn
    except Exception as e:
        print(f"Error in create_qr_banking_custom: {e}")
        return None
