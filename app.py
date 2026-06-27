import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Online Retail Dashboard",
    page_icon="📊",
    layout="wide"
)


# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    #df = pd.read_excel("dataset/cleaned_online_retail.csv"
    #".xlsx")
     file_id = "1RCw3tG7ARpY6GyaVvtq8CnzfyEXYTu36"
     url = f"file_id = "https://docs.google.com/spreadsheets/d/1RCw3tG7ARpY6GyaVvtq8CnzfyEXYTu36/edit?usp=drive_link&ouid=107011005573167658543&rtpof=true&sd=true"
    

      df = pd.read_excel(url, engine="openpyxl")

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Month"] = df["InvoiceDate"].dt.strftime("%b %Y")

    return df

df = load_data()

def format_currency(value):
    if value >= 1_000_000:
        return f"£{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"£{value/1_000:.1f}K"
    else:
        return f"£{value:.0f}"

# ============================
# SIDEBAR FILTERS
# ============================

st.sidebar.title("📊 Dashboard Filters")
st.sidebar.markdown("---")

selected_country = st.sidebar.multiselect(
    "Country",
    sorted(df["Country"].dropna().unique())
)

if not selected_country:
    selected_country = sorted(df["Country"].dropna().unique())

selected_month = st.sidebar.multiselect(
    "Month",
    sorted(df["Month"].dropna().unique())
)

if not selected_month:
    selected_month = sorted(df["Month"].dropna().unique())

filtered_df = df[
    (df["Country"].isin(selected_country)) &
    (df["Month"].isin(selected_month))
]

# ============================
# KPI CARDS
# ============================

total_revenue = filtered_df["Revenue"].sum()
total_orders = filtered_df["InvoiceNo"].nunique()
total_customers = filtered_df["CustomerID"].nunique()
total_products = filtered_df["Description"].nunique()
countries = filtered_df["Country"].nunique()
avg_order = total_revenue / total_orders if total_orders else 0

st.title("📊 Online Retail Sales Dashboard")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("💰 Revenue", format_currency(total_revenue))
col2.metric("🧾 Orders", total_orders)
col3.metric("👥 Customers", total_customers)
col4.metric("📦 Products", total_products)
col5.metric("🌍 Countries", countries)
col6.metric("🛒 Avg Order", f"£{avg_order:,.2f}")

st.markdown("---")


# ============================
# CHARTS
# ============================

left, right = st.columns(2)

# Monthly Revenue Trend
with left:
    monthly_sales = (
        filtered_df.groupby("Month", sort=False)["Revenue"]
        .sum()
        .reset_index()
    )

    fig = px.line(
    monthly_sales,
    x="Month",
    y="Revenue",
    markers=True,
    title="📈 Monthly Revenue Trend"
)

    fig.update_traces(line=dict(width=3))

    fig.update_layout(
        height=420,
        xaxis_title="",
        yaxis_title="Revenue (£)"
    )

    st.plotly_chart(fig, use_container_width=True)

# Revenue by Country
with right:
    country_sales = (
        filtered_df.groupby("Country")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        country_sales,
        x="Revenue",
        y="Country",
        orientation="h",
        title="🌍 Top 10 Countries by Revenue",
        text_auto=".2s"
    )

    fig.update_layout(
    height=420,
    yaxis={'categoryorder': 'total ascending'}
)

    st.plotly_chart(fig, use_container_width=True)

   

# ============================
# Top Products
# ============================

# ==========================
# Top Products
# ==========================

# Remove postage/service records
exclude_items = [
    "DOTCOM POSTAGE",
    "POSTAGE",
    "Manual",
    "BANK CHARGES",
    "CARRIAGE"
]

products_df = filtered_df[
    ~filtered_df["Description"].isin(exclude_items)
]

