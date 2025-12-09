import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Telecom Churn Portal", layout="wide")

# Demo users
USERS = {
    "admin@example.com": "1234",
    "manager@example.com": "manager",
}

TELECOM_COMPANIES = ["Airtel", "Jio", "VI", "BSNL"]


# ---------------- SESSION SETUP ----------------
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "page" not in st.session_state:
        # page can be: "login", "company_select", "current_month", "future_churn"
        st.session_state.page = "login"
    if "selected_company" not in st.session_state:
        st.session_state.selected_company = None


# ---------------- HELPER CHARTS ----------------
def reason_bar_chart(series: pd.Series, title: str):
    """Horizontal bar chart for reason distribution."""
    df = series.value_counts().reset_index()
    df.columns = ["Reason", "Count"]

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Count:Q", title="Number of Customers"),
            y=alt.Y("Reason:N", sort="-x", title="Churn Reason"),
            tooltip=["Reason", "Count"],
        )
        .properties(title=title, height=300)
    )
    st.altair_chart(chart, use_container_width=True)


def churn_bar_chart(churn_series: pd.Series, title: str):
    """Bar chart for churn vs not churn."""
    df = churn_series.value_counts().rename(index={0: "Not Churn", 1: "Churn"}).reset_index()
    df.columns = ["Status", "Count"]

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Status:N", title="Status"),
            y=alt.Y("Count:Q", title="Number of Customers"),
            tooltip=["Status", "Count"],
        )
        .properties(title=title, height=300)
    )
    st.altair_chart(chart, use_container_width=True)


def scatter_future_risk(df: pd.DataFrame, title: str):
    """Scatter plot: MonthlyCharges vs ChurnProbability for future risk."""
    chart = (
        alt.Chart(df)
        .mark_circle(size=80, opacity=0.8)
        .encode(
            x=alt.X("MonthlyCharges:Q", title="Monthly Charges"),
            y=alt.Y("ChurnProbability:Q", title="Churn Probability"),
            tooltip=["CustomerID", "MonthlyCharges", "ChurnProbability", "ContractType"],
        )
        .properties(title=title, height=350)
    )
    st.altair_chart(chart, use_container_width=True)


