import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
DB_PATH = "C:\Guvi\first project\uber_eats.db"

def run_query(query):
    # check_same_thread=False prevents threading errors in SQLite + Streamlit
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        return pd.read_sql(query, conn)

# -----------------------------
# PAGE CONFIGURATION & STYLING
# -----------------------------
st.set_page_config(
    page_title="Uber Eats Market Engine",
    page_icon="🍽️",
    layout="wide"
)

# Clean, brand-focused UI elements
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; }
    div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 800; color: #06C167; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR CONTROL PANEL
# -----------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/b3/Uber_Eats_2020_logo.svg", width=140)
st.sidebar.title("Navigation Hub")
page = st.sidebar.radio("Go to View:", ["📊 Executive Dashboard", "❓ Restaurant Q&A Insights", "📦 Order Analytics Studio"])

# =====================================================
# 1. EXECUTIVE DASHBOARD
# =====================================================
if page == "📊 Executive Dashboard":
    st.title("🍽️ Uber Eats Operations Dashboard")
    st.caption("Live exploration tracking performance baselines and restaurant partners.")
    st.write("---")
    
    # KPI Metrics Section
    try:
        total_restaurants = run_query("SELECT COUNT(*) FROM restaurants").iloc[0, 0]
        avg_rating = run_query("SELECT ROUND(AVG(rate), 2) FROM restaurants").iloc[0, 0]
        avg_cost = run_query("SELECT ROUND(AVG([approx_cost(for two people)]), 2) FROM restaurants").iloc[0, 0]
        total_locations = run_query("SELECT COUNT(DISTINCT location) FROM restaurants").iloc[0, 0]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Active Partners", f"{total_restaurants:,}")
        m2.metric("Market Benchmark Rating", f"⭐ {avg_rating}")
        m3.metric("Avg Cost (2 Pax)", f"₹{avg_cost}")
        m4.metric("Micro-Markets Covered", total_locations)
    except Exception as e:
        st.error(f"Error initializing summary metrics: {e}")
        
    st.write("---")
    
    # Interactive Advanced Search Filter Grid
    st.subheader("🔍 Intelligent Filter Engine")
    c1, c2 = st.columns(2)
    
    with c1:
        locations_df = run_query("SELECT DISTINCT location FROM restaurants ORDER BY location")
        selected_locations = st.multiselect("Select Target Regions", locations_df['location'].tolist())
        
    with c2:
        cuisine_data = run_query("SELECT cuisines FROM restaurants WHERE cuisines IS NOT NULL")
        all_cuisines = sorted(list(set([c.strip() for sublist in cuisine_data['cuisines'].str.split(',') for c in sublist if c])))
        selected_cuisines = st.multiselect("Select Cuisine Profiles", all_cuisines)
        
    c3, c4 = st.columns([3, 1])
    with c3:
        search_restaurant = st.text_input("Search Brand Name Directly")
    with c4:
        sort_option = st.selectbox("Optimize Sort Layout", ["Highest Rating", "Lowest Cost", "Most Customer Votes"])

    # Map filter selections to optimized database commands
    sort_dict = {
        "Highest Rating": "rate DESC",
        "Lowest Cost": "[approx_cost(for two people)] ASC",
        "Most Customer Votes": "votes DESC"
    }
    
    # Dynamic Query Constructor
    query = "SELECT name, location, cuisines, rate, [approx_cost(for two people)] AS cost, votes FROM restaurants WHERE 1=1"
    if selected_locations:
        query += f" AND location IN ({str(selected_locations)[1:-1]})"
    if selected_cuisines:
        cuisine_conditions = [f"cuisines LIKE '%{c}%'" for c in selected_cuisines]
        query += " AND (" + " OR ".join(cuisine_conditions) + ")"
    if search_restaurant:
        query += f" AND name LIKE '%{search_restaurant}%'"
        
    query += f" ORDER BY {sort_dict[sort_option]} LIMIT 50"
    
    # Results Processing Window
    filtered_df = run_query(query)
    st.subheader("📋 Discovery Feed Results")
    if filtered_df.empty:
        st.warning("No listings match your search setup rules.")
    else:
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Export Filtered Grid to CSV",
            data=csv_data,
            file_name="uber_eats_filtered.csv",
            mime="text/csv"
        )

