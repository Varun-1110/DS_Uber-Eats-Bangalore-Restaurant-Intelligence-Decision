import streamlit as st
import pandas as pd
import sqlite3
import json

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Uber Eats SQL Analytics",
    layout="wide"
)

st.title("🍔 Uber Eats Bangalore Analytics")

# ======================================================
# LOAD RESTAURANT DATA
# ======================================================

df = pd.read_csv(r"C:\Guvi\first project\Uber_Eats_data.csv")

# ======================================================
# CLEAN DATA
# ======================================================

df.drop_duplicates(inplace=True)

# CLEAN RATING

df['rate'] = (
    df['rate']
    .astype(str)
    .str.replace('/5', '', regex=False)
)

df['rate'] = pd.to_numeric(
    df['rate'],
    errors='coerce'
)

# CLEAN COST

df['approx_cost(for two people)'] = (
    df['approx_cost(for two people)']
    .astype(str)
    .str.replace(',', '', regex=False)
)

df['approx_cost(for two people)'] = pd.to_numeric(
    df['approx_cost(for two people)'],
    errors='coerce'
)

# FILL NULL VALUES

df.fillna(0, inplace=True)

# ======================================================
# SQLITE CONNECTION
# ======================================================

conn = sqlite3.connect(
    r"C:\Guvi\first project\uber_eats.db",
    check_same_thread=False
)

# STORE RESTAURANT TABLE

df.to_sql(
    "restaurants",
    conn,
    if_exists="replace",
    index=False
)

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go To",
    [
        "Dashboard",
        "Business Q&A",
        "Advanced Analysis",
        "Order SQL Q&A"
    ]
)

# ======================================================
# PAGE 1 — DASHBOARD
# ======================================================

if page == "Dashboard":

    st.header("📊 Restaurant Dashboard")

    # FILTERS

    locations = st.multiselect(
        "Select Location",
        sorted(df['location'].unique())
    )

    online = st.selectbox(
        "Online Order",
        ["All", "Yes", "No"]
    )

    rating = st.slider(
        "Minimum Rating",
        0.0,
        5.0,
        3.0
    )

    # SQL QUERY

    query = f"""
    SELECT
        name,
        location,
        cuisines,
        rate,
        votes,
        online_order,
        book_table,
        [approx_cost(for two people)]
    FROM restaurants
    WHERE rate >= {rating}
    """

    if locations:

        location_str = ",".join(
            [f"'{loc}'" for loc in locations]
        )

        query += f" AND location IN ({location_str})"

    if online != "All":

        query += f" AND online_order = '{online}'"

    result = pd.read_sql_query(query, conn)

    st.dataframe(
        result,
        use_container_width=True
    )

# ===================================================
# PAGE 2 — BUSINESS QUESTIONS
# ===================================================

