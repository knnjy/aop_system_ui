# aop_system_ui
A Streamlit‑based frontend for the Automated Academic Essentials Service.

This UI communicates with the FastAPI backend using **httpx** and **requests**, and provides **role-based navigation** for **Users** and **Admins**.

---

## 🚀 Features

- **[Streamlit UI](ca://s?q=Streamlit_UI_frontend)** - Interactive dashboard with styled cards and detail views.  
- **[API Communication](ca://s?q=Streamlit_API_communication_with_httpx_and_requests)** → Uses `httpx` and `requests` to fetch catalog, orders, and payments from the backend service.  
- **[Role-based Navbar](ca://s?q=Streamlit_role_based_navbar)** - Two different navigation bars:
  - **User Navbar** → Catalog, Orders, Payments, Account.  
  - **Admin Navbar** → Catalog CRUD, Orders Approval, Order Management, Admin Dashboard.  
- **[Session State](ca://s?q=Streamlit_session_state_usage)** - Maintains login state, selected book, and shopping cart across reruns.  
- **[Custom Styling](ca://s?q=Streamlit_custom_CSS_styling)** → Blue/White/Gold theme with styled book cards and detail boxes.

---

## Getting Started

1. Clone the repo
```bash
git clone https://github.com/your-org/catalog-frontend.git
cd catalog-frontend
```
2. Create Virtual Environment (Optional but Recommended)
```bash 
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```
4. Run Application
```bash
streamlit run app.py
```
 

