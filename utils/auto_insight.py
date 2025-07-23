import streamlit as st
import requests

def auto_insight_from_ai(data):
    CEREBRAS_TOKEN = st.secrets["token"]  # Ganti dengan token Cerebras
    API_URL = "https://api.cerebras.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {CEREBRAS_TOKEN}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "system",
            "content": "Anda adalah ahli gizi profesional yang memberikan analisis data kesehatan dengan insight yang akurat dan mudah dipahami."
        },
        {
            "role": "user",
            "content": f"""
                Analisis data kesehatan saya dan berikan 5 insight utama:

                {data}

                FORMAT JAWABAN:
                1. [Insight pertama dalam 1-2 kalimat singkat]
                2. [Insight kedua dalam 1-2 kalimat singkat] 
                3. [Insight ketiga dalam 1-2 kalimat singkat]
                4. [Insight keempat dalam 1-2 kalimat singkat]
                5. [Insight kelima dalam 1-2 kalimat singkat]

                ATURAN:
                - Setiap poin maksimal 2 kalimat
                - Fokus pada pola dan tren yang signifikan
                - Bahasa Indonesia yang jelas dan informatif
                - Hindari pengulangan informasi
                """
        }
    ]

    payload = {
        "messages": messages,
        "model": "llama3.1-8b",
        "temperature": 0.3,  # Lebih rendah untuk konsistensi format
        "max_tokens": 400,   # Lebih banyak untuk 5 poin lengkap
        "stream": False,
        "top_p": 0.9        # Tambahan untuk kontrol kualitas output
    }


    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Gagal ambil insight dari Cerebras AI. Status: {response.status_code}\nDetail: {response.text}"
    
    except requests.exceptions.RequestException as e:
        return f"Error koneksi ke Cerebras AI: {str(e)}"
    except KeyError as e:
        return f"Error parsing response dari Cerebras AI: {str(e)}"
    except Exception as e:
        return f"Error tidak terduga: {str(e)}"