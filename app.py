import streamlit as st
import pandas as pd
import MySQLdb

# Page config
st.set_page_config(page_title="Local Food Wastage Management", layout="wide")

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

choice = st.sidebar.radio("Choose an option:", ["Project Introduction", "View Tables", "CRUD Operations","SQL Queries & Visualizations","Learner SQL Queries","User Introduction"])

# Project Introduction
if choice == "Project Introduction":
    st.subheader("📖 Project Introduction")
    st.write("""
    This project aims to address the issue of food wastage in local communities by connecting food providers with receivers in need. 
    The system allows food providers to list available food items, which can then be claimed by registered receivers.
    
    Key Features:
    - Food Providers can register and list available food items.
    - Receivers can claim food items based on their needs.
    - The system tracks claims and provides insights into food distribution.
    
    Technologies Used:
    - MySQL for database management
    - Streamlit for web interface
    """)

#View Tables
if choice == "View Tables":
    st.subheader("📊 View Database Tables")
    
    # Show Providers Table
    if st.button("Show Providers"):
        df = pd.read_sql("SELECT * FROM providers", conn)
        st.dataframe(df)

    # Show Receivers Table
    if st.button("Show Receivers"):
        df = pd.read_sql("SELECT * FROM receivers", conn)
        st.dataframe(df)

    # Show Food Listings
    if st.button("Show Food Listings"):
        df = pd.read_sql("SELECT * FROM food_listings", conn)
        st.dataframe(df)

    # Show Claims
    if st.button("Show Claims"):
        df = pd.read_sql("SELECT * FROM claims", conn)
        st.dataframe(df)

#CRUD Operations
if choice == "CRUD Operations":
    st.subheader("🛠️ CRUD Operations")
    
    # Add New Provider
    with st.form("Add New Provider"):
        st.subheader("➕ Add New Provider")
        provider_id = st.number_input("Provider ID", min_value=1002, step=1)
        name = st.text_input("Provider Name")
        provider_type = st.selectbox("Provider Type", ["Supermarket", "Grocery Store", "Restaurant", "Catering Service"])
        address = st.text_input("Address")
        city = st.text_input("City")
        contact = st.text_input("Contact Info")
        submit=st.form_submit_button("Submit Provider")
    if submit:
        if name and provider_type and address and city and contact:
            cursor.execute(
                    "INSERT INTO providers (Provider_ID, Name, Type, Address, City, Contact) VALUES (%s, %s, %s, %s, %s, %s)",
                    (provider_id, name, provider_type, address, city, contact)
                )
            conn.commit()
            st.success("✅ Provider added successfully!")
        else:
            st.error("❌ Please fill in all the fields.")

    
    # Add New Receiver
    if st.button("Add New Receiver"):
        st.subheader("➕ Add New Receiver")
        receiver_id = st.number_input("Receiver ID", min_value=1001, step=1)
        name = st.text_input("Receiver Name")
        city = st.text_input("City")
        contact = st.text_input("Contact Info")
        
        if st.button("Submit Receiver"):
            if name and city and contact:
                cursor.execute(
                    "INSERT INTO receivers (Receiver_ID, Name, City, Contact) VALUES (%s, %s, %s, %s)",
                    (receiver_id, name, city, contact)
                )
                conn.commit()
                st.success("✅ Receiver added successfully!")
            else:
                st.error("❌ Please fill in all fields.")

    # Add New Food Listing
    if st.button("Add New Food Listing"):
        st.subheader("➕ Add New Food Listing")
        food_name = st.text_input("Food Name")
        food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan", "Gluten-Free"])
        quantity = st.number_input("Quantity (in kg)", min_value=1)
        location = st.text_input("Location")
        provider_id = st.number_input("Provider ID", min_value=1)
        
        if st.button("Submit Food Listing"):
            if food_name and food_type and quantity and location and provider_id:
                cursor.execute(
                    "INSERT INTO food_listings (Food_Name, Food_Type, Quantity, Location, Provider_ID) VALUES (%s, %s, %s, %s, %s)",
                    (food_name, food_type, quantity, location, provider_id)
                )
                conn.commit()
                st.success("✅ Food listing added successfully!")
            else:
                st.error("❌ Please fill in all fields.")

    # Add New Claim
    if st.button("Add New Claim"):
        st.subheader("➕ Add New Claim")
        food_id = st.number_input("Food ID", min_value=1)
        receiver_id = st.number_input("Receiver ID", min_value=1)
        status = st.selectbox("Claim Status", ["Pending", "Completed", "Cancelled"])
        
        if st.button("Submit Claim"):
            if food_id and receiver_id and status:
                cursor.execute(
                    "INSERT INTO claims (Food_ID, Receiver_ID, Status) VALUES (%s, %s, %s)",
                    (food_id, receiver_id, status)
                )
                conn.commit()
                st.success("✅ Claim added successfully!")
            else:
                st.error("❌ Please fill in all fields.")

