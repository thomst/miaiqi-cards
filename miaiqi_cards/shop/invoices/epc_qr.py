"""
Create payloads and QR images for EPC/SEPA Credit Transfer payments.

The payload follows the EPC QR Code specification (EPC069-12).
"""

from decimal import Decimal
from io import BytesIO
import base64

import qrcode
from django.conf import settings


class EPCPayment:
    """Details for a SEPA Credit Transfer EPC QR code."""

    def __init__(self, order):
        self.service_tag = "BCD"
        self.version = "002"
        self.character_set = "1"
        self.identification = "SCT"
        self.bic = settings.INVOICE_RECIPIENT_BIC
        self.name = settings.INVOICE_RECIPIENT_NAME
        self.iban = settings.INVOICE_RECIPIENT_IBAN
        self.amount = f"EUR{Decimal(order.cart_data['total']):.2f}"
        self.purpose = "TRAD"
        self.remittance = settings.PAYMENT_REMITTANCE_PATTERN.format(order=order)

    def as_payload(self):
        """Return the newline-delimited EPC payload (without a trailing newline)."""
        return "\n".join((
            self.service_tag, self.version, self.character_set, self.identification,
            self.bic, self.name, self.iban, self.amount, self.purpose, self.remittance
        ))

    def as_qr(self):
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(self.as_payload())
        qr.make(fit=True)
        return qr.make_image()

    def as_data_uri(self):
        buffer = BytesIO()
        self.as_qr().save(buffer, format='PNG')
        return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')