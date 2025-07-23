import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime
from utils.data_loader import load_filtered_data, load_data,add_user_record 

# Konfigurasi halaman
st.set_page_config(page_title="Main Dashboard", page_icon="🏥", layout="wide",
                   initial_sidebar_state='expanded')

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Silakan login terlebih dahulu untuk mengakses dashboard.")
    st.stop()

# Load user's data
data = load_data()
username = st.session_state.get('username', 'Unknown User')

# Check if user has any data
if data.empty:
    st.title("📊 Dashboard Monitoring Kesehatan")
    st.info(f"👋 Selamat datang, {username}! Anda belum memiliki data kesehatan.")
    st.write("Untuk melihat dashboard yang lengkap, silakan tambahkan data kesehatan Anda terlebih dahulu.")
    
    with st.form("pre_input_data_form"):
        col1, col2, col3 = st.columns(3)

        # Kolom 1: Informasi Umum
        with col1:
            tanggal = st.date_input("Tanggal", value=datetime.today())
            tinggi_badan = st.number_input("Tinggi badan (cm)", min_value=140, max_value=250, value=160)
            berat_badan = st.number_input("Berat Badan (kg)", min_value=30, max_value=150, value=60)

            tb_m = tinggi_badan / 100
            bmi = berat_badan / (tb_m ** 2)
            kalori = st.number_input("Kalori yang Dikonsumsi", min_value=1000, max_value=3500, value=2000)

        # Kolom 2: Kalori & BMR
        with col2:
            protein = st.number_input("Protein yang Dikonsumsi", min_value=0, max_value=200, value=50)
            lemak = st.number_input("Lemak yang Dikonsumsi", min_value=0, max_value=100, value=50)
            gula = st.number_input("Gula yang Dikonsumsi", min_value=0, max_value=100, value=50)
            karbo = st.number_input("Karbohidrat yang Dikonsumsi", min_value=0, max_value=400, value=100)

        # Kolom 3: Aktivitas & Stres
        with col3:
            kualitas_tidur = st.slider("Kualitas Tidur (1-10)", min_value=1, max_value=10)
            stres_level = st.slider("Level Stres (1-10)", min_value=1, max_value=10)
            jam_tidur = st.slider("Total Jam Tidur (5-8)", min_value=5, max_value=8)
            air = st.slider("Air yang Dikonsumsi (1-5 Liter)", min_value=1, max_value=5)

        # Submit button harus di dalam st.form()
        submitted = st.form_submit_button("💾 Simpan Data")

    if submitted:
        record = {
            "tanggal": tanggal,
            "berat_badan": berat_badan,
            "tinggi_badan": tinggi_badan,
            "bmi": round(bmi, 2),
            "kalori_konsumsi": kalori,
            "protein_gram": protein,
            "lemak_gram": lemak,
            "gula_gram": gula,
            "karbohidrat_gram": karbo,
            "air_liter": air,
            "stress_level": stres_level,
            "jam_tidur": jam_tidur,
            "kualitas_tidur": kualitas_tidur
        }

        success, msg = add_user_record(st.session_state.username, record)
        if success:
            st.success("Data berhasil disimpan!")
        else:
            st.error(f"Gagal menyimpan data: {msg}")

    st.stop()   

# If we reach here, user has data - proceed with normal dashboard
# Get date range from actual data
min_date = data['tanggal'].min().date()
max_date = data['tanggal'].max().date()

# Main content
st.title("📊 Dashboard Monitoring Kesehatan")
st.write(f"👋 Selamat datang kembali, **{username}**!")
st.markdown("---")

# Date range selector
col_filter_tgl1, col_filter_tgl2, col_filter_tgl3 = st.columns([2, 2, 1])

with col_filter_tgl1:
    start_date = st.date_input("Tanggal awal", min_date, min_value=min_date, max_value=max_date)

with col_filter_tgl2:
    end_date = st.date_input("Tanggal akhir", max_date, min_value=min_date, max_value=max_date)

with col_filter_tgl3:
    filter_tgl = st.selectbox("Filter tanggal per-", ("Hari", "Bulan", "Tahun"))

# Convert to datetime for filtering
start_date_dt = datetime.combine(start_date, datetime.min.time())
end_date_dt = datetime.combine(end_date, datetime.min.time())

# Filter data using the refactored function
filtered_data = load_filtered_data(start_date_dt, end_date_dt, filter_tgl)

# Store filtered data in session state
st.session_state['filtered_data'] = filtered_data

st.write(f"Menampilkan data dari {start_date.strftime('%d %B %Y')} hingga {end_date.strftime('%d %B %Y')}")

# Check if filtered data is empty
if filtered_data.empty:
    st.warning("⚠️ Tidak ada data dalam rentang tanggal yang dipilih. Coba ubah filter tanggal.")
    st.stop()

