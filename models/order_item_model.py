
import datetime
from typing import List, Optional


class OrderItem:
    order_item_id: str
    request_id: str
    product_id: str
    quantity: int
    unit_price: int
    subtotal: int

class OrderRequest:
    request_id: str
    user_id: str
    total_amount: float
    order_items: List[OrderItem]
    status: str
    date_created: datetime
    approved_by: Optional[str] = None 