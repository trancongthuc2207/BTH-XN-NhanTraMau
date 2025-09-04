from typing import Optional


class VietQRGenerator:
    # Raw prefix from original QR code
    RAW_PREFIX = ""
    CURRENCY_CODE_VND = "704"
    COUNTRY_CODE_VN = "VN"
    CRC_CODE = "6304"

    def __init__(self, RAW_PREFIX: str = None):
        """
        Initialize VietQR generator with fixed bank details from raw prefix.

        Args:
            RAW_PREFIX (str, optional): Raw prefix containing format, initiation method, and bank info.
                                       Defaults to VTB prefix if None.
        """
        self.RAW_PREFIX = RAW_PREFIX or self.RAW_PREFIX

        # Validate raw prefix (basic check)
        if not self.RAW_PREFIX.startswith("00020101"):
            raise ValueError(
                "Invalid raw prefix: Must start with payload format and initiation method")
        if "A000000727" not in self.RAW_PREFIX or "QRIBFTTA" not in self.RAW_PREFIX:
            raise ValueError(
                "Invalid raw prefix: Must contain NAPAS ID and service code")

    def _calculate_crc(self, payload: str) -> str:
        """
        Calculate CRC-16 for the QR code payload.

        Args:
            payload (str): Payload string without CRC.

        Returns:
            str: 4-digit hexadecimal CRC.
        """
        crc = 0xFFFF
        for char in payload:
            crc ^= ord(char) << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return f"{crc:04X}"

    def generate_qr_text(
        self,
        amount: Optional[int] = None,
        description: Optional[str] = None,
        merchant_name: Optional[str] = None,
        merchant_city: Optional[str] = None,
        postal_code: Optional[str] = None
    ) -> str:
        """
        Generate VietQR QR code text payload using raw prefix.

        Args:
            amount (int, optional): Transaction amount in VND.
            description (str, optional): Transaction description.
            merchant_name (str, optional): Merchant name.
            merchant_city (str, optional): Merchant city.
            postal_code (str, optional): Postal code.

        Returns:
            str: QR code text payload.

        Raises:
            ValueError: If amount is invalid.
        """
        # Start with raw prefix
        payload = self.RAW_PREFIX

        # Currency Code (VND)
        payload += f"53{len(self.CURRENCY_CODE_VND):02d}{self.CURRENCY_CODE_VND}"

        # Amount
        if amount is not None:
            if not isinstance(amount, int) or amount < 0:
                raise ValueError("Amount must be a non-negative integer")
            amount_str = f"{amount}"
            payload += f"54{len(amount_str):02d}{amount_str}"

        # Country Code
        payload += f"58{len(self.COUNTRY_CODE_VN):02d}{self.COUNTRY_CODE_VN}"

        # Merchant Name
        if merchant_name:
            payload += f"59{len(merchant_name):02d}{merchant_name}"

        # Merchant City
        if merchant_city:
            payload += f"60{len(merchant_city):02d}{merchant_city}"

        # Postal Code
        if postal_code:
            payload += f"61{len(postal_code):02d}{postal_code}"

        # Additional Data (Description)
        if description:
            additional_data = f"08{len(description):02d}{description}"
            payload += f"62{len(additional_data):02d}{additional_data}"

        # Calculate and append CRC
        crc = self._calculate_crc(payload + self.CRC_CODE)
        payload += self.CRC_CODE + crc

        return payload