# Metrics row - with error handling for edge cases
try:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        last_weight = filtered_data['berat_badan'].iloc[-1]
        first_weight = filtered_data['berat_badan'].iloc[0]
        weight_change = last_weight - first_weight
        st.metric("Berat Badan Terakhir", f"{last_weight} kg", 
                  f"{weight_change:+.1f} kg dari awal")
    
    with col2:
        last_bmi = filtered_data['bmi'].iloc[-1]
        first_bmi = filtered_data['bmi'].iloc[0]
        bmi_change = last_bmi - first_bmi
        st.metric("BMI Terakhir", f"{last_bmi:.2f}", 
                  f"{bmi_change:+.2f} dari awal")
    
    with col3:
        avg_calories = filtered_data['kalori_konsumsi'].mean()
        st.metric("Rata-rata Kalori", f"{avg_calories:.0f} kcal/hari")
    
    with col4:
        avg_sleep = filtered_data['jam_tidur'].mean()
        st.metric("Rata-rata Jam Tidur", f"{avg_sleep:.1f} jam/hari")
        
except (IndexError, KeyError) as e:
    st.error(f"❌ Error dalam menampilkan metrics: {str(e)}")
    st.info("Pastikan data Anda lengkap untuk semua kolom yang diperlukan.")

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Tren Utama", "🍎 Nutrisi", "😴 Tidur & Stres"])

with tab1:
    st.subheader("Tren Kesehatan Utama")
    
    try:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Determine x-axis column based on filter
        if filter_tgl == "Tahun":
            x_col = 'tahun'
            x_label = 'Tahun'
        elif filter_tgl == "Bulan":
            x_col = 'bulan'
            x_label = 'Bulan'
        else:
            x_col = 'tanggal'
            x_label = 'Tanggal'


        # Berat Badan
        sns.lineplot(data=filtered_data, x=x_col, y='berat_badan', ax=axes[0,0], marker='o')
        axes[0,0].set_title('Perkembangan Berat Badan')
        axes[0,0].set_xlabel(x_label)
        axes[0,0].set_ylabel('Berat Badan (kg)')
        axes[0,0].grid(False)
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # BMI
        sns.lineplot(data=filtered_data, x=x_col, y='bmi', ax=axes[0,1], marker='o', color='orange')
        axes[0,1].set_title('Perkembangan BMI')
        axes[0,1].set_xlabel(x_label)
        axes[0,1].set_ylabel('BMI')
        axes[0,1].grid(False)
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Kalori
        sns.lineplot(data=filtered_data, x=x_col, y='kalori_konsumsi', ax=axes[1,0], marker='o', color='green')
        axes[1,0].set_title('Konsumsi Kalori Harian')
        axes[1,0].set_xlabel(x_label)
        axes[1,0].set_ylabel('Kalori (kcal)')
        axes[1,0].grid(False)
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Air
        sns.lineplot(data=filtered_data, x=x_col, y='air_liter', ax=axes[1,1], marker='o', color='blue')
        axes[1,1].set_title('Konsumsi Air Harian')
        axes[1,1].set_xlabel(x_label)
        axes[1,1].set_ylabel('Air (Liter)')
        axes[1,1].grid(False)
        axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"❌ Error dalam membuat grafik tren utama: {str(e)}")
        st.info("Periksa apakah data Anda memiliki semua kolom yang diperlukan.")

with tab2:
    st.subheader("Analisis Nutrisi")
    
    try:
        st.write(f"#### Rata-rata Konsumsi per-{filter_tgl}")
        nutri_avg = filtered_data[['protein_gram', 'lemak_gram', 'karbohidrat_gram', 'gula_gram']].mean()
        fig, ax = plt.subplots(figsize=(8, 3))
        nutri_avg.plot(kind='bar', ax=ax, color=['red', 'yellow', 'green', 'purple'])
        ax.set_title(f'Rata-rata Konsumsi Nutrisi {filter_tgl}an')
        ax.set_ylabel('Gram')
        ax.set_xlabel('Jenis Nutrisi')
        ax.grid(False)
        ax.tick_params(axis='x', rotation=0)
        st.pyplot(fig)
        
        st.write("#### Tren Konsumsi Nutrisi")
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Determine x-axis column based on filter
        if filter_tgl == "Tahun":
            x_col = 'tahun'
            x_label = 'Tahun'
        elif filter_tgl == "Bulan":
            x_col = 'bulan'
            x_label = 'Bulan'
        else:
            x_col = 'tanggal'
            x_label = 'Tanggal'
            
        sns.lineplot(data=filtered_data, x=x_col, y='protein_gram', label='Protein', ax=ax, marker='o')
        sns.lineplot(data=filtered_data, x=x_col, y='lemak_gram', label='Lemak', ax=ax, marker='o')
        sns.lineplot(data=filtered_data, x=x_col, y='karbohidrat_gram', label='Karbohidrat', ax=ax, marker='o')
        sns.lineplot(data=filtered_data, x=x_col, y='gula_gram', label='Gula', ax=ax, marker='o')
        ax.set_title(f'Tren Konsumsi Nutrisi {filter_tgl}an')
        ax.set_xlabel(x_label)
        ax.set_ylabel('Gram')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(False)
        ax.legend()
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"❌ Error dalam analisis nutrisi: {str(e)}")
        st.info("Pastikan data nutrisi Anda lengkap.")