elif page == "Business Q&A":

    st.header("10 Business Questions")

    question = st.selectbox(
        "Select Question",
        [

            "1. Highest Rated Locations",

            "2. Over Saturated Locations",

            "3. Online Ordering Impact",

            "4. Table Booking Impact",

            "5. Best Price Segment",

            "6. Price Segment Performance",

            "7. Most Common Cuisines",

            "8. Highest Rated Cuisines",

            "9. Niche Cuisine Opportunities",

            "10. Premium Restaurant Locations"
        ]
    )

    # ------------------------------------------------

    if question == "1. Highest Rated Locations":

        q = """
        SELECT
            location,
            ROUND(AVG(rate),2) AS avg_rating
        FROM restaurants
        GROUP BY location
        ORDER BY avg_rating DESC
        LIMIT 10
        """

    # ------------------------------------------------

    elif question == "2. Over Saturated Locations":

        q = """
        SELECT
            location,
            COUNT(*) AS total_restaurants
        FROM restaurants
        GROUP BY location
        ORDER BY total_restaurants DESC
        LIMIT 10
        """

    # ------------------------------------------------

    elif question == "3. Online Ordering Impact":

        q = """
        SELECT
            online_order,
            ROUND(AVG(rate),2) AS avg_rating,
            COUNT(*) AS total
        FROM restaurants
        GROUP BY online_order
        """

    # ------------------------------------------------

    elif question == "4. Table Booking Impact":

        q = """
        SELECT
            book_table,
            ROUND(AVG(rate),2) AS avg_rating
        FROM restaurants
        GROUP BY book_table
        """

    # ------------------------------------------------

    elif question == "5. Best Price Segment":

        q = """
        SELECT

            CASE

                WHEN [approx_cost(for two people)] < 500
                    THEN 'Low Cost'

                WHEN [approx_cost(for two people)] BETWEEN 500 AND 1000
                    THEN 'Mid Range'

                ELSE 'Premium'

            END AS price_segment,

            ROUND(AVG(rate),2) AS avg_rating

        FROM restaurants

        GROUP BY price_segment

        ORDER BY avg_rating DESC
        """

    # ------------------------------------------------

    elif question == "6. Price Segment Performance":

        q = """
        SELECT

            CASE

                WHEN [approx_cost(for two people)] < 500
                    THEN 'Low Cost'

                WHEN [approx_cost(for two people)] BETWEEN 500 AND 1000
                    THEN 'Mid Range'

                ELSE 'Premium'

            END AS price_segment,

            COUNT(*) AS total_restaurants,
            ROUND(AVG(rate),2) AS avg_rating

        FROM restaurants

        GROUP BY price_segment
        """

    # ------------------------------------------------

    elif question == "7. Most Common Cuisines":

        q = """
        SELECT
            cuisines,
            COUNT(*) AS total
        FROM restaurants
        GROUP BY cuisines
        ORDER BY total DESC
        LIMIT 10
        """

    # ------------------------------------------------

    elif question == "8. Highest Rated Cuisines":

        q = """
        SELECT
            cuisines,
            ROUND(AVG(rate),2) AS avg_rating
        FROM restaurants
        GROUP BY cuisines
        ORDER BY avg_rating DESC
        LIMIT 10
        """

    # ------------------------------------------------

    elif question == "9. Niche Cuisine Opportunities":

        q = """
        SELECT
            cuisines,
            COUNT(*) AS total_restaurants,
            ROUND(AVG(rate),2) AS avg_rating
        FROM restaurants
        GROUP BY cuisines
        HAVING total_restaurants < 20
        ORDER BY avg_rating DESC
        LIMIT 10
        """

    # ------------------------------------------------

    elif question == "10. Premium Restaurant Locations":

        q = """
        SELECT
            location,
            ROUND(AVG(rate),2) AS avg_rating,
            ROUND(AVG([approx_cost(for two people)]),2) AS avg_cost
        FROM restaurants
        GROUP BY location
        HAVING avg_cost > 1000
        ORDER BY avg_rating DESC
        """

    # ------------------------------------------------

    result = pd.read_sql_query(q, conn)

    st.dataframe(
        result,
        use_container_width=True
    )


# ===================================================
# PAGE 3 — ADVANCED ANALYSIS
# ===================================================

# =====================================================
# ADVANCED ANALYSIS USING UBER EATS DATASET
# =====================================================

elif page == "Advanced Analysis":

    st.header("🚀 Advanced Business Analysis")

    analysis = st.selectbox(
        "Choose Analysis",
        [

            "Top Revenue Locations",

            "Best Online Order Locations",

            "Most Expensive Restaurant Areas",

            "Cuisine Performance Analysis",

            "High Votes But Low Ratings"
        ]
    )

# =====================================================
# 1. TOP REVENUE LOCATIONS
# =====================================================

    if analysis == "Top Revenue Locations":

        q = """
        SELECT

            location,

            COUNT(*) AS total_restaurants,

            ROUND(
                AVG([approx_cost(for two people)]),2
            ) AS avg_cost,

            ROUND(
                AVG(rate),2
            ) AS avg_rating

        FROM restaurants

        GROUP BY location

        ORDER BY avg_cost DESC

        LIMIT 10
        """

# =====================================================
# 2. BEST ONLINE ORDER LOCATIONS
# =====================================================

    elif analysis == "Best Online Order Locations":

        q = """
        SELECT

            location,

            COUNT(*) AS total_restaurants,

            ROUND(AVG(rate),2) AS avg_rating

        FROM restaurants

        WHERE online_order='Yes'

        GROUP BY location

        HAVING total_restaurants > 10

        ORDER BY avg_rating DESC

        LIMIT 10
        """

