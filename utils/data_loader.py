import pandas as pd
import os
import streamlit as st
from datetime import datetime

DATA_DIR = "data"
USERS_DATA_DIR = "data/users_data"

def ensure_users_data_directory():
    """Create users data directory if it doesn't exist"""
    if not os.path.exists(USERS_DATA_DIR):
        os.makedirs(USERS_DATA_DIR)

def get_user_data_path(username):
    """Get the file path for a specific user's data"""
    ensure_users_data_directory()
    return f"{USERS_DATA_DIR}/{username}.csv"

def init_user_data_file(username):
    """Initialize user data file if it doesn't exist"""
    user_data_path = get_user_data_path(username)
    
    if not os.path.exists(user_data_path):
        # Create empty dataframe with required columns
        user_columns = [
            "tanggal", "berat_badan", "tinggi_badan", "bmi", "kalori_konsumsi",
            "protein_gram", "lemak_gram", "gula_gram", "karbohidrat_gram",
            "air_liter", "stress_level", "jam_tidur", "kualitas_tidur"
        ]
        empty_df = pd.DataFrame(columns=user_columns)
        empty_df.to_csv(user_data_path, index=False)
        return empty_df
    
    return pd.read_csv(user_data_path)

def load_data(username=None):
    """
    Load data for a specific user. If no username provided, 
    try to get from session state or return empty dataframe.
    """
    # Get username from parameter or session state
    if username is None:
        if 'username' in st.session_state and st.session_state.username:
            username = st.session_state.username
        else:
            # Return empty dataframe if no user is logged in
            return pd.DataFrame()
    
    # Initialize user data file if needed
    data = init_user_data_file(username)
    
    # Convert date column to datetime if data exists
    if not data.empty and 'tanggal' in data.columns:
        data['tanggal'] = pd.to_datetime(data['tanggal'], errors='coerce')
    
    return data

def load_filtered_data(start_date=None, end_date=None, filter_tgl="Hari", username=None):
    """
    Load filtered data for a specific user with date and grouping options.
    """
    # Get username from parameter or session state
    if username is None:
        if 'username' in st.session_state and st.session_state.username:
            username = st.session_state.username
        else:
            # Return empty dataframe if no user is logged in
            return pd.DataFrame()
    
    # Load user's data
    data = load_data(username)
    
    # Return empty dataframe if no data
    if data.empty:
        return pd.DataFrame()
    
    # Set default date range if not provided
    if start_date is None:
        start_date = data['tanggal'].min()
    if end_date is None:
        end_date = data['tanggal'].max()
    
    # Define columns for statistical operations
    cols_stats = ['berat_badan', 'tinggi_badan', 'bmi', 'kalori_konsumsi',
                  'protein_gram', 'lemak_gram', 'gula_gram', 'karbohidrat_gram',
                  'air_liter', 'stress_level', 'jam_tidur', 'kualitas_tidur']
    
    # Filter data by date range
    filtered = data[(data['tanggal'] >= start_date) & (data['tanggal'] <= end_date)]
    
    # Group data based on filter_tgl parameter
    if filter_tgl == "Tahun":
        # Group by year and calculate mean values
        filtered = filtered.groupby(filtered['tanggal'].dt.year)[cols_stats].mean().round().reset_index()
        filtered.rename(columns={'tanggal': 'tahun'}, inplace=True)
    elif filter_tgl == "Bulan":
        # Group by year-month and calculate mean values
        filtered = filtered.groupby(filtered['tanggal'].dt.strftime('%Y-%m'))[cols_stats].mean().round().reset_index()
        filtered.rename(columns={'tanggal': 'bulan'}, inplace=True)
    
    return filtered

def save_user_data(username, data):
    """
    Save data for a specific user to their individual CSV file.
    """
    user_data_path = get_user_data_path(username)
    
    # Ensure the data directory exists
    ensure_users_data_directory()
    
    # Save data to CSV
    data.to_csv(user_data_path, index=False)
    
    return True

def add_user_record(username, record_data):
    """
    Add a new record to user's data file.
    record_data should be a dictionary with all required fields.
    """
    try:
        # Load existing data
        existing_data = load_data(username)
        
        # Convert record_data to DataFrame
        new_record = pd.DataFrame([record_data])
        
        # Ensure date column is properly formatted
        if 'tanggal' in new_record.columns:
            new_record['tanggal'] = pd.to_datetime(new_record['tanggal'])
        
        # Combine existing data with new record
        if not existing_data.empty:
            updated_data = pd.concat([existing_data, new_record], ignore_index=True)
        else:
            updated_data = new_record
        
        # Sort by date
        updated_data = updated_data.sort_values('tanggal')
        
        # Save updated data
        save_user_data(username, updated_data)
        
        return True, "Record added successfully"
        
    except Exception as e:
        return False, f"Failed to add record: {str(e)}"

def load_food_data():
    """
    Load nutrition/food data from the global nutrition CSV file.
    This remains unchanged as it's reference data, not user-specific.
    """
    nutrition_file = f"{DATA_DIR}/nutrition.csv"
    
    if os.path.exists(nutrition_file):
        return pd.read_csv(nutrition_file)
    else:
        # Return empty dataframe if file doesn't exist
        return pd.DataFrame()