# ---------------- PAGES ----------------
def login_page():
    st.title("🔐 Telecom Churn Portal - Login")

    tab1, tab2 = st.tabs(["Login", "Sign Up (Demo Only)"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if email in USERS and USERS[email] == password:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.page = "company_select"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email or password")

    with tab2:
        st.info("Signup is only a demo. In a real system, we’d store users in a database.")


def company_select_page():
    st.sidebar.write(f"Logged in as: {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.page = "login"
        st.rerun()

    st.title("📡 Telecom Churn Portal")
    st.subheader("Step 1: Select Telecom Company")

    company = st.selectbox("Choose a telecom company", TELECOM_COMPANIES)

    st.write(
        "After selecting the company, click **Go to Current Month Dashboard** "
        "to see churn analytics for that company."
    )

    if st.button("Go to Current Month Dashboard ➜"):
        st.session_state.selected_company = company
        st.session_state.page = "current_month"
        st.rerun()


def current_month_page():
    # Guard
    if not st.session_state.selected_company:
        st.warning("Please select a telecom company first.")
        if st.button("Go to Company Selection"):
            st.session_state.page = "company_select"
            st.rerun()
        return

    company = st.session_state.selected_company

    st.sidebar.write(f"Logged in as: {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.page = "login"
        st.rerun()

    st.title(f"📅 Current Month Churn - {company}")
    st.caption("Step 2: Overview of current month customers and churn risk.")

    # ----- CURRENT MONTH DATA: mix of low & medium & high risk -----
    np.random.seed(42)
    size = 50

    data = pd.DataFrame({
        "CustomerID": [f"{company[:2].upper()}-C{i}" for i in range(1, size + 1)],
        # more spread out probabilities
        "ChurnProbability": np.round(np.random.beta(a=2, b=3, size=size), 2),
        "MonthlyCharges": np.random.randint(400, 1600, size),
        "Tenure": np.random.randint(1, 36, size),
        "ContractType": np.random.choice(
            ["Month-to-month", "One year", "Two year"],
            size=size
        )
    })

    data["WillChurn"] = (data["ChurnProbability"] > 0.5).astype(int)

    total_customers = len(data)
    churners = int(data["WillChurn"].sum())
    non_churners = total_customers - churners
    churn_rate = churners / total_customers * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active Customers (sample)", total_customers)
    col2.metric("Predicted to Churn (current month)", churners)
    col3.metric("Churn Rate (%)", f"{churn_rate:.1f}")

    # Churn vs not churn graph
    st.write("#### Churn vs Not Churn – Current Month")
    churn_bar_chart(data["WillChurn"], "Current Month – Churn vs Not Churn")

    # Generate churn reasons
    reasons = []
    for _, row in data.iterrows():
        r = []
        if row["MonthlyCharges"] > 1200:
            r.append("High monthly charges")
        if row["Tenure"] <= 6:
            r.append("Low tenure")
        if row["ContractType"] == "Month-to-month":
            r.append("No long-term contract")
        if not r:
            r.append("General usage pattern")
        reasons.append(", ".join(r))

    data["ChurnReason"] = reasons

    high_risk = data[data["WillChurn"] == 1]

    st.write("#### High-Risk Customers — Current Month")
    st.dataframe(high_risk, use_container_width=True)

    st.write("#### Reason Distribution (Only Churners)")
    if not high_risk.empty:
        high_risk["MainReason"] = high_risk["ChurnReason"].str.split(",").str[0]
        reason_bar_chart(
            high_risk["MainReason"],
            "Current Month – Main Reasons for Churn",
        )
    else:
        st.info("No churners in the current sample.")

    st.markdown("---")
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("⬅ Back to Company Selection"):
            st.session_state.page = "company_select"
            st.rerun()
    with col_next:
        if st.button("Go to Future Churn Dashboard ➜"):
            st.session_state.page = "future_churn"
            st.rerun()


def future_churn_page():
    # Guard
    if not st.session_state.selected_company:
        st.warning("Please select a telecom company first.")
        if st.button("Go to Company Selection"):
            st.session_state.page = "company_select"
            st.rerun()
        return

    company = st.session_state.selected_company

    st.sidebar.write(f"Logged in as: {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.page = "login"
        st.rerun()

    st.title(f"🔮 Future Churn Prediction - {company}")
    st.caption("Step 3: Focus on very high-risk customers for the upcoming period.")

    # ---- FUTURE DATA: mostly very high probability customers ----
    np.random.seed(99)
    size = 50

    future_data = pd.DataFrame({
        "CustomerID": [f"{company[:2].upper()}-F{i}" for i in range(1, size + 1)],
        # mostly high probabilities 0.7–0.99
        "ChurnProbability": np.round(np.random.uniform(0.7, 0.99, size), 2),
        "MonthlyCharges": np.random.randint(600, 2000, size),
        "Tenure": np.random.randint(1, 24, size),
        "ContractType": np.random.choice(
            ["Month-to-month", "One year", "Two year"],
            size=size
        )
    })

    # consider very high risk as >= 0.8
    very_high_risk = future_data[future_data["ChurnProbability"] >= 0.8].copy()

    total_future_customers = len(future_data)
    very_high_count = len(very_high_risk)
    avg_future_prob = future_data["ChurnProbability"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers Evaluated (future)", total_future_customers)
    col2.metric("Very High-Risk Customers (p ≥ 0.8)", very_high_count)
    col3.metric("Average Future Churn Probability", f"{avg_future_prob:.2f}")

    # Generate reasons for very high risk only
    reasons = []
    for _, row in very_high_risk.iterrows():
        r = []
        if row["MonthlyCharges"] > 1400:
            r.append("Very high monthly charges")
        elif row["MonthlyCharges"] > 1000:
            r.append("High monthly charges")
        if row["Tenure"] <= 6:
            r.append("Early-stage customer")
        if row["ContractType"] == "Month-to-month":
            r.append("No contract lock-in")
        if not r:
            r.append("Usage pattern risk")
        reasons.append(", ".join(r))

    very_high_risk["ChurnReason"] = reasons

    st.write("#### Very High-Risk Customers – Future Period")
    st.dataframe(very_high_risk, use_container_width=True)

    st.write("#### Reason Distribution – Future High-Risk")
    if not very_high_risk.empty:
        very_high_risk["MainReason"] = very_high_risk["ChurnReason"].str.split(",").str[0]
        reason_bar_chart(
            very_high_risk["MainReason"],
            "Future Period – Main Reasons for Very High Risk",
        )
    else:
        st.info("No very high-risk customers in this sample.")

    st.write("#### Risk Profile – Monthly Charges vs Churn Probability")
    scatter_future_risk(
        future_data,
        "Future Risk – Monthly Charges vs Churn Probability",
    )

    st.markdown("---")
    col_back, col_home = st.columns(2)
    with col_back:
        if st.button("⬅ Back to Current Month Dashboard"):
            st.session_state.page = "current_month"
            st.rerun()
    with col_home:
        if st.button("🏠 Back to Company Selection"):
            st.session_state.page = "company_select"
            st.rerun()


# ---------------- MAIN ----------------
def main():
    init_session_state()

    if not st.session_state.logged_in or st.session_state.page == "login":
        login_page()
    else:
        if st.session_state.page == "company_select":
            company_select_page()
        elif st.session_state.page == "current_month":
            current_month_page()
        elif st.session_state.page == "future_churn":
            future_churn_page()
        else:
            st.session_state.page = "company_select"
            company_select_page()


if __name__ == "__main__":
    main()
