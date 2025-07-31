import streamlit as st
import plotly.express as px
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Rectangle
from utils.prediction import predict
from utils.data_loader import load_data,load_food_data

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Silakan login terlebih dahulu untuk mengakses dashboard.")
    st.stop()

df = load_food_data()
user_data = load_data()
username = st.session_state.get('username', 'Unknown User')

st.set_page_config(page_title="Prediksi", page_icon="🏥", layout="wide",
                   initial_sidebar_state='collapsed')

if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

# filtered_data = load_filtered_data()  # default full range
# if 'filtered_data' in st.session_state:
#         filtered_data = st.session_state['filtered_data']
# else:
#     st.warning("Data belum difilter. Buka halaman Dashboard dulu.")
#     filtered_data = pd.DataFrame()

st.title("Prediksi Tujuan Mu!")

st.markdown("Masukkan datamu, dan biarkan AI NutriVerse hitung kebutuhanmu.")

with st.form("prediction_form"):
    st.subheader("🧠 Formulir Prediksi")

    col1, col2, col3 = st.columns(3)

    # Kolom 1: Informasi Umum
    with col1:
        tinggi_badan = st.number_input("Tinggi badan (cm)", min_value=140, max_value=250, value=160)
        berat_badan = st.number_input("Berat Badan (kg)", min_value=30, max_value=150, value=60)
        
        # tinggi cm ke M
        tb_m = tinggi_badan / 100 
        tb2 = tb_m * tb_m
        bmi = berat_badan / tb2
        
        st.metric("BMI", f"{bmi:.2f}")
        kalori = st.number_input("Kalori yang Dikonsumsi", min_value=1000, max_value=3500, value=2000)
        
        submitted = st.form_submit_button("🔍 Prediksi")        

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

    # Data prediksi (1 baris)
    data_pred = pd.DataFrame([{'berat_badan':berat_badan, 
                               'tinggi_badan':tinggi_badan, 
                               'bmi':bmi, 
                               'kalori_konsumsi':kalori,
                                'protein_gram':protein, 
                                'lemak_gram':lemak, 
                                'gula_gram':gula, 
                                'karbohidrat_gram':karbo,
                                'air_liter':air,
                                'stress_level':stres_level,
                                'jam_tidur':jam_tidur, 
                                'kualitas_tidur':kualitas_tidur}])

    if submitted:
    #     st.session_state.prediction_result = predict(data_pred).round()

    # # Tampilkan hasil prediksi
    # if st.session_state.prediction_result is not None:
        user_data['tanggal'] = pd.to_datetime(user_data['tanggal'])
        last_7_days = user_data[user_data['tanggal'] >= user_data['tanggal'].max() - pd.Timedelta(days=6)]
        
        result = predict(data_pred).round()
        fig, ax = plt.subplots(figsize=(6,3))

        sns.lineplot(data=last_7_days, x='tanggal', y='berat_badan', label='Aktual', marker='o', ax=ax)

        last_tanggal = user_data['tanggal'].max()
        pred_weight = result
        
        ax.scatter(last_tanggal + pd.Timedelta(days=1), pred_weight, color='red', label='Prediksi', zorder=5)
        ax.set_title("Perkembangan Berat Badan + Prediksi")
        ax.set_xlabel("Tanggal")
        ax.set_ylabel("Berat Badan (kg)")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(False)
        ax.legend()
        st.pyplot(fig)

        # Set style untuk matplotlib dan seaborn
plt.style.use('default')
sns.set_palette("husl")

