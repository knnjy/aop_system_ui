import httpx
import streamlit as st
from typing import Optional, Dict, List

API_BASE_URL = "http://localhost:9000/api/orders"

class OrderClient:
    def __init__(self):
        self.client = httpx.Client(base_url=API_BASE_URL)

    def _get_headers(self) -> dict:
        token = st.session_state.get("token")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def list_orders(self) -> List[Dict]:
        """
        Fetch all orders from backend
        IMPORTANT: backend should return LIST of dicts
        """
        try:
            response = self.client.get("/", headers=self._get_headers())

            if response.status_code == 200:
                data = response.json()

                # safety check
                if isinstance(data, list):
                    return data
                return []

            return []

        except Exception as e:
            st.error(f"API error: {e}")
            return []