import streamlit as st
import pandas as pd

# --------------- CONFIG ---------------
st.set_page_config(page_title="Telecom Churn Dashboard", layout="wide")

# Fake user database (for demo)
USERS = {
    "admin@example.com": "1234",
    "manager@example.com": "manager",
}

TELECOM_COMPANIES = ["Airtel", "Jio", "VI", "BSNL"]

# --------------- HELPER FUNCTIONS ---------------

def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None

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
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

    with tab2:
        st.info("For project demo, signup will just show a message.")

def telecom_home():
    st.sidebar.write(f"Logged in as: {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.experimental_rerun()

    st.title("📡 Telecom Churn Dashboard")

    company = st.selectbox("Select Telecom Company", TELECOM_COMPANIES)

    st.write(f"### Company: {company}")

    page = st.radio(
        "Select Analysis Type",
        ["Current Month Churn", "Future Churn Prediction"],
        horizontal=True,
    )

    if page == "Current Month Churn":
        show_current_month_churn(company)
    else:
        show_future_churn(company)

def show_current_month_churn(company: str):
    st.subheader(f"📅 Current Month Churn - {company}")

    data = pd.DataFrame({
        "CustomerID": [f"{company[:2].upper()}-{i}" for i in range(1, 21)],
        "ChurnProbability": [0.1, 0.8, 0.3, 0.9, 0.6,
                             0.2, 0.7, 0.4, 0.55, 0.95,
                             0.12, 0.33, 0.76, 0.88, 0.5,
                             0.67, 0.44, 0.29, 0.99, 0.18],
    })
    data["WillChurn"] = (data["ChurnProbability"] > 0.5).astype(int)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers (sample)", len(data))
    col2.metric("Predicted to Churn", data["WillChurn"].sum())
    col3.metric(
        "Churn Rate (%)",
        f"{(data['WillChurn'].sum() / len(data)) * 100:.1f}"
    )

    st.write("#### Churn Distribution")
    churn_counts = data["WillChurn"].value_counts().rename({0: "Not Churn", 1: "Churn"})
    st.bar_chart(churn_counts)

    st.write("#### Customer Predictions")
    st.dataframe(data)

def show_future_churn(company: str):
    st.subheader(f"🔮 Future Churn Prediction - {company}")

    future_data = pd.DataFrame({
        "CustomerID": [f"{company[:2].upper()}-F{i}" for i in range(1, 16)],
        "ChurnProbability": [0.85, 0.92, 0.78, 0.81, 0.95,
                             0.72, 0.88, 0.9, 0.83, 0.8,
                             0.69, 0.77, 0.91, 0.89, 0.93],
        "MonthlyCharges": [900, 1200, 750, 1100, 1300,
                           800, 1250, 1400, 950, 1000,
                           700, 720, 1500, 1350, 1180],
        "Tenure": [2, 5, 3, 1, 4, 6, 2, 3, 2, 1, 5, 7, 1, 2, 3],
        "ContractType": [
            "Month-to-month", "Month-to-month", "One year", "Month-to-month",
            "Month-to-month", "One year", "Month-to-month", "Two year",
            "Month-to-month", "Month-to-month", "One year", "Two year",
            "Month-to-month", "Month-to-month", "One year"
        ],
    })

    # Generate churn reason
    reasons = []
    for _, row in future_data.iterrows():
        r = []
        if row["MonthlyCharges"] > 1000:
            r.append("High monthly charges")
        if row["Tenure"] <= 3:
            r.append("Low tenure")
        if row["ContractType"] == "Month-to-month":
            r.append("No long-term contract")
        if not r:
            r.append("General usage pattern")
        reasons.append(", ".join(r))

    future_data["ChurnReason"] = reasons

    st.write("#### High Risk Customers")
    st.dataframe(future_data)

    st.write("#### Reason Distribution")
    future_data["MainReason"] = future_data["ChurnReason"].str.split(",").str[0]
    st.bar_chart(future_data["MainReason"].value_counts())

# --------------- MAIN ---------------

def main():
    init_session_state()
    if not st.session_state.logged_in:
        login_page()
    else:
        telecom_home()

if __name__ == "__main__":
    main()
