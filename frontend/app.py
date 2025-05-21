import streamlit as st
import requests
from top_100_us_stocks import top_100_stocks  # 👈 Import list

st.set_page_config(page_title="Agentic AI Stock Tool", layout="wide")
st.title("📈 Agentic AI-Driven Stock Market Analysis")

# --- Option Selector ---
option = st.radio("Choose a feature:", ["Chat with Agent", "Market Sentiment", "Prediction"], horizontal=True)

# --- Input Box ---
if option == "Market Sentiment":
    user_input = st.selectbox("Select a stock to analyze:", top_100_stocks)
else:
    user_input = st.text_input(f"Enter input for {option}:")

# --- Submit Button ---
if st.button("Submit"):
    st.info(f"You selected: {option}")
    st.write(f"📨 Input: {user_input}")

    # Example API request (adjust endpoint as needed)
    try:
        if option == "Chat with Agent":
            response = requests.post("http://127.0.0.1:8000/chat", json={"message": user_input})
        elif option == "Market Sentiment":
            response = requests.post("http://127.0.0.1:8000/sentiment", json={"query": user_input})
        elif option == "Prediction":
            response = requests.post("http://127.0.0.1:8000/predict", json={"ticker": user_input})
        
        if response.status_code == 200:
            result = response.json()
            st.success("✅ Success!")
            st.json(result)
        else:
            st.error(f"❌ Error: {response.status_code} - {response.text}")

    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to backend. Is it running?")
