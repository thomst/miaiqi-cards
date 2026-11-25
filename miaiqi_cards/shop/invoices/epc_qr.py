"""
Create payloads and QR images for EPC/SEPA Credit Transfer payments.

The payload follows the EPC QR Code specification (EPC069-12).
"""

import qrcode
from django.conf import settings


class EPCPayment:
    """Details for a SEPA Credit Transfer EPC QR code."""

    def __init__(self, amount, remittance):
        self.service_tag = "BCD"
        self.version = "002"
        self.character_set = "1"
        self.identification = "SCT"
        self.bic = settings.INVOICE_RECIPIENT_BIC
        self.name = settings.INVOICE_RECIPIENT_NAME
        self.iban = settings.INVOICE_RECIPIENT_IBAN
        self.amount = amount
        self.purpose = "TRAD"
        self.remittance = remittance

    def as_payload(self):
        """Return the newline-delimited EPC payload (without a trailing newline)."""
        amount = f"EUR{self.amount:.2f}"
        return "\n".join((
            self.service_tag, self.version, self.character_set, self.identification,
            self.bic, self.name, self.iban, amount, self.purpose, self.remittance
        ))

    def as_qr(self):
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(self.as_payload())
        qr.make(fit=True)
        return qr.make_image()
