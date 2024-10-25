import streamlit as st
from psycopg import Connection
import os
import pandas as pd

CWD = "/".join(__file__.replace("\\", "/").split("/")[:-1])
DATA_DIR = os.path.join(CWD, "data")
df_knowledge = pd.read_excel(os.path.join(DATA_DIR, "TALENTDNA SECRET INGREDIENT.xls"))
talents = []
for _, row in df_knowledge.iterrows():
    talents.append(row["ASPECTS / THEMES / ATTRIBUTES"])

# Function to create a connection to PostgreSQL
def get_connection():
    return Connection.connect(conninfo=st.secrets["POSTGRES_CONNINFO_VALIDATOR"])

# Function to read all data
def read_data():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM data_talent")
            rows = cur.fetchall()
            if rows:
                # Convert the fetched data to a Pandas DataFrame for better display
                df = pd.DataFrame(rows, columns=["ID", "Talent No", "Talent Name", 
                                                 "Short (IND)", "Short Paragraph (IND)", 
                                                 "Short (ENG)", "Short Paragraph (ENG)",
                                                 "Long (IND)", "Long (ENG)",
                                                 "When Strong (ENG)", "When Strong (IND)",
                                                 "When Weak (ENG)", "Whean Weak (IND)",
                                                 "Coaching Recommendation (ENG)",
                                                 "Coaching Recommendation (IND)"])
                st.dataframe(df)  # Displays the data as a table
            else:
                st.write("No data available.")

# Function to update data by ID
def update_data(talent, col, new_data):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE data_talent SET {col} = \'{new_data}\' WHERE talent_name = \'{talent}\'")
            if cur.rowcount > 0:
                conn.commit()
                st.success(f"Data with Talent {talent} updated.")
            else:
                st.warning(f"Data with Talent {talent} not found.")

# Function to check API key
def check_api_key(api_key):
    return api_key == st.secrets["VALID_API_KEY"]

# App logic
if 'api_key_validated' not in st.session_state:
    st.session_state.api_key_validated = False

# API Key input form
if not st.session_state.api_key_validated:
    st.title("Enter API Key")
    api_key = st.text_input("API Key", type="password")
    
    if st.button("Submit"):
        if check_api_key(api_key):
            st.session_state.api_key_validated = True
            st.success("API Key validated successfully!")

            # Force a rerun to reflect the updated session state
            st.rerun()
        else:
            st.error("Invalid API Key. Please try again.")

else:
    st.title("Update Data")
    st.subheader("Stored Data")
    read_data()
    st.subheader("Update Data Form")
    talent_name = st.selectbox("Choose talent", talents, key="create_talent_name")
    column = st.selectbox("Choose column", ["definisi_singkat_indo",
                                            "definisi_singkat_paragraf_indo", "short_definition_eng",
                                            "short_definition_paragraph_eng", "deskripsi_panjang_indo",
                                            "long_description_eng", "behavior_when_strong_eng",
                                            "perilaku_ketika_kuat_indo", "behaviors_when_weak_eng",
                                            "perilaku_ketika_lemah_indo", "coaching_recommendations_eng",
                                            "rekomendasi_pengembangan_indo"])
    data_update = st.text_area("Enter new data", key="update_data")
    if st.button("Update"):
        if data_update:
            update_data(talent_name, column, data_update)
            st.rerun()
        else:
            st.warning("Please enter a new data.")