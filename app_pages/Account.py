import streamlit as st

def show():
    # Page configuration
    # Custom CSS styling
    st.markdown("""
    <style>
    .stApp {font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;}
    h1 {color:#1e3a8a;font-weight:700;}
    .card,.left-card {
        background:#fff;border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,.1);padding:25px;
    }
    .banner {
        background:linear-gradient(90deg,#1e3a8a 0%,#3b82f6 40%,#eab308 100%);
        height:130px;border-radius:10px 10px 0 0;
        display:flex;justify-content:center;align-items:center;position:relative;
    }
    .avatar {
        background:#1e3a8a;
        color:#fff;
        font-size:40px;
        font-weight:700;
        border-radius:50%;
        width:130px;
        height:130px;
        display:flex;
        align-items:center;
        justify-content:center;
        border:4px solid #fff;
        position:absolute;
        bottom:-40px;
    }
    .student-name {
        font-size:20px;
        font-weight:700;
        color:#1e3a8a;
        margin-top:20px;
    }
    .student-subtitle {
        font-size:14px;
        color:#475569;
        margin-bottom:20px;
    }
    .info-row {
        display:flex;
        justify-content:space-between;
        margin-bottom:10px;
    }
    .label {
        font-weight:600;
        color:#1e40af;
    }
    .value {
        color:#334155;
    }
    .status {
        color:#16a34a;
        font-weight:600;
    }
    .input-field {
        border:1.5px solid #e2e8f0;
        border-radius:6px;
        padding:10px;
        width:100%;
    }
    
    </style>
    """, unsafe_allow_html=True)
    user = st.session_state.user_data
    # Demo data
    first_name = user.get("Name", "Regie")
    student_id, status, year_level, department = user.get("Student ID"), user.get("status", "Active Regular"), user.get("Year Level"), user.get("Program")
    email, sex, address = user.get("Email"), user.get("Sex"), user.get("Block Section")
    course = user.get("Course")
    age = user.get("Age")

    # Page title
    st.markdown("<h1>Account Info</h1>", unsafe_allow_html=True)

    # Layout: even cards
    col1, col2 = st.columns([1, 1.3])

    # Left card (Academic Info)
    with col1:
        st.markdown(f"""
        <div class="left-card">
            <div class="banner"><div class="avatar">👤</div></div>
            <div style="text-align:center; padding:20px;">
                <div class="student-name">{first_name} </div>
                <div class="student-subtitle">{course}</div>
                <div class="info-row"><div class="label">Student ID:</div><div class="value">{student_id}</div></div>
                <div class="info-row"><div class="label">Portal Status:</div><div class="status">{status}</div></div>
                <div class="info-row"><div class="label">Year Level:</div><div class="value">{year_level}</div></div>
                <div class="info-row"><div class="label">Program:</div><div class="value">{department}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Right card (Personal Coordinates)
    with col2:
        st.markdown(f"""
        <div class="card">
            <h4 style="color:#1e3a8a;">Personal Coordinates</h4>
            <div class="info-row">
                <div style="width:48%;"><div class="label">Full Name</div><input class="input-field" value="{first_name}" readonly></div>
            </div>
            <div class="info-row">
                <div style="width:48%;"><div class="label">Email Address</div><input class="input-field" value="{email}" readonly></div>
                <div style="width:48%;"><div class="label">Sex</div><input class="input-field" value="{sex}" readonly></div>
            </div>
            <div class="info-row">
                <div style="width:100%;"><div class="label">Block Section</div><input class="input-field" value="{address}" readonly></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
