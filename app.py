import streamlit as st
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Telecom Churn Portal", layout="wide")

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
        st.info("Signup is only conceptual. In viva, explain DB storage etc.")


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
    # Safety: if user landed here without selecting company
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
    st.caption("Step 2: View current month churn risk for the selected company.")

    # ----- dummy data (we will replace with real model later) -----
    data = pd.DataFrame({
        "CustomerID": [f"{company[:2].upper()}-{i}" for i in range(1, 21)],
        "ChurnProbability": [
            0.1, 0.8, 0.3, 0.9, 0.6,
            0.2, 0.7, 0.4, 0.55, 0.95,
            0.12, 0.33, 0.76, 0.88, 0.5,
            0.67, 0.44, 0.29, 0.99, 0.18,
        ],
    })
    data["WillChurn"] = (data["ChurnProbability"] > 0.5).astype(int)

    total_customers = len(data)
    churners = data["WillChurn"].sum()
    churn_rate = churners / total_customers * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers (sample)", total_customers)
    col2.metric("Predicted to Churn", churners)
    col3.metric("Churn Rate (%)", f"{churn_rate:.1f}")

    st.write("#### Churn vs Not Churn Count")
    churn_counts = data["WillChurn"].value_counts().rename(
        index={0: "Not Churn", 1: "Churn"}
    )
    st.bar_chart(churn_counts)

    st.write("#### Customer Level Predictions (Sample)")
    st.dataframe(data)

    st.info("Later this will be replaced with predictions from your ML model.")

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
    st.caption("Step 3: View high-risk customers and churn reasons.")

    # ----- dummy data (to be replaced with real predictions) -----
    future_data = pd.DataFrame({
        "CustomerID": [f"{company[:2].upper()}-F{i}" for i in range(1, 16)],
        "ChurnProbability": [
            0.85, 0.92, 0.78, 0.81, 0.95,
            0.72, 0.88, 0.90, 0.83, 0.80,
            0.69, 0.77, 0.91, 0.89, 0.93,
        ],
        "MonthlyCharges": [
            900, 1200, 750, 1100, 1300,
            800, 1250, 1400, 950, 1000,
            700, 720, 1500, 1350, 1180,
        ],
        "Tenure": [2, 5, 3, 1, 4, 6, 2, 3, 2, 1, 5, 7, 1, 2, 3],
        "ContractType": [
            "Month-to-month", "Month-to-month", "One year", "Month-to-month",
            "Month-to-month", "One year", "Month-to-month", "Two year",
            "Month-to-month", "Month-to-month", "One year", "Two year",
            "Month-to-month", "Month-to-month", "One year",
        ],
    })

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

    st.write("#### High-Risk Customers (Sample)")
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
            # fallback
            st.session_state.page = "company_select"
            company_select_page()


if __name__ == "__main__":
    main()
