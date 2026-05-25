# app/services/auth_client.py
import httpx
import streamlit as st
from typing import Dict, List, Optional

API_BASE_URL = "http://localhost:9000/api/uniforms"  # adjust if deployed

class UniformClient:
    def __init__(self):
        self.client = httpx.Client(base_url=API_BASE_URL)

    def _get_headers(self) -> dict:

        token = st.session_state.get("access_token")
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    # -------------------------------
    # Uniform Catalog Endpoints
    # -------------------------------

    def list_uniforms(self) -> Optional[List[Dict]]:
        response = self.client.get("/list-uniforms", headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        st.error("Failed to fetch uniforms")
        return None

    def add_uniform(self, uniform_data: dict) -> bool:
        response = self.client.post("/add-uniform", json=uniform_data, headers=self._get_headers())
        return response.status_code in (200, 201)

    def update_uniform(self, uniform_code: str, update_data: dict) -> bool:
        response = self.client.put(f"/update-uniform/{uniform_code}", json=update_data, headers=self._get_headers())
        return response.status_code == 200

    def delete_uniform(self, product_id: str) -> bool:
        response = self.client.delete(f"/delete-uniform/{product_id}", headers=self._get_headers())
        return response.status_code == 200
    
    def filter_uniforms(self, size: str = None, gender: str = None, uniform_type: str = None) -> Optional[List[Dict]]:
        params = {}
        if size:
            params["size"] = size
        if gender:
            params["gender"] = gender
        if uniform_type:
            params["uniform_type"] = uniform_type

        response = self.client.get("/filter-uniform", params=params, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        st.error("Failed to filter uniforms")
        return None
    
    def get_stocks(self):
        response = self.client.get("/get-uniform-stocks", headers=self._get_headers())
        return response.json()