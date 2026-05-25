# app/services/auth_client.py
import httpx
import streamlit as st
from typing import Dict, List, Optional

API_BASE_URL = "http://localhost:9000/api/books"  # adjust if deployed

class BookClient:
    def __init__(self):
        self.client = httpx.Client(base_url=API_BASE_URL)

    def _get_headers(self) -> dict:

        token = st.session_state.get("access_token")
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    # -------------------------------
    # Books Catalog Endpoints
    # -------------------------------
    
    def list_books(self) -> Optional[List[Dict]]:
        """Fetch all books"""
        response = self.client.get("/list-books", headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        st.error("Failed to fetch books")
        return None

    def add_book(self, book_data: dict) -> bool:
        """Admin: Add new book"""
        response = self.client.post("/add-book", json=book_data)
        return response.status_code == 200 or response.status_code == 201

    def update_book(self, book_id: str, updated_data: dict) -> bool:
        """Admin: Update book details"""
        response = self.client.put(f"/update-book/{book_id}", json=updated_data, headers=self._get_headers())
        return response.status_code == 200

    def delete_book(self, book_id: str) -> bool:
        """Admin: Soft delete book"""
        response = self.client.delete(f"/delete-book/{book_id}", headers=self._get_headers())
        return response.status_code == 200

    def filter_books(self, program_related: str = None, title: str = None, semester_available: int = None) -> Optional[List[Dict]]:
        """Filter books by program, title, and semester"""
        params = {}
        if program_related:
            params["program_related"] = program_related
        if title:
            params["title"] = title
        if semester_available is not None:
            params["semester_available"] = semester_available

        response = self.client.get("/filter-books", params=params, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        st.error("Failed to filter books")
        return None

    def get_book_stock(self) -> Optional[Dict]:
        """Get stock update summary"""
        response = self.client.get("/get-book-stock", headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        st.error("Failed to fetch stock info")
        return None
    
    def get_book(self, book_id: str):
        response = self.client.get(f"/get-book/{book_id}")
        if response.status_code == 200:
            return response.json()
        st.error("Failed to Book Info")
        return None