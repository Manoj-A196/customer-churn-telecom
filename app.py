import streamlit as st
import pandas as pd
import numpy as np

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
    st.caption("Step 2: View current month high-risk customers and churn reasons.")

    # ----- 50 SAMPLE CUSTOMERS -----
    np.random.seed(42)
    size = 50

    data = pd.DataFrame({
        "CustomerID": [f"{company[:2].upper()}-C{i}" for i in range(1, size + 1)],
        "ChurnProbability": np.round(np.random.uniform(0.1, 0.99, size), 2),
        "MonthlyCharges": np.random.randint(500, 1600, size),
        "Tenure": np.random.randint(1, 25, size),
        "ContractType": np.random.choice(
            ["Month-to-month", "One year", "Two year"],
            size=size
        )
    })

    data["WillChurn"] = (data["ChurnProbability"] > 0.5).astype(int)

    total_customers = len(data)
    churners = data["WillChurn"].sum()
    churn_rate = churners / total_customers * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers (sample)", total_customers)
    col2.metric("Predicted to Churn (current month)", churners)
    col3.metric("Churn Rate (%)", f"{churn_rate:.1f}")

    # Generate churn reasons
    reasons = []
    for _, row in data.iterrows():
        r = []
        if row["MonthlyCharges"] > 1200:
            r.append("High monthly charges")
        if row["Tenure"] <= 3:
            r.append("Low tenure")
        if row["ContractType"] == "Month-to-month":
            r.append("No long-term contract")
        if not r:
            r.append("General usage pattern")
        reasons.append(", ".join(r))

    data["ChurnReason"] = reasons

    high_risk = data[data["WillChurn"] == 1]

    st.write("#### High-Risk Customers — Current Month (50 sample)")
    st.dataframe(high_risk)

    st.write("#### Reason Distribution (Main Reason)")
    data["MainReason"] = data["ChurnReason"].str.split(",").str[0]
    st.bar_chart(data["MainReason"].value_counts())

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
    st.caption("Step 3: View high-risk customers and churn reasons for upcoming period.")

    # ---- 50 SAMPLE FUTURE CUSTOMERS ----
    np.random.seed(99)
    size = 50

    future_data = pd.DataFrame({
        "CustomerID": [f"{company[:2].upper()}-F{i}" for i in range(1, size + 1)],
        "ChurnProbability": np.round(np.random.uniform(0.5, 0.99, size), 2),
        "MonthlyCharges": np.random.randint(600, 1800, size),
        "Tenure": np.random.randint(1, 20, size),
        "ContractType": np.random.choice(
            ["Month-to-month", "One year", "Two year"],
            size=size
        )
    })

    reasons = []
    for _, row in future_data.iterrows():
        r = []
        if row["MonthlyCharges"] > 1200:
            r.append("High monthly charges")
        if row["Tenure"] <= 3:
            r.append("Low tenure")
        if row["ContractType"] == "Month-to-month":
            r.append("No long-term contract")
        if not r:
            r.append("General usage pattern")
        reasons.append(", ".join(r))

    future_data["ChurnReason"] = reasons

    st.write("#### High-Risk Customers — Future (50 sample)")
    st.dataframe(future_data)

    st.write("#### Reason Distribution (Main Reason)")
    future_data["MainReason"] = future_data["ChurnReason"].str.split(",").str[0]
    st.bar_chart(future_data["MainReason"].value_counts())

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