# =====================================================
# 3. MOST EXPENSIVE RESTAURANT AREAS
# =====================================================

    elif analysis == "Most Expensive Restaurant Areas":

        q = """
        SELECT

            location,

            ROUND(
                AVG([approx_cost(for two people)]),2
            ) AS avg_cost,

            ROUND(
                MAX([approx_cost(for two people)]),2
            ) AS highest_cost

        FROM restaurants

        GROUP BY location

        ORDER BY avg_cost DESC

        LIMIT 10
        """

# =====================================================
# 4. CUISINE PERFORMANCE ANALYSIS
# =====================================================

    elif analysis == "Cuisine Performance Analysis":

        q = """
        SELECT

            cuisines,

            COUNT(*) AS total_restaurants,

            ROUND(AVG(rate),2) AS avg_rating,

            ROUND(
                AVG([approx_cost(for two people)]),2
            ) AS avg_cost

        FROM restaurants

        GROUP BY cuisines

        HAVING total_restaurants >= 5

        ORDER BY avg_rating DESC

        LIMIT 15
        """

# =====================================================
# 5. HIGH VOTES BUT LOW RATINGS
# =====================================================

    elif analysis == "High Votes But Low Ratings":

        q = """
        SELECT

            name,

            location,

            votes,

            rate,

            cuisines

        FROM restaurants

        WHERE votes > 500
        AND rate < 3.5

        ORDER BY votes DESC

        LIMIT 15
        """

# =====================================================
# EXECUTE QUERY
# =====================================================

    result = pd.read_sql_query(q, conn)

# =====================================================
# SHOW DATA
# =====================================================

    st.dataframe(
        result,
        use_container_width=True
    )


# ======================================================
# PAGE 4 — ORDER SQL Q&A
# ======================================================