with tab3:
    st.subheader("Tidur dan Tingkat Stres")
    
    try:
        st.write("#### Kualitas dan Durasi Tidur")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax2 = ax.twinx()
        
        # Determine x-axis column based on filter
        if filter_tgl == "Tahun":
            x_col = 'tahun'
            x_label = 'Tahun'
        elif filter_tgl == "Bulan":
            x_col = 'bulan'
            x_label = 'Bulan'
        else:
            x_col = 'tanggal'
            x_label = 'Tanggal'
            
        sns.lineplot(data=filtered_data, x=x_col, y='jam_tidur', color='blue', label='Jam Tidur', ax=ax, marker='o')
        sns.lineplot(data=filtered_data, x=x_col, y='kualitas_tidur', color='green', label='Kualitas Tidur', ax=ax2, marker='o')
        ax.set_title(f'Tren Tidur {filter_tgl}an')
        ax.set_xlabel(x_label)
        ax.set_ylabel('Jam Tidur', color='blue')
        ax2.set_ylabel('Kualitas Tidur (1-10)', color='green')
        ax.grid(False)
        ax.tick_params(axis='x', rotation=45)
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        st.pyplot(fig)
        
        st.write("#### Tingkat Stres")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=filtered_data, x=x_col, y='stress_level', color='red', marker='o', ax=ax)
        ax.set_title(f'Tren Tingkat Stres {filter_tgl}an (1-10)')
        ax.set_xlabel(x_label)
        ax.set_ylabel('Tingkat Stres')
        ax.grid(False)
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"❌ Error dalam analisis tidur dan stres: {str(e)}")
        st.info("Pastikan data tidur dan stres Anda lengkap.")

with st.expander("Masukan data hari ini"):
    with st.form("input_data_form"):
        col1, col2, col3 = st.columns(3)

        # Kolom 1: Informasi Umum
        with col1:
            tanggal = st.date_input("Tanggal", value=datetime.today())
            tinggi_badan = st.number_input("Tinggi badan (cm)", min_value=140, max_value=250, value=160)
            berat_badan = st.number_input("Berat Badan (kg)", min_value=30, max_value=150, value=60)

            tb_m = tinggi_badan / 100
            bmi = berat_badan / (tb_m ** 2)
            kalori = st.number_input("Kalori yang Dikonsumsi", min_value=1000, max_value=3500, value=2000)

        # Kolom 2: Kalori & BMR
        with col2:
            protein = st.number_input("Protein yang Dikonsumsi", min_value=0, max_value=200, value=50)
            lemak = st.number_input("Lemak yang Dikonsumsi", min_value=0, max_value=100, value=50)
            gula = st.number_input("Gula yang Dikonsumsi", min_value=0, max_value=100, value=50)
            karbo = st.number_input("Karbohidrat yang Dikonsumsi", min_value=0, max_value=400, value=100)

        # Kolom 3: Aktivitas & Stres
        with col3:
            kualitas_tidur = st.slider("Kualitas Tidur (1-10)", min_value=1, max_value=10)
            stres_level = st.slider("Level Stres (1-10)", min_value=1, max_value=10)
            jam_tidur = st.slider("Total Jam Tidur (5-8)", min_value=5, max_value=8)
            air = st.slider("Air yang Dikonsumsi (1-5 Liter)", min_value=1, max_value=5)

        # Submit button harus di dalam st.form()
        submitted = st.form_submit_button("💾 Simpan Data")

    if submitted:
        record = {
            "tanggal": tanggal,
            "berat_badan": berat_badan,
            "tinggi_badan": tinggi_badan,
            "bmi": round(bmi, 2),
            "kalori_konsumsi": kalori,
            "protein_gram": protein,
            "lemak_gram": lemak,
            "gula_gram": gula,
            "karbohidrat_gram": karbo,
            "air_liter": air,
            "stress_level": stres_level,
            "jam_tidur": jam_tidur,
            "kualitas_tidur": kualitas_tidur
        }

        success, msg = add_user_record(st.session_state.username, record)
        if success:
            st.success("Data berhasil disimpan!")
        else:
            st.error(f"Gagal menyimpan data: {msg}")

# Footer with dynamic last update


st.markdown("---")
if not data.empty:
    last_update = data['tanggal'].max().strftime('%d %B %Y')
    st.caption(f"Dashboard Kesehatan © 2025 - Data diperbarui terakhir pada {last_update}")
else:
    st.caption("Dashboard Kesehatan © 2025 - Menunggu data kesehatan Anda")