#SQL Queries & Visualizations
if choice == "SQL Queries & Visualizations":
    st.subheader("📊 SQL Queries & Visualizations")

    # Food Providers and Receivers City Wise
    if st.button("City Wise Providers and Receivers"):
        df_providers = pd.read_sql("SELECT * FROM providers", conn)
        df_receivers = pd.read_sql("SELECT * FROM receivers", conn)

        st.subheader("🌆 City Wise Providers and Receivers")
        
        city = st.selectbox("Select City", ["All"] + sorted(df_providers["City"].unique()))

        if city != "All":
            df_providers = df_providers[df_providers["City"] == city]
            df_receivers = df_receivers[df_receivers["City"] == city]

        st.write("### Providers")
        st.dataframe(df_providers)

        st.write("### Receivers")
        st.dataframe(df_receivers)
    
    #Food Provider Contributing the most food
    if st.button("Top Food Provider"):
        df = pd.read_sql("SELECT Provider_Type, SUM(Quantity) AS Total_Quantity FROM food_listings GROUP BY Provider_Type ORDER BY Total_Quantity DESC LIMIT 1", conn)
        st.subheader("🥇 Top Food Provider")
        if not df.empty:
            st.dataframe(df)
            # Plotting the top provider with other providers
            st.bar_chart(df.set_index('Provider_Type'))
        else:
            st.write("No data available.")

    #Contact Info of Food Providers in a Specific City
    if st.button("Contact Info of Providers in City"):
        city = st.selectbox("Select City", ["All"] + sorted(pd.read_sql("SELECT DISTINCT City FROM providers", conn)["City"].tolist()))
        
        if city != "All":
            query = "SELECT Name, Address, Contact FROM providers WHERE City = %s"
            df = pd.read_sql(query, conn, params=(city,))
        else:
            df = pd.read_sql("SELECT Name, Address, Contact FROM providers", conn)

        st.subheader(f"📞 Contact Info of Providers in {city if city != 'All' else 'All Cities'}")
        st.dataframe(df)
    
    #Receiver with the Most Claims
    if st.button("Receiver with Most Claims"):
        df = pd.read_sql("SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims FROM claims c JOIN receivers r ON c.Receiver_ID = r.Receiver_ID GROUP BY r.Name ORDER BY Total_Claims DESC LIMIT 5", conn)
        st.subheader("🏆 Receiver with Most Claims")
        if not df.empty:
            st.dataframe(df)
        else:
            st.write("No claims data available.")
        
    #Total Quantity of Food available from each Provider
    if st.button("Total Quantity of Food from Each Provider"):
        df = pd.read_sql("SELECT Provider_Type, SUM(Quantity) AS Total_Quantity FROM food_listings GROUP BY Provider_Type", conn)
        st.subheader("📊 Total Quantity of Food from Each Provider")
        if not df.empty:
            st.dataframe(df)
            st.bar_chart(df.set_index('Provider_Type'))
        else:
            st.write("No food listings available.")
    
    #City with the Most Food Listings
    if st.button("City with Most Food Listings"):
        df = pd.read_sql("SELECT Location, COUNT(*) AS Total_Listings FROM food_listings GROUP BY Location ORDER BY Total_Listings DESC LIMIT 1", conn)
        st.subheader("🌍 City with Most Food Listings")
        if not df.empty:
            st.dataframe(df)
        else:
            st.write("No food listings available.")

    #Common Available Food Types
    if st.button("Commonly Available Food Types"):
        df = pd.read_sql("SELECT Food_Type, COUNT(*) AS Total FROM food_listings GROUP BY Food_Type ORDER BY Total DESC", conn)
        st.subheader("🍽️ Commonly Available Food Types")
        if not df.empty:
            st.dataframe(df)
            st.bar_chart(df.set_index('Food_Type')['Total'])
        else:
            st.write("No food listings available.")

    #Food Claims by Item Type
    if st.button("Food Claims by Item Type"):
        df = pd.read_sql("SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claim_Count FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID GROUP BY f.Food_Name ORDER BY Claim_Count DESC;", conn)
        st.subheader("📋 Food Claims by Item Type")
        if not df.empty:
            st.dataframe(df)
        else:
            st.write("No claims data available.")
    
    #Provider with highest number of claims
    if st.button("Provider with Highest Number of Claims"):
        df = pd.read_sql("SELECT p.Name, COUNT(c.Claim_ID) AS Total_Claims FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID JOIN providers p ON f.Provider_ID = p.Provider_ID GROUP BY p.Name ORDER BY Total_Claims DESC LIMIT 1", conn)
        st.subheader("🏅 Provider with Highest Number of Claims")
        if not df.empty:
            st.dataframe(df)
        else:
            st.write("No claims data available.")
    
    #Ratio of Completed Claims to Pending Claims to Cancelled Claims
    if st.button("Claims Status Ratio"):
        df = pd.read_sql("SELECT Status, COUNT(*) AS Count FROM claims GROUP BY Status", conn)
        st.subheader("📊 Claims Status Ratio")
        
        if not df.empty:
            total_claims = df['Count'].sum()
            df['Ratio'] = df['Count'] / total_claims
            st.dataframe(df)
            
            # Plotting the ratio
            st.bar_chart(df.set_index('Status')['Ratio'])
        else:
            st.write("No claims data available.")
    
    #Average Quantity of Food Claimed per Receiver
    if st.button("Average Quantity Claimed per Receiver"):
        df = pd.read_sql("SELECT r.Name, AVG(f.Quantity) AS Average_Quantity FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID JOIN receivers r ON c.Receiver_ID = r.Receiver_ID GROUP BY r.Name", conn)
        st.subheader("📈 Average Quantity of Food Claimed per Receiver")
        if not df.empty:
            st.dataframe(df)
        else:
            st.write("No claims data available.")
    
    #Most Claimed Meal Type
    if st.button("Most Claimed Meal Type"):
        df = pd.read_sql("SELECT Meal_Type, COUNT(c.Claim_ID) AS Claim_Count FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID GROUP BY Meal_Type ORDER BY Claim_Count DESC LIMIT 1", conn)
        st.subheader("🍽️ Most Claimed Meal Type")
        if not df.empty:
            st.dataframe(df)
        else:
            st.write("No claims data available.")
    
    #Total Quantity of Food donated by each Provider
    if st.button("Total Quantity Donated by Each Provider"):
        df = pd.read_sql("SELECT p.Name, SUM(f.Quantity) AS Total_Quantity FROM food_listings f JOIN providers p ON f.Provider_ID = p.Provider_ID GROUP BY p.Name", conn)
        st.subheader("📊 Total Quantity of Food Donated by Each Provider")
        if not df.empty:
            st.dataframe(df)
            st.bar_chart(df.set_index('Name')['Total_Quantity'])
        else:
            st.write("No food listings available.")
    
#Learner SQL Queries
if choice == "Learner SQL Queries":
    st.subheader("📝 Learner SQL Queries")
    
    # Example Query: Total Food Listings by Provider Type
    if st.button("Total Food Listings by Provider Type"):
        df = pd.read_sql("SELECT Provider_Type, COUNT(*) AS Total_Listings FROM food_listings GROUP BY Provider_Type", conn)
        st.dataframe(df)
        st.bar_chart(df.set_index('Provider_Type'))

    # Example Query: Total Claims by Status
    if st.button("Total Claims by Status"):
        df = pd.read_sql("SELECT Status, COUNT(*) AS Total_Claims FROM claims GROUP BY Status", conn)
        st.dataframe(df)
        st.bar_chart(df.set_index('Status'))

# User Introduction
if choice == "User Introduction":
    st.subheader("👤 User Introduction")
    st.write("""
    This project is developed by Muruga Prasaad MD as part of a local initiative to reduce food wastage and support community needs.
    """)