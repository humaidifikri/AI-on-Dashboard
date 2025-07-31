import streamlit as st
from utils.auth_handler import register_user, authenticate_user

def login_page():
    """Optimized login page with better UX"""
    st.subheader("🔐 Masuk ke NutriVerse")
    
    with st.form("login_form"):
        username = st.text_input(
            "Username", 
            placeholder="Masukkan username",
            help="username NutriVerse"
        )
        password = st.text_input(
            "Password", 
            type="password",
            placeholder="Masukkan password",
            help="password akun mu"
        )
        
        submitted = st.form_submit_button("Masuk", use_container_width=True)
        
        if submitted:
            with st.spinner("Meng-autentikasi..."):
                success, message = authenticate_user(username, password)
                
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Selamat Datang, {username}! 🎉")
                    st.rerun()
                else:
                    st.error(message)

def register_page():
    """Optimized registration page with validation"""
    st.subheader("📝 Buat akun NutriVerse")
    
    with st.form("register_form"):
        username = st.text_input(
            "Username", 
            placeholder="tentukan username (3+ karakter)",
            help="Hanya huruf, angka, dan underscore yang diizinkan"
        )
        password = st.text_input(
            "Password", 
            type="password",
            placeholder="Buat password yang kuat (6+ characters)",
            help="Gunakan campuran huruf, angka, dan simbol"
        )
        confirm_password = st.text_input(
            "Confirm Password", 
            type="password",
            placeholder="Konfirmasi password mu",
            help="Masukkan kembali password mu"
        )
        
        # Terms acceptance
        terms_accepted = st.checkbox("Saya setuju dengan Ketentuan Layanan dan Kebijakan Privasi")
        
        submitted = st.form_submit_button("Buat Akun", use_container_width=True)
        
        if submitted:
            if not terms_accepted:
                st.error("Harap terima Persyaratan Layanan untuk melanjutkan")
                return
            
            with st.spinner("Membuat akun mu..."):
                success, message = register_user(username, password, confirm_password)
                
                if success:
                    st.success("🎉 Akun telah berhasil dibuat, Silahkan Masuk!")
                    st.balloons()
                else:
                    st.error(message)