with st.expander("Pilih Makanan yang cocok untuk Mu!"):
    # Title and description
    st.title("🍏 Penuhi Gizi Mu!")
    st.markdown("Jelajahi informasi nutrisi untuk berbagai makanan")
    st.markdown("---")

    # Sidebar filters
    st.markdown(f"Opsi Filter")

    col1, col2, col3 = st.columns([1,1,2])
    # Nutrient selection
    with col1:
        nutrients = ['calories', 'proteins', 'fat', 'carbohydrate']
        selected_nutrient = st.selectbox("Select Nutrient to Analyze", nutrients)

    
    # Category selection (based on name patterns)
    with col2:
        categories = ['All', 'Meat', 'Vegetable', 'Fruit', 'Seafood', 'Dairy', 'Grain']
        selected_category = st.selectbox("Select Food Category", categories)

    # Apply category filter
    if selected_category != 'All':
        if selected_category == 'Meat':
            filtered_df = df[df['name'].str.contains('ayam|sapi|daging|babi|bebek|domba|kambing', case=False)]
        elif selected_category == 'Vegetable':
            filtered_df = df[df['name'].str.contains('daun|sayur|kangkung|bayam|kacang|wortel', case=False)]
        elif selected_category == 'Fruit':
            filtered_df = df[df['name'].str.contains('apel|jeruk|mangga|pisang|anggur|semangka', case=False)]
        elif selected_category == 'Seafood':
            filtered_df = df[df['name'].str.contains('ikan|udang|cumi|kepiting|kerang', case=False)]
        elif selected_category == 'Dairy':
            filtered_df = df[df['name'].str.contains('keju|susu|yogurt', case=False)]
        elif selected_category == 'Grain':
            filtered_df = df[df['name'].str.contains('beras|jagung|gandum|oat', case=False)]
    else:
        filtered_df = df.copy()

    # Slider for nutrient range
    min_val = int(filtered_df[selected_nutrient].min())
    max_val = int(filtered_df[selected_nutrient].max())
    with col3:
        nutrient_range = st.slider(f"Select {selected_nutrient} range", min_val, max_val, (min_val, max_val))
        filtered_df = filtered_df[
            (filtered_df[selected_nutrient] >= nutrient_range[0]) & 
            (filtered_df[selected_nutrient] <= nutrient_range[1])
        ]

    # Main dashboard
    tab1, tab2 = st.tabs(["Nutrient Analysis", "Food Explorer"])

    with tab1:
        st.header("Nutrition Overview")
        st.subheader("Top 10 Highest " + selected_nutrient.capitalize())

        top_10 = filtered_df.nlargest(10, selected_nutrient)[['name', selected_nutrient]]
        
        # Matplotlib horizontal bar chart
        fig1, ax = plt.subplots(figsize=(15, 8))
        y_pos = np.arange(len(top_10))
        bars = ax.barh(y_pos, top_10[selected_nutrient], 
                        color=sns.color_palette("viridis", len(top_10)))
        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_10['name'], fontsize=10)
        ax.set_xlabel(f'{selected_nutrient.capitalize()}', fontsize=12)
        ax.set_title(f'Top 10 Foods by {selected_nutrient.capitalize()}', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(top_10[selected_nutrient]):
            ax.text(v + max(top_10[selected_nutrient]) * 0.01, i, f'{v:.1f}', 
                    va='center', ha='left', fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close()

        st.subheader("Macronutrient Ratio")
        top_10['protein_ratio'] = filtered_df['proteins'] / (filtered_df['proteins'] + filtered_df['fat'] + filtered_df['carbohydrate']) * 100
        top_10['fat_ratio'] = filtered_df['fat'] / (filtered_df['proteins'] + filtered_df['fat'] + filtered_df['carbohydrate']) * 100
        top_10['carb_ratio'] = filtered_df['carbohydrate'] / (filtered_df['proteins'] + filtered_df['fat'] + filtered_df['carbohydrate']) * 100
        
        # # Stacked horizontal bar chart
        # sample_df = filtered_df.head(10)
        
        fig2, ax = plt.subplots(figsize=(15, 8))
        
        # Create stacked bars
        protein_bars = ax.barh(range(len(top_10)), top_10['protein_ratio'], 
                                label='Protein', color='#FF6B6B', alpha=0.8)
        fat_bars = ax.barh(range(len(top_10)), top_10['fat_ratio'], 
                            left=top_10['protein_ratio'], label='Fat', 
                            color='#4ECDC4', alpha=0.8)
        carb_bars = ax.barh(range(len(top_10)), top_10['carb_ratio'], 
                            left=top_10['protein_ratio'] + top_10['fat_ratio'], 
                            label='Carbohydrates', color='#45B7D1', alpha=0.8)
        
        ax.set_yticks(range(len(top_10)))
        ax.set_yticklabels(top_10['name'], fontsize=10)
        ax.set_xlabel('Percentage (%)', fontsize=12)
        ax.set_title('Macronutrient Distribution (Top 10 Foods)', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right')
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

    with tab2:
        st.header("Food Item Explorer")
        
        search_term = st.text_input("Search for food items", "")
        if search_term:
            search_results = filtered_df[filtered_df['name'].str.contains(search_term, case=False)]
        else:
            search_results = filtered_df.copy()
        
        if not search_results.empty:
            st.dataframe(search_results[['name', 'calories', 'proteins', 'fat', 'carbohydrate']].sort_values(by='calories', ascending=False).reset_index(drop=True))
            
            selected_food = st.selectbox("Select a food for detailed view", search_results['name'])
            food_details = search_results[search_results['name'] == selected_food].iloc[0]
            
            # Nutrient metrics display
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Calories", f"{food_details['calories']} kcal")
            col2.metric("Protein", f"{food_details['proteins']}g")
            col3.metric("Fat", f"{food_details['fat']}g")
            col4.metric("Carbohydrates", f"{food_details['carbohydrate']}g")
            
            # Detailed nutrient breakdown chart
            st.subheader(f"Nutrient Breakdown for {selected_food}")
            
            # Pie chart for macronutrients
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Pie chart
            nutrients_values = [food_details['proteins'], food_details['fat'], food_details['carbohydrate']]
            nutrients_labels = ['Proteins', 'Fat', 'Carbohydrates']
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            wedges, texts, autotexts = ax1.pie(nutrients_values, labels=nutrients_labels, 
                                              colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.set_title(f'Macronutrient Distribution\n{selected_food}', fontsize=12, fontweight='bold')
            
            # Bar chart for all nutrients
            all_nutrients = ['calories', 'proteins', 'fat', 'carbohydrate']
            all_values = [food_details[nutrient] for nutrient in all_nutrients]
            
            bars = ax2.bar(all_nutrients, all_values, 
                          color=['#FFA07A', '#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.8)
            ax2.set_ylabel('Amount', fontsize=12)
            ax2.set_title(f'All Nutrients\n{selected_food}', fontsize=12, fontweight='bold')
            ax2.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for bar, value in zip(bars, all_values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + max(all_values) * 0.01,
                        f'{value:.1f}', ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
            # Display image if available
            if not pd.isna(food_details['image']):
                st.image(food_details['image'], caption=selected_food, width=400)
        else:
            st.warning("No food items found matching your search.")