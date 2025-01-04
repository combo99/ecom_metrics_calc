import streamlit as st
import plotly.express as px

def calculate_shopify_fees(product_price: float) -> float:
    """Returns Shopify fees for a single transaction."""
    return 0.029 * product_price + 0.30

def calculate_breakeven_metrics(p: float, c: float, fees: float):
    """
    Given product price p, COGS c, and Shopify fees,
    returns a dict with breakeven ad spend, breakeven CPA, and breakeven ROAS.
    """
    ad_spend_breakeven = p - c - fees
    # If ad_spend_breakeven <= 0, we technically can't break even,
    # but we'll just display whatever it is (can be negative).
    breakeven_cpa = ad_spend_breakeven
    if ad_spend_breakeven != 0:
        breakeven_roas = p / ad_spend_breakeven
    else:
        breakeven_roas = 0  # or float('inf') if you prefer
    return {
        "breakeven_cpa": breakeven_cpa,
        "breakeven_roas": breakeven_roas
    }

st.title("E-Commerce Single-Unit Profit Calculator")

# --- 1. Basic Inputs ---
product_price = st.number_input("Product Price ($)", min_value=0.0, value=82.99, step=1.0)
cogs = st.number_input("COGS ($)", min_value=0.0, value=10.0, step=1.0)

# Calculate Shopify Fees
shopify_fees = calculate_shopify_fees(product_price)

# Breakeven metrics
breakeven_data = calculate_breakeven_metrics(product_price, cogs, shopify_fees)
breakeven_cpa = breakeven_data["breakeven_cpa"]
breakeven_roas = breakeven_data["breakeven_roas"]

# --- 2. Choose Calculation Mode (CPA or ROAS) ---
calculation_mode = st.radio("Calculation Mode", ("CPA", "ROAS"), index=0)

# We'll define variables to store Ad Spend, CPA, ROAS
ad_spend = 0.0
final_cpa = 0.0
final_roas = 0.0

# --- 3. Mode-Specific Logic ---
if calculation_mode == "CPA":
    # User inputs desired CPA
    desired_cpa = st.number_input("Desired CPA ($)", min_value=0.0, value=20.0, step=0.5)
    ad_spend = desired_cpa  # Single unit => Ad Spend = CPA
    # Derived ROAS (avoid division by zero)
    final_roas = product_price / ad_spend if ad_spend > 0 else 0.0
    final_cpa = desired_cpa
else:
    # User inputs desired ROAS
    desired_roas = st.number_input("Desired ROAS", min_value=0.0, value=2.0, step=0.1)
    if desired_roas > 0:
        ad_spend = product_price / desired_roas
        final_cpa = ad_spend  # Single unit => CPA = Ad Spend
        final_roas = desired_roas
    else:
        ad_spend = 0.0
        final_cpa = 0.0
        final_roas = 0.0

# --- 4. Profit Calculation ---
profit = product_price - cogs - shopify_fees - ad_spend

# --- 5. Display Results ---
st.subheader("Results")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Ad Spend", f"${ad_spend:,.2f}")
with col2:
    st.metric("ROAS", f"{final_roas:,.2f}")
with col3:
    st.metric("CPA", f"${final_cpa:,.2f}")

st.metric("Profit (Single Unit)", f"${profit:,.2f}")

# --- 6. Breakeven Stats ---
st.subheader("Breakeven Metrics (Single Unit)")
st.write(f"**Breakeven CPA:** ${breakeven_cpa:,.2f}")
st.write(f"**Breakeven ROAS:** {breakeven_roas:,.2f}")

# --- 7. Chart Type Selection ---
chart_type = st.selectbox("Select Chart Type", ["Pie Chart", "Bar Chart"])

# Prepare data for the chart
labels = ["COGS", "Shopify Fees", "Ad Spend", "Profit"]
values = [cogs, shopify_fees, ad_spend, profit]

# Define a fixed color map for Plotly
color_map = {
    "COGS": "blue",
    "Shopify Fees": "orange",
    "Ad Spend": "red",
    "Profit": "green",
}

# --- 8. Create Chart ---
if chart_type == "Pie Chart":
    fig = px.pie(
        names=labels,
        values=values,
        color=labels,
        color_discrete_map=color_map,
        title="Cost Distribution (Single Unit)"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

else:  # Bar Chart
    # For a bar chart, we set color=labels to preserve color mapping
    fig = px.bar(
        x=labels,
        y=values,
        color=labels,
        color_discrete_map=color_map,
        title="Cost Distribution (Single Unit)",
        labels={"x": "Segments", "y": "Amount ($)"}
    )
    st.plotly_chart(fig, use_container_width=True)
