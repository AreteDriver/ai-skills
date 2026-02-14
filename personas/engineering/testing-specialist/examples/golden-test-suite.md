# Golden Example: Comprehensive Test Suite

Demonstrates the testing specialist writing a complete test suite with
happy paths, edge cases, error conditions, and clear naming.

## Input: Function to Test

```python
# cart.py — Shopping cart with discount logic

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class CartItem:
    product_id: str
    name: str
    price: Decimal
    quantity: int = 1


@dataclass
class Cart:
    items: list[CartItem] = field(default_factory=list)
    discount_code: Optional[str] = None

    DISCOUNT_CODES = {
        "SAVE10": Decimal("0.10"),    # 10% off
        "HALF": Decimal("0.50"),      # 50% off
        "WELCOME5": Decimal("0.05"),  # 5% off, first order only
    }

    MIN_ORDER_FOR_FREE_SHIPPING = Decimal("50.00")
    SHIPPING_COST = Decimal("5.99")

    def add_item(self, item: CartItem) -> None:
        for existing in self.items:
            if existing.product_id == item.product_id:
                existing.quantity += item.quantity
                return
        self.items.append(item)

    def remove_item(self, product_id: str) -> None:
        self.items = [i for i in self.items if i.product_id != product_id]

    def subtotal(self) -> Decimal:
        return sum(i.price * i.quantity for i in self.items, Decimal("0"))

    def discount_amount(self) -> Decimal:
        if not self.discount_code:
            return Decimal("0")
        rate = self.DISCOUNT_CODES.get(self.discount_code)
        if rate is None:
            raise ValueError(f"Invalid discount code: {self.discount_code}")
        return (self.subtotal() * rate).quantize(Decimal("0.01"))

    def shipping_cost(self) -> Decimal:
        if not self.items:
            return Decimal("0")
        if self.subtotal() - self.discount_amount() >= self.MIN_ORDER_FOR_FREE_SHIPPING:
            return Decimal("0")
        return self.SHIPPING_COST

    def total(self) -> Decimal:
        return self.subtotal() - self.discount_amount() + self.shipping_cost()
```

## Expected Test Output

```markdown
## Test Suite: Shopping Cart

### Test File: `tests/test_cart.py`

```python
import pytest
from decimal import Decimal

from cart import Cart, CartItem


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def empty_cart():
    return Cart()


@pytest.fixture
def cart_with_one_item():
    cart = Cart()
    cart.add_item(CartItem(product_id="A1", name="Widget", price=Decimal("10.00")))
    return cart


@pytest.fixture
def cart_over_free_shipping():
    """Cart with subtotal > $50 to qualify for free shipping."""
    cart = Cart()
    cart.add_item(CartItem(
        product_id="B1", name="Gadget", price=Decimal("30.00"), quantity=2
    ))
    return cart


# ─────────────────────────────────────────────
# add_item
# ─────────────────────────────────────────────

class TestAddItem:
    def test_adds_new_item_to_empty_cart(self, empty_cart):
        empty_cart.add_item(CartItem("A1", "Widget", Decimal("10.00")))
        assert len(empty_cart.items) == 1
        assert empty_cart.items[0].product_id == "A1"

    def test_increments_quantity_for_duplicate_product(self, cart_with_one_item):
        cart_with_one_item.add_item(CartItem("A1", "Widget", Decimal("10.00"), quantity=3))
        assert len(cart_with_one_item.items) == 1
        assert cart_with_one_item.items[0].quantity == 4

    def test_adds_different_products_separately(self, cart_with_one_item):
        cart_with_one_item.add_item(CartItem("B1", "Gadget", Decimal("20.00")))
        assert len(cart_with_one_item.items) == 2

    def test_quantity_defaults_to_one(self, empty_cart):
        empty_cart.add_item(CartItem("A1", "Widget", Decimal("10.00")))
        assert empty_cart.items[0].quantity == 1


# ─────────────────────────────────────────────
# remove_item
# ─────────────────────────────────────────────

class TestRemoveItem:
    def test_removes_existing_item(self, cart_with_one_item):
        cart_with_one_item.remove_item("A1")
        assert len(cart_with_one_item.items) == 0

    def test_removing_nonexistent_item_is_noop(self, cart_with_one_item):
        cart_with_one_item.remove_item("NONEXISTENT")
        assert len(cart_with_one_item.items) == 1

    def test_removing_from_empty_cart_is_noop(self, empty_cart):
        empty_cart.remove_item("A1")  # Should not raise
        assert len(empty_cart.items) == 0


# ─────────────────────────────────────────────
# subtotal
# ─────────────────────────────────────────────

class TestSubtotal:
    def test_empty_cart_subtotal_is_zero(self, empty_cart):
        assert empty_cart.subtotal() == Decimal("0")

    def test_single_item(self, cart_with_one_item):
        assert cart_with_one_item.subtotal() == Decimal("10.00")

    def test_multiple_quantity(self):
        cart = Cart()
        cart.add_item(CartItem("A1", "Widget", Decimal("10.00"), quantity=3))
        assert cart.subtotal() == Decimal("30.00")

    def test_multiple_different_items(self):
        cart = Cart()
        cart.add_item(CartItem("A1", "Widget", Decimal("10.00"), quantity=2))
        cart.add_item(CartItem("B1", "Gadget", Decimal("25.50")))
        assert cart.subtotal() == Decimal("45.50")