top_products = (
    products_df.groupby("Description", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
    .head(10)
)

fig_products = px.bar(
    top_products,
    x="Revenue",
    y="Description",
    orientation="h",
    title="📦 Top 10 Products by Revenue",
    text="Revenue"
)

fig_products.update_traces(
    texttemplate="£%{text:,.0f}",
    textposition="outside"
)

fig_products.update_layout(
    height=450,
    yaxis=dict(categoryorder="total ascending"),
    margin=dict(l=180, r=30, t=60, b=20)
)

st.plotly_chart(fig_products, use_container_width=True)

# ============================
# Monthly Orders
# ============================

monthly_orders = (
    filtered_df.groupby("Month", sort=False)["InvoiceNo"]
    .nunique()
    .reset_index(name="Orders")
)

fig_orders = px.bar(
    monthly_orders,
    x="Month",
    y="Orders",
    title="🛒 Monthly Orders",
    text_auto=True
)

fig_orders.update_layout(
    height=500
)

st.plotly_chart(fig_orders, use_container_width=True)

st.markdown("---")

# ============================
# Top Customers
# ============================

top_customers = (
    filtered_df.dropna(subset=["CustomerID"])
    .groupby("CustomerID", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
    .head(10)
)

# Convert CustomerID to string so Plotly treats it as text
top_customers["CustomerID"] = (
    "Customer " + top_customers["CustomerID"].astype(int).astype(str)
)

fig_customers = px.bar(
    top_customers,
    x="Revenue",
    y="CustomerID",
    orientation="h",
    title="👤 Top 10 Customers by Revenue",
    text="Revenue"
)

fig_customers.update_traces(
    texttemplate="£%{text:,.0f}",
    textposition="outside"
)

fig_customers.update_layout(
    height=450,
    yaxis=dict(categoryorder="total ascending"),
    margin=dict(l=100, r=20, t=60, b=20)
)

st.plotly_chart(fig_customers, use_container_width=True)

st.markdown("---")


st.header("💡 Business Insights & Recommendations")

# ==============================
# BUSINESS INSIGHTS
# ==============================

with st.expander("🌍 Insight 1: UK Market Dominance"):
    st.markdown("""
**Observation**
- The United Kingdom accounts for **91.45% of all transactions** and **84.59% of total revenue**.
- This shows a strong domestic market but also creates dependency on a single region.

**Recommendations**
- Expand marketing efforts in **Germany, France, and the Netherlands**.
- Launch localized campaigns to grow international sales.
""")

with st.expander("📈 Insight 2: Strong Q4 Seasonality"):
    st.markdown("""
**Observation**
- Revenue peaks between **September and November**.
- **November** recorded the highest revenue of **£1,503,866.78**.

**Recommendations**
- Increase inventory before Q4.
- Launch promotional campaigns in October to capture holiday demand.
""")

with st.expander("👑 Insight 3: High-Value Customers"):
    st.markdown("""
**Observation**
- **274 customers generate 61.5% of total revenue**, making them the most valuable customer segment.

**Recommendations**
- Launch a VIP loyalty program.
- Provide exclusive discounts and priority customer support.
""")

with st.expander("📦 Insight 4: Product Portfolio"):
    st.markdown("""
**Observation**
- A small number of products contribute most of the revenue, while many products have very low sales.

**Recommendations**
- Apply the 80/20 rule to focus on top-performing products.
- Bundle or discontinue low-selling products.
""")

with st.expander("💰 Insight 5: Medium Value Customers"):
    st.markdown("""
**Observation**
- **1,390 medium-value customers contribute 28.11% of total revenue**.

**Recommendations**
- Use personalized email campaigns.
- Offer bundle discounts and upsell opportunities.
""")

with st.expander("🔄 Insight 6: One-Time Buyers"):
    st.markdown("""
**Observation**
- **34.4% of customers purchased only once**.

**Recommendations**
- Send personalized recommendations.
- Offer discount coupons or free shipping to encourage repeat purchases.
""")

st.markdown("---")

# ==============================
# BUSINESS RECOMMENDATIONS
# ==============================

st.subheader("🎯 Key Business Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.success("🇬🇧 Focus marketing investment on the UK while gradually expanding into international markets.")
    st.success("👑 Retain high-value customers through VIP loyalty programs and personalized offers.")
    st.success("📈 Convert medium-value customers using targeted upselling and bundle discounts.")

with col2:
    st.success("📦 Optimize the product portfolio by promoting top sellers and reviewing low-performing products.")
    st.success("🛒 Prepare inventory and staffing before the Q4 seasonal demand peak.")
    st.success("🔄 Re-engage one-time buyers with personalized email campaigns and return incentives.")

st.markdown("---")

