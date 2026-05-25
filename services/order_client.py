import httpx
import streamlit as st
from typing import Optional, Dict, List

API_BASE_URL = "http://localhost:9000/api/orders"  # adjust if deployed

class OrderClient:
    def __init__(self):
        self.client = httpx.Client(base_url=API_BASE_URL)

    def _get_headers(self) -> dict:
        token = st.session_state.get("access_token")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def add_order(self, order_data: dict) -> Optional[Dict]:
        """User: Place new order"""
        response = self.client.post("/add-order", json=order_data, headers=self._get_headers())
        if response.status_code in (200, 201):
            return response.json()
        st.error("Failed to add order")
        return None

    def list_orders(self) -> Optional[List[Dict]]:
        """Admin: View all orders"""
        response = self.client.get("/list-orders", headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        st.error("Failed to fetch orders")
        return None

    def get_order(self, request_id: str) -> Optional[Dict]:
        """User/Admin: View order details"""
        response = self.client.get(f"/get-order/{request_id}", headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        st.error("Order not found")
        return None

    def update_order(self, request_id: str, update_data: dict) -> bool:
        """Admin: Approve/Reject order"""
        response = self.client.put(f"/update-order/{request_id}", json=update_data, headers=self._get_headers())
        return response.status_code == 200

    def cancel_order(self, request_id: str) -> bool:
        """User: Cancel own order"""
        response = self.client.delete(f"/cancel-order/{request_id}", headers=self._get_headers())
        return response.status_code == 200
    
    def get_product_item(self, product_item_id:str):
        response = self.client.get(f"/get-product-item/{product_item_id}")
        return response.status_code == 200