elif page == "Order SQL Q&A":

    st.header("🛒 Order Data Integration & SQL Q&A")

    # --------------------------------------------------
    # UPLOAD JSON
    # --------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload Order JSON File",
        type=["json"]
    )

    if uploaded_file is not None:

        # --------------------------------------------------
        # LOAD JSON
        # --------------------------------------------------

        data = json.load(uploaded_file)

        orders_df = pd.DataFrame(data)

        # --------------------------------------------------
        # CLEAN COLUMN NAMES
        # --------------------------------------------------

        orders_df.columns = (
            orders_df.columns
            .str.strip()
        )

        # --------------------------------------------------
        # CLEAN ORDER VALUE
        # --------------------------------------------------

        orders_df['order_value'] = pd.to_numeric(
            orders_df['order_value'],
            errors='coerce'
        )

        # --------------------------------------------------
        # STORE INTO SQL
        # --------------------------------------------------

        orders_df.to_sql(
            "orders",
            conn,
            if_exists="replace",
            index=False
        )

        st.success("Orders Stored In SQL Database ✅")

        # --------------------------------------------------
        # SHOW DATA
        # --------------------------------------------------

        st.subheader("📄 Orders Preview")

        st.dataframe(
            orders_df.head(),
            use_container_width=True
        )

        # ==================================================
        # ORDER ANALYTICS
        # ==================================================

        st.subheader("📊 Order Analytics")

        # TOTAL ORDERS

        total_orders = pd.read_sql_query(
            """
            SELECT COUNT(*) AS total_orders
            FROM orders
            """,
            conn
        )

        st.metric(
            "Total Orders",
            int(total_orders.iloc[0,0])
        )

        # TOTAL REVENUE

        revenue = pd.read_sql_query(
            """
            SELECT
                ROUND(SUM(order_value),2)
                AS total_revenue
            FROM orders
            """,
            conn
        )

        st.metric(
            "Total Revenue",
            revenue.iloc[0,0]
        )

        # ==================================================
        # TOP RESTAURANTS
        # ==================================================

        st.subheader("🏆 Top Restaurants")

        top_restaurants = pd.read_sql_query(
            """
            SELECT
                restaurant_name,
                COUNT(*) AS total_orders,
                ROUND(SUM(order_value),2)
                AS revenue
            FROM orders
            GROUP BY restaurant_name
            ORDER BY revenue DESC
            LIMIT 10
            """,
            conn
        )

        st.dataframe(
            top_restaurants,
            use_container_width=True
        )

        # ==================================================
        # PAYMENT METHOD ANALYSIS
        # ==================================================

        st.subheader("💳 Payment Method Analysis")

        payment_df = pd.read_sql_query(
            """
            SELECT
                payment_method,
                COUNT(*) AS total_orders
            FROM orders
            GROUP BY payment_method
            ORDER BY total_orders DESC
            """,
            conn
        )

        st.dataframe(
            payment_df,
            use_container_width=True
        )

        st.bar_chart(
            payment_df.set_index(
                "payment_method"
            )
        )

        # ==================================================
        # DISCOUNT ANALYSIS
        # ==================================================

        st.subheader("🎯 Discount Usage Analysis")

        discount_df = pd.read_sql_query(
            """
            SELECT
                discount_used,
                COUNT(*) AS total_orders,
                ROUND(AVG(order_value),2)
                AS avg_order_value
            FROM orders
            GROUP BY discount_used
            """,
            conn
        )

        st.dataframe(
            discount_df,
            use_container_width=True
        )

        # ==================================================
        # MONTHLY SALES
        # ==================================================

        st.subheader("📅 Monthly Revenue")

        monthly_df = pd.read_sql_query(
            """
            SELECT
                SUBSTR(order_date,1,7)
                AS month,

                ROUND(SUM(order_value),2)
                AS revenue

            FROM orders

            GROUP BY month

            ORDER BY month
            """,
            conn
        )

        st.dataframe(
            monthly_df,
            use_container_width=True
        )

        st.line_chart(
            monthly_df.set_index("month")
        )

        # ==================================================
        # HIGHEST VALUE ORDERS
        # ==================================================

        st.subheader("🔥 Highest Value Orders")

        high_orders = pd.read_sql_query(
            """
            SELECT
                restaurant_name,
                order_date,
                order_value,
                payment_method
            FROM orders
            ORDER BY order_value DESC
            LIMIT 10
            """,
            conn
        )

        st.dataframe(
            high_orders,
            use_container_width=True
        )

        # ==================================================
        # CUSTOM SQL BUSINESS Q&A
        # ==================================================

        st.divider()

        st.subheader("🤖 Custom SQL Business Q&A")

        st.markdown("""

        Example Questions:

        - total revenue
        - total orders
        - top restaurants
        - payment methods
        - discount analysis
        - highest orders
        - monthly revenue

        """)

        user_question = st.text_input(
            "Ask Business Question"
        )

        # --------------------------------------------------

        if st.button("Run Query"):

            q = user_question.lower()

            query = ""

            # TOTAL REVENUE

            if "total revenue" in q:

                query = """
                SELECT
                    ROUND(SUM(order_value),2)
                    AS total_revenue
                FROM orders
                """

            # TOTAL ORDERS

            elif "total orders" in q:

                query = """
                SELECT
                    COUNT(*) AS total_orders
                FROM orders
                """

            # TOP RESTAURANTS

            elif "top restaurants" in q:

                query = """
                SELECT
                    restaurant_name,
                    ROUND(SUM(order_value),2)
                    AS revenue
                FROM orders
                GROUP BY restaurant_name
                ORDER BY revenue DESC
                LIMIT 10
                """

            # PAYMENT METHODS

            elif "payment" in q:

                query = """
                SELECT
                    payment_method,
                    COUNT(*) AS total_orders
                FROM orders
                GROUP BY payment_method
                """

            # DISCOUNT ANALYSIS

            elif "discount" in q:

                query = """
                SELECT
                    discount_used,
                    COUNT(*) AS total_orders,
                    ROUND(AVG(order_value),2)
                    AS avg_order_value
                FROM orders
                GROUP BY discount_used
                """

            # HIGHEST ORDERS

            elif "highest" in q:

                query = """
                SELECT
                    restaurant_name,
                    order_value
                FROM orders
                ORDER BY order_value DESC
                LIMIT 10
                """

            # MONTHLY REVENUE

            elif "monthly" in q:

                query = """
                SELECT
                    SUBSTR(order_date,1,7)
                    AS month,

                    ROUND(SUM(order_value),2)
                    AS revenue

                FROM orders

                GROUP BY month

                ORDER BY month
                """

            else:

                st.error("Question Not Supported")

            # --------------------------------------------------

            if query != "":

                result = pd.read_sql_query(
                    query,
                    conn
                )

                st.success("Analysis Completed ✅")

                st.dataframe(
                    result,
                    use_container_width=True
                )

    else:

        st.info("Upload Order JSON File")
# ======================================================
# CLOSE CONNECTION
# ======================================================

conn.close()