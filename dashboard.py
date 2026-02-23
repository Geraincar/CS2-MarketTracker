import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import config

st.set_page_config(page_title="CS2 Market Tracker", layout="wide")
st.title("🔫 CS2 Market Real-Time Dashboard")

count = st_autorefresh(interval=15000, key="refresh")

DB_NAME = "market_data.db"

@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

tab1, tab2 = st.tabs(["🇺🇸 Steam Market", "🇨🇳 Buff Market"])

# --- STEAM TAB ---
with tab1:
    st.header("Steam Market")
    try:
        df = pd.read_sql("SELECT * FROM steam_prices ORDER BY timestamp DESC", get_conn())
        if df.empty:
            st.info("Waiting for Steam data...")
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            items = df['item_name'].unique()
            item = st.selectbox("Select Item", items, key="s_item")

            data = df[df['item_name']==item].sort_values('timestamp')
            c1, c2 = st.columns(2)
            c1.metric("Current Price (USD)", f"${data.iloc[0]['price']:.2f}")
            c2.metric("Volume", data.iloc[0]['volume'])

            fig = px.line(data, x='timestamp', y='price', title='Price History')
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error("Run parser_steam.py first")

# --- BUFF TAB ---
with tab2:
    st.header("Buff163 Market")
    try:
        df = pd.read_sql("SELECT * FROM buff_prices ORDER BY timestamp DESC", get_conn())
        if df.empty:
            st.info("Waiting for Buff data...")
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Группируем по ID для выбора
            unique_items = df[['goods_id', 'item_name']].drop_duplicates()

            selection = st.selectbox(
                "Select Item",
                unique_items['goods_id'],
                format_func=lambda x: unique_items[unique_items['goods_id']==x]['item_name'].values[0],
                key="b_item"
            )

            data = df[df['goods_id']==selection].sort_values('timestamp')

            c1, c2 = st.columns(2)
            price_cny = data.iloc[0]['price_cny']
            c1.metric("Current Price (CNY)", f"¥{price_cny:.2f}")
            c2.metric("Approx Price (USD)", f"${price_cny / config.CURRENCY_RATE:.2f}")

            fig = px.line(data, x='timestamp', y='price_cny', title='Price History (CNY)')
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error("Run parser_buff.py first")
