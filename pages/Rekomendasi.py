import streamlit as st

from datetime import datetime
from utils.pdf_converter import get_download_link, generate_pdf
from utils.auto_insight import auto_insight_from_ai
from utils.data_loader import load_data

st.set_page_config(page_title="Rekomendasi", page_icon="🏥", layout="wide",
                   initial_sidebar_state='collapsed')

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Silakan login terlebih dahulu untuk mengakses halaman rekomendasi.")
    st.stop()

# Load data
data = load_data()
username = st.session_state.get('username', 'Pengguna')

if data.empty:
    st.title("💡 Rekomendasi Kesehatan")
    st.info("📊 Anda belum memiliki data kesehatan. Silakan tambahkan data di halaman Dashboard terlebih dahulu untuk mendapatkan rekomendasi personal.")
    st.stop()

# Main title and welcome
st.title("💡 Rekomendasi Kesehatan Personal")
st.markdown(f"### Halo **{username}**! 👋")
st.markdown("Dapatkan insight dan rekomendasi berdasarkan data kesehatan Anda")

# Quick health stats
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    latest_weight = data['berat_badan'].iloc[-1]
    weight_trend = "📈" if data['berat_badan'].iloc[-1] > data['berat_badan'].iloc[0] else "📉"
    st.metric("Berat Terkini", f"{latest_weight} kg", delta=f"{weight_trend}")

with col2:
    avg_stress = data['stress_level'].mean()
    stress_status = "😰 Tinggi" if avg_stress >= 7 else "😊 Normal" if avg_stress >= 4 else "😌 Rendah"
    st.metric("Rata-rata Stres", f"{avg_stress:.1f}/10", delta=stress_status)

with col3:
    avg_sleep = data['jam_tidur'].mean()
    sleep_status = "😴 Kurang" if avg_sleep < 7 else "✅ Baik"
    st.metric("Rata-rata Tidur", f"{avg_sleep:.1f} jam", delta=sleep_status)

with col4:
    latest_bmi = data['bmi'].iloc[-1]
    if latest_bmi < 18.5:
        bmi_status = "⚖️ Underweight"
    elif latest_bmi < 25:
        bmi_status = "✅ Normal"
    elif latest_bmi < 30:
        bmi_status = "⚠️ Overweight"
    else:
        bmi_status = "🔴 Obesitas"
    st.metric("BMI Terkini", f"{latest_bmi:.1f}", delta=bmi_status)

st.markdown("---")

# Two main sections
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("### 🎯 Analisis AI")
    st.markdown("Klik tombol di bawah untuk mendapatkan insight mendalam dari data kesehatan Anda")
    
    # AI Insight Button
    if st.button("🧠 Analisis dengan AI", type="primary", use_container_width=True):
        with st.spinner("🤖 AI sedang menganalisis data Anda..."):
            # Prepare data summary for AI
            data_summary = {
                "total_records": len(data),
                "date_range": f"{data['tanggal'].min().strftime('%Y-%m-%d')} hingga {data['tanggal'].max().strftime('%Y-%m-%d')}",
                "weight_range": f"{data['berat_badan'].min():.1f} - {data['berat_badan'].max():.1f} kg",
                "avg_bmi": f"{data['bmi'].mean():.1f}",
                "avg_calories": f"{data['kalori_konsumsi'].mean():.0f} kcal/hari",
                "avg_protein": f"{data['protein_gram'].mean():.1f}g/hari",
                "avg_sleep": f"{data['jam_tidur'].mean():.1f} jam/hari",
                "avg_stress": f"{data['stress_level'].mean():.1f}/10",
                "avg_sleep_quality": f"{data['kualitas_tidur'].mean():.1f}/10"
            }
            
            insight = auto_insight_from_ai(data_summary)

        # Display AI insight
        with st.container(border=True):
            st.markdown("#### 🧠 Hasil Analisis AI")
            st.markdown("✨ **Insight berdasarkan data Anda:**")
            st.markdown(insight)
            
            # PDF Download
            st.markdown("---")
            pdf_path = generate_pdf(insight)
            st.markdown(
                get_download_link(pdf_path, "📥 Download Insight sebagai PDF"), 
                unsafe_allow_html=True
            )

with col_right:
    st.markdown("### 📋 Rekomendasi Personal")
    
    # General recommendations based on data
    recommendations = []
    
    # BMI recommendations
    latest_bmi = data['bmi'].iloc[-1]
    if latest_bmi < 18.5:
        recommendations.append("🍎 **Nutrisi**: Tingkatkan asupan kalori sehat dan protein")
    elif latest_bmi > 25:
        recommendations.append("🏃 **Aktivitas**: Perbanyak olahraga dan kurangi kalori harian")
    else:
        recommendations.append("✅ **BMI**: Pertahankan pola hidup sehat yang sudah baik")
    
    # Sleep recommendations
    avg_sleep = data['jam_tidur'].mean()
    if avg_sleep < 7:
        recommendations.append("😴 **Tidur**: Tambah durasi tidur minimal 7-8 jam per hari")
    else:
        recommendations.append("✅ **Tidur**: Pertahankan pola tidur yang sudah baik")
    
    # Stress recommendations
    avg_stress = data['stress_level'].mean()
    if avg_stress >= 6:
        recommendations.append("🧘 **Stres**: Coba teknik relaksasi atau meditasi")
    elif avg_stress >= 4:
        recommendations.append("😊 **Stres**: Jaga keseimbangan work-life balance")
    else:
        recommendations.append("✅ **Stres**: Level stres Anda terkendali dengan baik")
    
    # Water intake
    avg_water = data['air_liter'].mean()
    if avg_water < 2:
        recommendations.append("💧 **Hidrasi**: Tingkatkan konsumsi air minimal 2L per hari")
    else:
        recommendations.append("✅ **Hidrasi**: Konsumsi air Anda sudah mencukupi")
    
    # Display recommendations
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")

# Progress tracking
st.markdown("---")
st.markdown("### 📈 Progress Tracking")

# Calculate progress metrics
if len(data) > 7:  # If we have more than a week of data
    recent_data = data.tail(7)
    older_data = data.iloc[-14:-7] if len(data) >= 14 else data.head(7)
    
    weight_progress = recent_data['berat_badan'].mean() - older_data['berat_badan'].mean()
    sleep_progress = recent_data['jam_tidur'].mean() - older_data['jam_tidur'].mean()
    stress_progress = older_data['stress_level'].mean() - recent_data['stress_level'].mean()  # Lower is better
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Perubahan Berat (7 hari)", 
                 f"{weight_progress:+.1f} kg",
                 delta="Baik" if abs(weight_progress) < 0.5 else "Perhatian")
    
    with col2:
        st.metric("Perubahan Tidur (7 hari)", 
                 f"{sleep_progress:+.1f} jam",
                 delta="Baik" if sleep_progress >= 0 else "Kurang")
    
    with col3:
        st.metric("Perubahan Stres (7 hari)", 
                 f"{stress_progress:+.1f} poin",
                 delta="Baik" if stress_progress >= 0 else "Tinggi")

else:
    st.info("📊 Tambahkan lebih banyak data untuk melihat progress tracking")

# Footer
st.markdown("---")
current_date = datetime.now().strftime('%d %B %Y')
total_days = len(data)
st.caption(f"💡 Rekomendasi diperbarui pada {current_date} • Total {total_days} hari data kesehatan")
st.caption("⚠️ **Disclaimer**: Rekomendasi ini bersifat umum. Konsultasikan dengan dokter untuk saran medis spesifik.")