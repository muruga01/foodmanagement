import streamlit as st
import pandas as pd
import MySQLdb

# Page config
st.set_page_config(page_title="Food Wastage Management", layout="wide")

st.title("🍱 Local Food Wastage Management System")

# Connect to MySQL
try:
    conn = MySQLdb.connect(
        host="127.0.0.1",
        user="root",
        passwd="",  # use your actual MySQL password
        database="food_data"
    )
    cursor = conn.cursor()
    st.success("✅ Connected to MySQL database")
except Exception as e:
    st.error(f"❌ Could not connect: {e}")

# View Providers Table
if st.sidebar.button("Show Providers"):
    df = pd.read_sql("SELECT * FROM providers", conn)
    st.subheader("📋 Provider Details")
    st.dataframe(df)

# View Receivers Table
if st.sidebar.button("Show Receivers"):
    df = pd.read_sql("SELECT * FROM receivers", conn)
    st.subheader("🙋‍♀️ Receiver Details")
    st.dataframe(df)

# View Food Listings with Filters
if st.sidebar.button("Show Food Listings"):
    df = pd.read_sql("SELECT * FROM food_listings", conn)
    st.subheader("🍛 Available Food Listings")

    city_filter = st.selectbox("Filter by City", ["All"] + sorted(df["Location"].unique()))
    food_type_filter = st.selectbox("Filter by Food Type", ["All"] + sorted(df["Food_Type"].unique()))

    if city_filter != "All":
        df = df[df["Location"] == city_filter]
    if food_type_filter != "All":
        df = df[df["Food_Type"] == food_type_filter]

    st.dataframe(df)

# View Claims
if st.sidebar.button("Show Claims"):
    df = pd.read_sql("SELECT * FROM claims", conn)
    st.subheader("📦 Food Claims Status")
    st.dataframe(df)

# Close MySQL connection on exit
def close_connection():
    if conn:
        cursor.close()
        conn.close()
        st.success("✅ MySQL connection closed.")

# Add New Provider
# if st.sidebar.button("Add New Provider"):
#     st.subheader("➕ Add New Provider")
#     name = st.text_input("Provider Name")
#     type=st.selectbox("Provider Type", ["Supermarket", "Grocery Store", "Restaurant", "Catering Service"])
#     address= st.text_input("Address")
#     city= st.text_input("City")
#     contact = st.text_input("Contact Info")
    
#     if st.button("Submit Provider"):
#         if name and contact:
#             cursor.execute("INSERT INTO providers (Name, Contact_Info) VALUES (%s, %s)", (name,type,address,city,contact))
#             conn.commit()
#             st.success("✅ Provider added successfully!")
#         else:
#             st.error("❌ Please fill in all fields.")

    