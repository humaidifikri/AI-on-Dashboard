import streamlit as st
from utils.login_register import login_page, register_page
from utils.auth_handler import logout, get_user_stats

st.set_page_config(
    page_title="NutriVerse", 
    page_icon="🌐",
    layout="wide", 
    initial_sidebar_state='collapsed'
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .stats-card {
        text-align: center;
        padding: 1rem;
        background: #e3f2fd;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main application logic
if not st.session_state.logged_in:
    # Landing page for non-authenticated users
    st.markdown("""
    <div class="main-header">
        <h1>🌐 NutriVerse</h1>
        <h3>Pemandu AI Mu Untuk Makan Lebih Cerdas</h3>
        <p>Ubah perjalanan kesehatan Anda dengan wawasan nutrisi yang dipersonalisasi</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🔍 Analisis Makanan Cerdas</h4>
            <p>Jelajahi makanan kaya nutrisi dengan rekomendasi berbasis AI</p>
        </div>
        
        <div class="feature-card">
            <h4>📊 Pelacakan Kesehatan Visual</h4>
            <p>Pantau kemajuan Anda dengan dashboard interaktif yang menarik</p>
        </div>
        
        <div class="feature-card">
            <h4>🤖 Insight yang Dipersonalisasi</h4>
            <p>Dapatkan saran nutrisi yang disesuaikan berdasarkan data kesehatan Anda</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show platform statistics
        stats = get_user_stats()
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.markdown(f"""
            <div class="stats-card">
                <h3>{stats['total_users']}</h3>
                <p>Users Registered</p>
            </div>
            """, unsafe_allow_html=True)
        with col_stat2:
            st.markdown(f"""
            <div class="stats-card">
                <h3>{stats['recent_logins']}</h3>
                <p>Active Users</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        tab1, tab2 = st.tabs(["✨ Daftar", "🔑 Masuk"])
        
        with tab1:
            register_page()
        
        with tab2:
            login_page()

else:    
    # Sidebar navigation
    with st.sidebar:
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
    
    # Main content area
    st.markdown(f"""
    <div class="main-header">
        <h1 style="color: white;">Selamat Datang, {st.session_state.username}! 🎉</h1>
        <p>Sudah siap melanjutkan perjalanan body-goals mu?</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.switch_page("pages/Dashboard.py")
    
    with col2:
        if st.button("🔮 Buat Prediksi", use_container_width=True):
            st.switch_page("pages/Prediksi.py")
    
    with col3:
        if st.button("🍎 Analisa dengan AI", use_container_width=True):
            st.switch_page("pages/Rekomendasi.py")
    st.info("💡 **Tip**: Gunakan navigasi sidebar untuk mengakses fitur-fitur di NutriVerse!")