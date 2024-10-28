import streamlit as st
from psycopg import Connection
import os
import re
import pandas as pd

CWD = "/".join(__file__.replace("\\", "/").split("/")[:-1])
DATA_DIR = os.path.join(CWD, "data")
df_knowledge = pd.read_excel(os.path.join(DATA_DIR, "TALENTDNA SECRET INGREDIENT.xls"))
talents = []
for _, row in df_knowledge.iterrows():
    talents.append(row["ASPECTS / THEMES / ATTRIBUTES"])
db_columns = ["definisi_singkat_indo",
              "definisi_singkat_paragraf_indo", "short_definition_eng",
              "short_definition_paragraph_eng", "deskripsi_panjang_indo",
              "long_description_eng", "behavior_when_strong_eng",
              "perilaku_ketika_kuat_indo", "behaviors_when_weak_eng",
              "perilaku_ketika_lemah_indo", "coaching_recommendations_eng",
              "rekomendasi_pengembangan_indo"]

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

#Function to fetch talents data
def fetching_talent_description(col:str, talent:str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {col} FROM data_talent WHERE talent_name = \'{talent}\'")
            talent_desc = cur.fetchone()
    
    sentence_list = str(talent_desc[0]).split(".\n")
    sentence_list[-1] = re.sub(r"\.", "",sentence_list[-1])
    return sentence_list


def input_data(col:str, talent:str, new_data:str):
    sentence_list = fetching_talent_description(col,talent)
    new_data = f"{new_data}."
    sentence_list.append(new_data)
    new_final_data = ".\n".join(sentence_list)
    update_data(talent, col, new_final_data)

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

# Function to delete data by ID
def delete_data(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM data WHERE id = %s", (id,))
            if cur.rowcount > 0:
                conn.commit()
                st.success(f"Data with ID {id} deleted.")
            else:
                st.warning(f"Data with ID {id} not found.")

# Function to check API key
def check_api_key(api_key):
    return api_key == st.secrets["VALID_API_KEY"]

# App logic
if 'api_key_validated' not in st.session_state:
    st.session_state.api_key_validated = False

# API Key input form
if not st.session_state.api_key_validated:
    st.title("🔐Enter API Key")
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
    st.sidebar.title("CRUD Operations")
    window_option = st.sidebar.selectbox("Choose an operation", ["📝CUD Operation", "🧰Advanced Mode"])
    
    if window_option == "🧰Advanced Mode":
        with st.form("advanced form"):
            st.title("🧰Advanced Operation")
            st.subheader("Stored Data")
            read_data()
            st.subheader("Update Data Form")
            talent_name = st.selectbox("Choose talent", talents, key="create_talent_name")
            column = st.selectbox("Choose column", db_columns, index=db_columns.index("perilaku_ketika_kuat_indo"))
            data_update = st.text_area("Enter new data", key="update_data")

            st.form_submit_button("Submit")
        
        if data_update:
            update_data(talent_name, column, data_update)
            st.rerun()
        else:
            st.warning("Please enter a new data.")
        
    elif window_option == "📝CUD Operation":
        st.title("📝Create, Update, and Delete Data")
        column = st.selectbox("Choose column", db_columns, index=db_columns.index("perilaku_ketika_kuat_indo"))
        selected_talent = st.selectbox("Choose talents", talents)
        
        st.subheader(selected_talent)

        tab1, tab2 = st.tabs(["✏️Create/Input", "🧹Delete"])

        with tab1:
            with st.form("create form"):
                new_desc = st.text_area("Create/input new data")
                submitted = st.form_submit_button("Submit")
            
            if submitted:
                input_data(column, selected_talent, new_desc)

        with tab2:
            desc_list = fetching_talent_description(column, selected_talent)
            selected_desc_list = st.multiselect(f"\"{column}\" data", desc_list, desc_list)
            st.write("Selected data:", selected_desc_list)

            if st.button("Submit"):
                if len(selected_desc_list) != 0:
                    new_final_data = ".\n".join(selected_desc_list)
                    new_final_data = f"{new_final_data}."
                    update_data(selected_talent, column, new_final_data)
                    st.rerun()
                else:
                    st.warning("Please select at least one data.")