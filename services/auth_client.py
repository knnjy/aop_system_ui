import httpx
import streamlit as st
from typing import Optional, Dict
from jose import jwt

API_BASE_URL = "http://localhost:9000/api/auth"  # adjust if deployed

SECRET_KEY = "supersecretkey" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2

class AuthClient:
    def __init__(self):
        self.client = httpx.Client(base_url=API_BASE_URL)

    def _get_headers(self) -> dict:
        token = st.session_state.get("token")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def login(self, username: str, password: str) -> Optional[Dict]:
        payload = {"username": username, "password": password}
        response = self.client.post("/login", json=payload)

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")

            # Decode JWT to extract role and user info
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            st.session_state["access_token"] = token
            st.session_state["role"] = decoded.get("role")
            st.session_state["user_id"] = decoded.get("account_id")
            st.session_state["user_data"] = decoded.get("user_data")

            return decoded   # return full claims for debugging

        st.error("Login failed")
        return None

    # def register(self, username: str, password: str, role: str = "User") -> bool:
    #     """Register a new user (Admin can assign role)"""
    #     payload = {"username": username, "password": password, "role": role}
    #     response = self.client.post("/register", json=payload)
    #     return response.status_code == 201

    def get_profile(self) -> Optional[Dict]:
        """Fetch current user profile"""
        response = self.client.get("/get-student-data", headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        st.error("Failed to fetch profile")
        return None

    def update_profile(self, profile_data: dict) -> bool:
        """Update user profile"""
        response = self.client.put("/profile", json=profile_data, headers=self._get_headers())
        return response.status_code == 200

    def logout(self) -> bool:
        """Clear session and call backend logout"""
        response = self.client.post("/logout", headers=self._get_headers())
        if response.status_code == 200:
            st.session_state.clear()
            return True
        return False
