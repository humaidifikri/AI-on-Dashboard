import pandas as pd
import os
import streamlit as st
import hashlib
import re
from datetime import datetime

USER_DB = "data/users.csv"
DATA_DIR = "data"

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_username(username):
    """Validate username format"""
    if not username:
        return False, "Username tidak boleh kosong"
    if len(username) < 3:
        return False, "Username minimal 3 karakter panjangnya"
    if not re.match("^[a-zA-Z0-9_]+$", username):
        return False, "Username hanya dapat berisi huruf, angka, dan garis bawah"
    return True, "Valid username"

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password tidak kosong"
    if len(password) < 6:
        return False, "Password minimal 6 karakter panjangnya"
    return True, "Valid password"

def init_user_db():
    """Initialize user database CSV file"""
    ensure_data_directory()
    if not os.path.exists(USER_DB):
        df = pd.DataFrame(columns=["username", "password_hash", "created_at", "last_login"])
        df.to_csv(USER_DB, index=False)
        return df
    return pd.read_csv(USER_DB)

def register_user(username, password, confirm_password):
    """Register new user with validation"""
    try:
        # Validate inputs
        username_valid, username_msg = validate_username(username)
        if not username_valid:
            return False, username_msg
        
        password_valid, password_msg = validate_password(password)
        if not password_valid:
            return False, password_msg
        
        if password != confirm_password:
            return False, "Passwords tidak cocok"
        
        # Initialize database
        users = init_user_db()
        
        # Check if username already exists
        if username.lower() in users['username'].str.lower().values:
            return False, "Username sudah ada"
        
        # Hash password and create new user
        password_hash = hash_password(password)
        new_user = pd.DataFrame([{
            "username": username,
            "password_hash": password_hash,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }])
        
        # Add to database using concat instead of append
        users = pd.concat([users, new_user], ignore_index=True)
        users.to_csv(USER_DB, index=False)
        
        # Create user data file
        user_data_path = f"{DATA_DIR}/users_data/{username}.csv"
        user_columns = [
            "tanggal", "berat_badan", "tinggi_badan", "bmi", "kalori_konsumsi",
            "protein_gram", "lemak_gram", "gula_gram", "karbohidrat_gram",
            "air_liter", "stress_level", "jam_tidur", "kualitas_tidur"
        ]
        pd.DataFrame(columns=user_columns).to_csv(user_data_path, index=False)
        
        return True, "Pendaftaran Berhasil"
        
    except Exception as e:
        return False, f"Pendaftaran Gagal: {str(e)}"

def authenticate_user(username, password):
    """Authenticate user with hashed password"""
    try:
        if not username or not password:
            return False, "Perlu Username dan password"
        
        users = init_user_db()
        
        # Find user (case-insensitive)
        user_row = users[users['username'].str.lower() == username.lower()]
        
        if user_row.empty:
            return False, "username atau password salah"
        
        # Verify password
        stored_hash = user_row['password_hash'].iloc[0]
        password_hash = hash_password(password)
        
        if stored_hash != password_hash:
            return False, "username atau password salah"
        
        # Update last login
        users.loc[users['username'].str.lower() == username.lower(), 'last_login'] = datetime.now().isoformat()
        users.to_csv(USER_DB, index=False)
        
        return True, "Berhasil Masuk"
        
    except Exception as e:
        return False, f"Autentikasi Gagal: {str(e)}"

def logout():
    """Clear user session"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()  # Updated from st.experimental_rerun()

def get_user_stats():
    """Get user statistics"""
    try:
        users = init_user_db()
        if users.empty:
            return {"total_users": 0, "recent_logins": 0}
        
        total_users = len(users)
        recent_logins = len(users[users['last_login'].notna()])
        
        return {
            "total_users": total_users,
            "recent_logins": recent_logins
        }
    except:
        return {"total_users": 0, "recent_logins": 0}
