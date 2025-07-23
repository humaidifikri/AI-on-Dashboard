import streamlit as st
from utils.auth_handler import register_user, authenticate_user

def login_page():
    """Optimized login page with better UX"""
    st.subheader("🔐 Sign In to NutriVerse")
    
    with st.form("login_form"):
        username = st.text_input(
            "Username", 
            placeholder="Enter your username",
            help="Your NutriVerse username"
        )
        password = st.text_input(
            "Password", 
            type="password",
            placeholder="Enter your password",
            help="Your account password"
        )
        
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            with st.spinner("Authenticating..."):
                success, message = authenticate_user(username, password)
                
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome back, {username}! 🎉")
                    st.rerun()
                else:
                    st.error(message)

def register_page():
    """Optimized registration page with validation"""
    st.subheader("📝 Create Your NutriVerse Account")
    
    with st.form("register_form"):
        username = st.text_input(
            "Username", 
            placeholder="Choose a username (3+ characters)",
            help="Only letters, numbers, and underscores allowed"
        )
        password = st.text_input(
            "Password", 
            type="password",
            placeholder="Create a strong password (6+ characters)",
            help="Use a mix of letters, numbers, and symbols"
        )
        confirm_password = st.text_input(
            "Confirm Password", 
            type="password",
            placeholder="Confirm your password",
            help="Re-enter your password to confirm"
        )
        
        # Terms acceptance
        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        
        if submitted:
            if not terms_accepted:
                st.error("Please accept the Terms of Service to continue")
                return
            
            with st.spinner("Creating your account..."):
                success, message = register_user(username, password, confirm_password)
                
                if success:
                    st.success("🎉 Account created successfully! You can now sign in.")
                    st.balloons()
                else:
                    st.error(message)