# =====================================================
# 2. RESTAURANT Q&A INSIGHTS
# =====================================================
elif page == "❓ Restaurant Q&A Insights":
    st.title("❓ Strategic Market Q&A Analyzer")
    st.caption("Addressing core platform business hypotheses with dynamic chart elements.")
    st.write("---")
    
    hypothesis = st.selectbox(
        "Choose Business Evaluation Area:",
        [
            "Top Performing Locations by Benchmark Rating",
            "High Density Market Saturation Zones",
            "Reservation Ecosystem Impact (Table Booking vs Rating)",
            "Combined Operational Channel Spread (Online vs Booking)"
        ]
    )
    
    if hypothesis == "Top Performing Locations by Benchmark Rating":
        sql = "SELECT location, ROUND(AVG(rate),2) AS avg_rating, COUNT(*) AS total_units FROM restaurants GROUP BY location HAVING total_units > 20 ORDER BY avg_rating DESC LIMIT 10;"
        res = run_query(sql)
        
        st.subheader("📊 Premium Service Quality Micro-Markets")
        fig = px.bar(res, x='avg_rating', y='location', orientation='h', text='avg_rating',
                     color='avg_rating', color_continuous_scale='YlGnBu')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
    elif hypothesis == "High Density Market Saturation Zones":
        sql = "SELECT location, COUNT(*) AS restaurant_count FROM restaurants GROUP BY location ORDER BY restaurant_count DESC LIMIT 10;"
        res = run_query(sql)
        
        st.subheader("📊 Top 10 Saturated Regions by Volume")
        fig = px.pie(res, values='restaurant_count', names='location', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Plotly3)
        st.plotly_chart(fig, use_container_width=True)
        
    elif hypothesis == "Reservation Ecosystem Impact (Table Booking vs Rating)":
        sql = "SELECT CASE book_table WHEN 1 THEN 'Accepts Bookings' ELSE 'No Booking System' END AS booking_status, ROUND(AVG(rate),2) AS avg_rating FROM restaurants GROUP BY book_table;"
        res = run_query(sql)
        
        st.subheader("📊 Customer Quality Metrics Based on Table Bookings")
        fig = px.bar(res, x='booking_status', y='avg_rating', color='booking_status', 
                     text='avg_rating', color_discrete_sequence=['#06C167', '#FF3B30'])
        st.plotly_chart(fig, use_container_width=True)
        
    elif hypothesis == "Combined Operational Channel Spread (Online vs Booking)":
        sql = """
        SELECT 
            CASE online_order WHEN 1 THEN 'Online' ELSE 'Offline Only' END AS Order_Type,
            CASE book_table WHEN 1 THEN 'Reservations' ELSE 'Walk-in' END AS Booking_Type,
            ROUND(AVG(rate),2) AS avg_rating 
        FROM restaurants 
        GROUP BY online_order, book_table;
        """
        res = run_query(sql)
        
        st.subheader("📊 Strategic Multi-Channel Performance Matrix")
        fig = px.density_heatmap(res, x='Order_Type', y='Booking_Type', z='avg_rating', 
                                 text_auto=True, color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 3. ORDER ANALYTICS STUDIO
# =====================================================
elif page == "📦 Order Analytics Studio":
    st.title("📦 Transactional Customer Order Streams")
    st.caption("Deep-dive calculations checking high-volume items, revenue maps, and average values.")
    st.write("---")
    
    order_metric = st.selectbox(
        "Choose Transaction Performance Metric Group:",
        [
            "Top Volume Brands by Total Completed Orders",
            "Gross Market Revenue Drivers by Location",
            "Highest Average Order Value (AOV) Outlets"
        ]
    )
    
    # Safe structure checking for the presence of the transactions database table
    try:
        if order_metric == "Top Volume Brands by Total Completed Orders":
            sql = "SELECT restaurant_name, COUNT(*) AS total_orders FROM orders GROUP BY restaurant_name ORDER BY total_orders DESC LIMIT 10;"
            df = run_query(sql)
            st.subheader("🔥 Most Ordered Partner Chains")
            fig = px.bar(df, x='total_orders', y='restaurant_name', orientation='h', text='total_orders', color='total_orders', color_continuous_scale='Sunset')
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

        elif order_metric == "Gross Market Revenue Drivers by Location":
            sql = "SELECT location, ROUND(SUM(order_amount),2) AS total_revenue FROM orders GROUP BY location ORDER BY total_revenue DESC LIMIT 10;"
            df = run_query(sql)
            st.subheader("💰 Platform Economic Revenue Footprint")
            fig = px.bar(df, x='location', y='total_revenue', text='total_revenue', color='total_revenue', color_continuous_scale='Algae')
            st.plotly_chart(fig, use_container_width=True)

        elif order_metric == "Highest Average Order Value (AOV) Outlets":
            sql = "SELECT restaurant_name, ROUND(AVG(order_amount),2) AS avg_order_value FROM orders GROUP BY restaurant_name ORDER BY avg_order_value DESC LIMIT 10;"
            df = run_query(sql)
            st.subheader("💎 Premium Ticket Invoicing Standouts")
            fig = px.scatter(df, x='avg_order_value', y='restaurant_name', size='avg_order_value', color='avg_order_value', color_continuous_scale='Cividis')
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.info("💡 Transaction analysis features require an updated 'orders' dataset table inside your local SQLite archive file.")
        st.error(f"Database response tracking code: {e}")