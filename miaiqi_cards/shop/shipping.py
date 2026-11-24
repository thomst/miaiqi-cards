from decimal import Decimal
from cart.shipping import ShippingCalculator, ShippingOption


class DefaultShipping(ShippingCalculator):
    COST = Decimal("2.00")

    def get_options(self, cart):
        return [
            ShippingOption(
                id="standard",
                name="Standard Shipping",
                price=str(self.COST),
            )
        ]

    def calculate(self, cart):
        if cart.is_empty():
            return Decimal("0.00")
        else:
            return self.COST