# ─────────────────────────────────────────────
# discount_amount
# ─────────────────────────────────────────────

class TestDiscountAmount:
    def test_no_discount_code_returns_zero(self, cart_with_one_item):
        assert cart_with_one_item.discount_amount() == Decimal("0")

    def test_valid_10_percent_discount(self):
        cart = Cart(discount_code="SAVE10")
        cart.add_item(CartItem("A1", "Widget", Decimal("100.00")))
        assert cart.discount_amount() == Decimal("10.00")

    def test_valid_50_percent_discount(self):
        cart = Cart(discount_code="HALF")
        cart.add_item(CartItem("A1", "Widget", Decimal("100.00")))
        assert cart.discount_amount() == Decimal("50.00")

    def test_discount_rounds_to_two_decimal_places(self):
        cart = Cart(discount_code="SAVE10")
        cart.add_item(CartItem("A1", "Widget", Decimal("33.33")))
        assert cart.discount_amount() == Decimal("3.33")  # 33.33 * 0.10 = 3.333 → 3.33

    def test_invalid_discount_code_raises_error(self):
        cart = Cart(discount_code="BOGUS")
        cart.add_item(CartItem("A1", "Widget", Decimal("10.00")))
        with pytest.raises(ValueError, match="Invalid discount code: BOGUS"):
            cart.discount_amount()

    def test_discount_on_empty_cart_is_zero(self):
        cart = Cart(discount_code="SAVE10")
        assert cart.discount_amount() == Decimal("0")


# ─────────────────────────────────────────────
# shipping_cost
# ─────────────────────────────────────────────

class TestShippingCost:
    def test_empty_cart_no_shipping(self, empty_cart):
        assert empty_cart.shipping_cost() == Decimal("0")

    def test_under_threshold_charges_shipping(self, cart_with_one_item):
        assert cart_with_one_item.shipping_cost() == Decimal("5.99")

    def test_at_threshold_free_shipping(self):
        cart = Cart()
        cart.add_item(CartItem("A1", "Widget", Decimal("50.00")))
        assert cart.shipping_cost() == Decimal("0")

    def test_over_threshold_free_shipping(self, cart_over_free_shipping):
        assert cart_over_free_shipping.shipping_cost() == Decimal("0")

    def test_discount_can_push_below_free_shipping_threshold(self):
        """$60 cart with 50% off = $30 after discount → shipping applies."""
        cart = Cart(discount_code="HALF")
        cart.add_item(CartItem("A1", "Widget", Decimal("60.00")))
        assert cart.shipping_cost() == Decimal("5.99")

    def test_discount_keeping_above_threshold_still_free(self):
        """$100 cart with 10% off = $90 after discount → still free shipping."""
        cart = Cart(discount_code="SAVE10")
        cart.add_item(CartItem("A1", "Widget", Decimal("100.00")))
        assert cart.shipping_cost() == Decimal("0")


# ─────────────────────────────────────────────
# total
# ─────────────────────────────────────────────

class TestTotal:
    def test_empty_cart_total_is_zero(self, empty_cart):
        assert empty_cart.total() == Decimal("0")

    def test_single_item_with_shipping(self, cart_with_one_item):
        # $10.00 + $5.99 shipping = $15.99
        assert cart_with_one_item.total() == Decimal("15.99")

    def test_free_shipping_no_discount(self, cart_over_free_shipping):
        # $60.00, no discount, free shipping
        assert cart_over_free_shipping.total() == Decimal("60.00")

    def test_discount_and_shipping(self):
        # $40 cart, 10% off = $36, under $50 → $36 + $5.99 = $41.99
        cart = Cart(discount_code="SAVE10")
        cart.add_item(CartItem("A1", "Widget", Decimal("40.00")))
        assert cart.total() == Decimal("41.99")

    def test_discount_and_free_shipping(self):
        # $100 cart, 10% off = $90, over $50 → $90 + $0 = $90
        cart = Cart(discount_code="SAVE10")
        cart.add_item(CartItem("A1", "Widget", Decimal("100.00")))
        assert cart.total() == Decimal("90.00")
```

### Coverage Summary
- **Functions tested:** add_item, remove_item, subtotal, discount_amount,
  shipping_cost, total
- **Edge cases covered:**
  - Empty cart (all methods)
  - Duplicate product add (quantity merge)
  - Remove nonexistent item (noop)
  - Discount rounding to 2 decimal places
  - Free shipping threshold boundary (at, above, below)
  - Discount pushing total below free shipping threshold
- **Error conditions tested:**
  - Invalid discount code raises ValueError with message
- **Branches covered:** All conditional paths in discount_amount and
  shipping_cost including the discount-affects-shipping interaction
```

## Why This Test Suite Is Good

1. **Organized by method** — each class groups tests for one function,
   making it easy to find what's tested
2. **Names describe behavior** — `test_discount_can_push_below_free_shipping_threshold`
   tells you exactly what scenario is covered without reading the code
3. **AAA pattern** — each test has clear arrange (fixture/setup), act
   (method call), assert (expectation)
4. **Edge cases are the interesting tests** — the boundary between free
   and paid shipping, the rounding behavior, the noop on nonexistent items
5. **Comments explain the math** — `# $40 cart, 10% off = $36` makes the
   assertion self-documenting
6. **Fixtures avoid duplication** — shared setup is in `@pytest.fixture`,
   not copy-pasted across tests
7. **Tests are independent** — no shared state between tests, any test
   can run alone
