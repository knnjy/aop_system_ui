# app/services/auth_client.py
import httpx
import streamlit as st
from typing import Optional

API_BASE_URL = "http://localhost:8000/api/auth"  # adjust if deployed

class AuthClient:
    def __init__(self):
        self.client = httpx.Client(base_url=API_BASE_URL)