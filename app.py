import streamlit as st
import pandas as pd
import MySQLdb
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="Local Food Wastage Management", layout="wide")

st.title("🍱 Local Food Wastage Management System")

if "crud_form_view" not in st.session_state:
    st.session_state.crud_form_view = "default_value"

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

# --- Initialize session state for current table view ---
if 'current_table_view' not in st.session_state:
    st.session_state.current_table_view = None # No table selected initially

# --- Main App Structure (assuming 'choice' comes from a sidebar or similar) ---
# For demonstration, let's simulate 'choice'
# In your actual app, 'choice' would be set by a navigation element (e.g., st.sidebar.radio)
choice = st.sidebar.radio("Navigation", ["Home", "View Tables", "CRUD Operations", "SQL Queries & Visualizations", "Learner SQL Queries", "User Introduction"])

if choice == "Home":
    st.subheader("🏠 Home")
    st.write("Welcome to the Local Food Wastage Management System!")
    st.write("This app helps manage food donations, claims, and reduce wastage in local communities.")
    st.markdown("---")

if choice == "View Tables":
    st.subheader("📊 View Database Tables")

    col1, col2, col3, col4 = st.columns(4) # Use columns for better button layout

    with col1:
        if st.button("Show Providers"):
            st.session_state.current_table_view = "providers"
    with col2:
        if st.button("Show Receivers"):
            st.session_state.current_table_view = "receivers"
    with col3:
        if st.button("Show Food Listings"):
            st.session_state.current_table_view = "food_listings"
    with col4:
        if st.button("Show Claims"):
            st.session_state.current_table_view = "claims"

    st.markdown("---") # Separator

    # --- Conditional Display of Tables based on session state ---
    if st.session_state.current_table_view == "providers":
        st.subheader("Providers Table")
        # Filter by Provider Type - this selectbox is always visible when 'providers' table is chosen
        # Fetch distinct types from DB for selectbox options
        try:
            provider_types_query = "SELECT DISTINCT Type FROM providers"
            available_provider_types_df = pd.read_sql(provider_types_query, conn)
            available_provider_types = ["All"] + sorted(available_provider_types_df["Type"].tolist())
        except Exception as e:
            st.error(f"Could not fetch provider types. Error: {e}")
            available_provider_types = ["All"] # Fallback

        provider_type_selected = st.selectbox("Filter by Provider Type", available_provider_types)

        if provider_type_selected != "All":
            query = "SELECT * FROM providers WHERE Type = %s"
            df_display = pd.read_sql(query, conn, params=(provider_type_selected,))
        else:
            df_display = pd.read_sql("SELECT * FROM providers", conn)
        st.dataframe(df_display)

    # --- Receivers Table ---
    elif st.session_state.current_table_view == "receivers":
        st.subheader("Receivers Table")

        # Fetch distinct types and cities for selectbox options
        try:
            receiver_types_query = "SELECT DISTINCT type FROM receivers"
            available_receiver_types_df = pd.read_sql(receiver_types_query, conn)
            available_receiver_types = ["All"] + sorted(available_receiver_types_df["type"].tolist())

            receiver_cities_query = "SELECT DISTINCT city FROM receivers"
            available_receiver_cities_df = pd.read_sql(receiver_cities_query, conn)
            available_receiver_cities = ["All"] + sorted(available_receiver_cities_df["city"].tolist())

        except Exception as e:
            st.error(f"Could not fetch filter options for Receivers. Error: {e}")
            available_receiver_types = ["All"]
            available_receiver_cities = ["All"]

        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            receiver_type_selected = st.selectbox("Filter by Receiver Type", available_receiver_types, key="rec_type_filter")
        with col_filter2:
            receiver_city_selected = st.selectbox("Filter by City", available_receiver_cities, key="rec_city_filter")

        query = "SELECT * FROM receivers WHERE 1=1"
        params = []

        if receiver_type_selected != "All":
            query += " AND type = %s"
            params.append(receiver_type_selected)
        if receiver_city_selected != "All":
            query += " AND city = %s"
            params.append(receiver_city_selected)
        
        df_display = pd.read_sql(query, conn, params=tuple(params))
        st.dataframe(df_display)
        if df_display.empty:
            st.info("No receivers found matching the selected filters.")

    # --- Food Listings Table ---
    elif st.session_state.current_table_view == "food_listings":
        st.subheader("Food Listings Table")

        # Fetch distinct food types, meal types, and statuses
        try:
            food_types_query = "SELECT DISTINCT food_type FROM food_listings"
            available_food_types_df = pd.read_sql(food_types_query, conn)
            available_food_types = ["All"] + sorted(available_food_types_df["food_type"].tolist())

            meal_types_query = "SELECT DISTINCT meal_type FROM food_listings"
            available_meal_types_df = pd.read_sql(meal_types_query, conn)
            available_meal_types = ["All"] + sorted(available_meal_types_df["meal_type"].tolist())

            listing_cities_query = "SELECT DISTINCT Location FROM food_listings"
            available_listing_cities_df = pd.read_sql(listing_cities_query, conn)
            available_listing_cities = ["All"] + sorted(available_listing_cities_df["Location"].tolist())

        except Exception as e:
            st.error(f"Could not fetch filter options for Food Listings. Error: {e}")
            available_food_types = ["All"]
            available_meal_types = ["All"]
            available_statuses = ["All"]
            available_listing_cities = ["All"]

        col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
        with col_filter1:
            food_type_selected = st.selectbox("Filter by Food Type", available_food_types, key="food_type_filter")
        with col_filter2:
            meal_type_selected = st.selectbox("Filter by Meal Type", available_meal_types, key="meal_type_filter")
        with col_filter3:
            listing_city_selected = st.selectbox("Filter by City", available_listing_cities, key="listing_city_filter")

        query = "SELECT * FROM food_listings WHERE 1=1"
        params = []

        if food_type_selected != "All":
            query += " AND food_type = %s"
            params.append(food_type_selected)
        if meal_type_selected != "All":
            query += " AND meal_type = %s"
            params.append(meal_type_selected)
        if listing_city_selected != "All":
            query += " AND Location = %s"
            params.append(listing_city_selected)
        
        df_display = pd.read_sql(query, conn, params=tuple(params))
        st.dataframe(df_display)
        if df_display.empty:
            st.info("No food listings found matching the selected filters.")

    # --- Claims Table ---
    elif st.session_state.current_table_view == "claims":
        st.subheader("Claims Table")

        # Fetch distinct statuses and get min/max dates for date range
        try:
            claim_statuses_query = "SELECT DISTINCT status FROM claims"
            available_claim_statuses_df = pd.read_sql(claim_statuses_query, conn)
            available_claim_statuses = ["All"] + sorted(available_claim_statuses_df["status"].tolist())

            min_max_date_query = "SELECT MIN(timestamp), MAX(timestamp) FROM claims"
            min_date_db, max_date_db = pd.read_sql(min_max_date_query, conn).iloc[0]
            # Convert to datetime.date objects for st.date_input
            min_date_db = min_date_db.date() if min_date_db else datetime.now().date()
            max_date_db = max_date_db.date() if max_date_db else datetime.now().date()

        except Exception as e:
            st.error(f"Could not fetch filter options for Claims. Error: {e}")
            available_claim_statuses = ["All"]
            min_date_db = datetime.now().date()
            max_date_db = datetime.now().date()

        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            claim_status_selected = st.selectbox("Filter by Claim Status", available_claim_statuses, key="claim_status_filter")
        with col_filter2:
            date_range = st.date_input("Filter by Claim Date Range",
                                       value=(min_date_db, max_date_db),
                                       min_value=min_date_db,
                                       max_value=max_date_db,
                                       key="claim_date_filter")

        query = "SELECT * FROM claims WHERE 1=1"
        params = []

        if claim_status_selected != "All":
            query += " AND status = %s"
            params.append(claim_status_selected)
        
        # Handle date range filter
        if len(date_range) == 2:
            start_date = date_range[0]
            end_date = date_range[1]
            query += " AND timestamp BETWEEN %s AND %s"
            params.append(start_date.strftime('%Y-%m-%d'))
            params.append(end_date.strftime('%Y-%m-%d'))
        
        df_display = pd.read_sql(query, conn, params=tuple(params))
        st.dataframe(df_display)
        if df_display.empty:
            st.info("No claims found matching the selected filters.")

    # --- Initial message when no table is selected ---
    elif st.session_state.current_table_view is None:
        st.info("Click a button above to view a table and apply filters.")

#CRUD Operations
elif choice == "CRUD Operations":
    st.subheader("🛠️ CRUD Operations")

    crud_col1, crud_col2 = st.columns(2)
    with crud_col1:
        if st.button("Add New Record", key="add_new_record_btn"):
            st.session_state.crud_form_view = "add_new"
            st.session_state.current_table_view = None # Clear table view
        if st.button("Update Existing Record", key="update_existing_record_btn"):
            st.session_state.crud_form_view = "update_existing"
            st.session_state.current_table_view = None # Clear table view
    with crud_col2:
        if st.button("Delete Record", key="delete_record_btn"):
            st.session_state.crud_form_view = "delete_record"
            st.session_state.current_table_view = None # Clear table view

    st.markdown("---")

    # --- Add New Record Forms ---
    if st.session_state.crud_form_view == "add_new":
        st.subheader("➕ Add New Record")
        add_type = st.radio("Select type of record to add:", ["Provider", "Receiver", "Food Listing", "Claim"], key="add_type_radio")

        if add_type == "Provider":
            with st.form("Add New Provider Form", clear_on_submit=True):
                st.markdown("#### Add New Provider")
                # provider_id is AUTO_INCREMENT in DB, so no input needed
                name = st.text_input("Provider Name*", max_chars=255)
                provider_type = st.selectbox("Provider Type*", ["Restaurant", "NGO", "Individual", "Supermarket", "Catering Service"], key="add_prov_type")
                address = st.text_input("Address*", max_chars=255)
                city = st.text_input("City*", max_chars=100)
                contact = st.text_input("Phone", max_chars=20)
                
                submit_add_provider = st.form_submit_button("Submit Provider")
                if submit_add_provider:
                    if name and provider_type and address and city: # Phone can be optional
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO providers (name, type, address, city, contact) VALUES (%s, %s, %s, %s, %s)",
                                (name, provider_type, address, city, contact)
                            )
                            conn.commit()
                            st.success("✅ Provider added successfully!")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error adding provider: {err}")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please fill in all required fields (marked with *).")

        elif add_type == "Receiver":
            with st.form("Add New Receiver Form", clear_on_submit=True):
                st.markdown("#### Add New Receiver")
                # receiver_id is AUTO_INCREMENT in DB
                name = st.text_input("Receiver Name*", max_chars=255)
                receiver_type = st.selectbox("Receiver Type*", ["NGO", "Individual", "Shelter", "Food Bank"], key="add_rec_type")
                city = st.text_input("City*", max_chars=100)
                contact = st.text_input("Phone", max_chars=20)

                submit_add_receiver = st.form_submit_button("Submit Receiver")
                if submit_add_receiver:
                    if name and receiver_type and city:
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO receivers (name, type, city, contact) VALUES (%s, %s, %s, %s)",
                                (name, receiver_type, city, contact)
                            )
                            conn.commit()
                            st.success("✅ Receiver added successfully!")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error adding receiver: {err}")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please fill in all required fields (marked with *).")

        elif add_type == "Food Listing":
            with st.form("Add New Food Listing Form", clear_on_submit=True):
                st.markdown("#### Add New Food Listing")
                # Claim_ID is AUTO_INCREMENT
                food_name = st.text_input("Food Name*", max_chars=255)
                food_type = st.selectbox("Food Type*", ["Vegetarian", "Non-Vegetarian", "Vegan", "Gluten-Free"], key="add_food_type")
                meal_type = st.selectbox("Meal Type*", ["Breakfast", "Lunch", "Dinner", "Snacks", "Any"], key="add_meal_type")
                quantity = st.number_input("Quantity (in kg)*", min_value=0.1, step=0.1)
                expiry_date = st.date_input("Expiry Date*", min_value=datetime.now().date())
                location_city = st.text_input("Location City*", max_chars=100)
                
                # Fetch available provider IDs for selection
                provider_ids = []
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT provider_id, name FROM providers ORDER BY name")
                    provider_options = cursor.fetchall()
                    provider_ids = [f"{pid} - {name}" for pid, name in provider_options]
                except Exception as e:
                    st.warning(f"Could not fetch provider IDs: {e}. Please ensure providers table is populated.")
                finally:
                    cursor.close()

                selected_provider_id_str = st.selectbox("Select Provider*", [""] + provider_ids, key="add_listing_provider_id")
                
                submit_add_listing = st.form_submit_button("Submit Food Listing")
                if submit_add_listing:
                    if food_name and food_type and meal_type and quantity and expiry_date and location_city and selected_provider_id_str:
                        try:
                            provider_id = int(selected_provider_id_str.split(' - ')[0]) # Extract ID
                            cursor = conn.cursor()
                            # listed_date will be current datetime
                            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute(
                                "INSERT INTO food_listings (food_name, food_type, meal_type, quantity, expiry_date, location_city, provider_id, listed_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (food_name, food_type, meal_type, quantity, expiry_date, location_city, provider_id, current_datetime, "Available")
                            )
                            conn.commit()
                            st.success("✅ Food listing added successfully!")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error adding food listing: {err}")
                        except ValueError:
                            st.error("❌ Invalid Provider ID selected.")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please fill in all required fields (marked with *).")

        elif add_type == "Claim":
            with st.form("Add New Claim Form", clear_on_submit=True):
                st.markdown("#### Add New Claim")
                # claim_id is AUTO_INCREMENT
                
                # Fetch available food listing IDs
                Claim_IDs = []
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT Claim_ID, food_name FROM food_listings ORDER BY food_name")
                    listing_options = cursor.fetchall()
                    Claim_IDs = [f"{lid} - {item}" for lid, item in listing_options]
                except Exception as e:
                    st.warning(f"Could not fetch food listing IDs: {e}. Please ensure food listings table is populated.")
                finally:
                    cursor.close()

                selected_Claim_ID_str = st.selectbox("Select Food Listing*", [""] + Claim_IDs, key="add_claim_Claim_ID")

                # Fetch available receiver IDs
                receiver_ids = []
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT receiver_id, name FROM receivers ORDER BY name")
                    receiver_options = cursor.fetchall()
                    receiver_ids = [f"{rid} - {name}" for rid, name in receiver_options]
                except Exception as e:
                    st.warning(f"Could not fetch receiver IDs: {e}. Please ensure receivers table is populated.")
                finally:
                    cursor.close()

                selected_receiver_id_str = st.selectbox("Select Receiver*", [""] + receiver_ids, key="add_claim_receiver_id")
                
                quantity_claimed = st.number_input("Quantity Claimed (in kg)*", min_value=0.1, step=0.1)
                status = st.selectbox("Claim Status*", ["Pending", "Approved", "Rejected", "Completed", "Cancelled"], key="add_claim_status")
                
                submit_add_claim = st.form_submit_button("Submit Claim")
                if submit_add_claim:
                    if selected_Claim_ID_str and selected_receiver_id_str and quantity_claimed and status:
                        try:
                            Claim_ID = int(selected_Claim_ID_str.split(' - ')[0])
                            receiver_id = int(selected_receiver_id_str.split(' - ')[0])
                            cursor = conn.cursor()
                            # claim_date will be current datetime
                            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute(
                                "INSERT INTO claims (Claim_ID, receiver_id, quantity_claimed, status, timestamp) VALUES (%s, %s, %s, %s, %s)",
                                (Claim_ID, receiver_id, quantity_claimed, status, current_datetime)
                            )
                            conn.commit()
                            st.success("✅ Claim added successfully!")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error adding claim: {err}")
                        except ValueError:
                            st.error("❌ Invalid Listing ID or Receiver ID selected.")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please fill in all required fields (marked with *).")

    # --- Update Existing Record Forms ---
    elif st.session_state.crud_form_view == "update_existing":
        st.subheader("✏️ Update Existing Record")
        update_type = st.radio("Select type of record to update:", ["Provider", "Receiver", "Food Listing", "Claim"], key="update_type_radio")

        if update_type == "Provider":
            with st.form("Update Provider Form", clear_on_submit=True):
                st.markdown("#### Update Provider")
                provider_id_to_update = st.number_input("Provider ID to Update*", min_value=1, step=1, key="upd_prov_id")
                
                # Optional: Fetch current data for pre-filling
                current_data = {}
                if provider_id_to_update:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT name, type, address, city, contact FROM providers WHERE provider_id = %s", (provider_id_to_update,))
                        result = cursor.fetchone()
                        if result:
                            current_data = {
                                "name": result[0], "type": result[1], "address": result[2],
                                "city": result[3], "contact": result[4]}
                            st.info(f"Current data for Provider ID {provider_id_to_update} loaded. Fill fields to update.")
                        else:
                            st.warning(f"No provider found with ID {provider_id_to_update}.")
                    except Exception as e:
                        st.error(f"Error fetching current provider data: {e}")
                    finally:
                        cursor.close()

                name = st.text_input("New Provider Name", value=current_data.get("name", ""), max_chars=255)
                provider_type = st.selectbox("New Provider Type", ["Restaurant", "NGO", "Grocery Store", "Individual", "Supermarket", "Catering Service"], index=["Restaurant", "NGO", "Grocery Store", "Individual", "Supermarket", "Catering Service"].index(current_data.get("type", "Restaurant")) if current_data.get("type") else 0, key="upd_prov_type")
                address = st.text_input("New Address", value=current_data.get("address", ""), max_chars=255)
                city = st.text_input("New City", value=current_data.get("city", ""), max_chars=100)
                contact = st.text_input("New Phone", value=current_data.get("contact", ""), max_chars=20)
                
                submit_update_provider = st.form_submit_button("Update Provider")
                if submit_update_provider:
                    if provider_id_to_update and name and provider_type and address and city:
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE providers SET name=%s, type=%s, address=%s, city=%s, contact=%s WHERE provider_id=%s",
                                (name, provider_type, address, city, contact, provider_id_to_update)
                            )
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Provider ID {provider_id_to_update} updated successfully!")
                            else:
                                st.warning(f"No changes made or Provider ID {provider_id_to_update} not found.")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error updating provider: {err}")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please fill in Provider ID and all required fields.")

        elif update_type == "Receiver":
            with st.form("Update Receiver Form", clear_on_submit=True):
                st.markdown("#### Update Receiver")
                receiver_id_to_update = st.number_input("Receiver ID to Update*", min_value=1, step=1, key="upd_rec_id")

                current_data = {}
                if receiver_id_to_update:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT name, type, city, contact FROM receivers WHERE receiver_id = %s", (receiver_id_to_update,))
                        result = cursor.fetchone()
                        if result:
                            current_data = {
                                "name": result[0], "type": result[1], "city": result[2], "contact": result[3]
                            }
                            st.info(f"Current data for Receiver ID {receiver_id_to_update} loaded. Fill fields to update.")
                        else:
                            st.warning(f"No receiver found with ID {receiver_id_to_update}.")
                    except Exception as e:
                        st.error(f"Error fetching current receiver data: {e}")
                    finally:
                        cursor.close()

                name = st.text_input("New Receiver Name", value=current_data.get("name", ""), max_chars=255)
                receiver_type = st.selectbox("New Receiver Type", ["NGO", "Individual", "Shelter", "Food Bank"], index=["NGO", "Individual", "Shelter", "Food Bank"].index(current_data.get("type", "NGO")) if current_data.get("type") else 0, key="upd_rec_type")
                city = st.text_input("New City", value=current_data.get("city", ""), max_chars=100)
                contact = st.text_input("New Phone", value=current_data.get("contact", ""), max_chars=20)
                
                submit_update_receiver = st.form_submit_button("Update Receiver")
                if submit_update_receiver:
                    if receiver_id_to_update and name and receiver_type and city:
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE receivers SET name=%s, type=%s, city=%s, contact=%s WHERE receiver_id=%s",
                                (name, receiver_type, city, contact, receiver_id_to_update)
                            )
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Receiver ID {receiver_id_to_update} updated successfully!")
                            else:
                                st.warning(f"No changes made or Receiver ID {receiver_id_to_update} not found.")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error updating receiver: {err}")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please fill in Receiver ID and all required fields.")

        elif update_type == "Food Listing":
            with st.form("Update Food Listing Form", clear_on_submit=True):
                st.markdown("#### Update Food Listing")
                Claim_ID_to_update = st.number_input("Food Listing ID to Update*", min_value=1, step=1, key="upd_list_id")

                current_data = {}
                if Claim_ID_to_update:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT food_name, food_type, meal_type, quantity, expiry_date, location_city, provider_id, status FROM food_listings WHERE Claim_ID = %s", (Claim_ID_to_update,))
                        result = cursor.fetchone()
                        if result:
                            current_data = {
                                "food_name": result[0], "food_type": result[1], "meal_type": result[2],
                                "quantity": result[3], "expiry_date": result[4], "location_city": result[5],
                                "provider_id": result[6], "status": result[7]
                            }
                            st.info(f"Current data for Food Listing ID {Claim_ID_to_update} loaded. Fill fields to update.")
                        else:
                            st.warning(f"No food listing found with ID {Claim_ID_to_update}.")
                    except Exception as e:
                        st.error(f"Error fetching current food listing data: {e}")
                    finally:
                        cursor.close()

                food_name = st.text_input("New Food Item Name", value=current_data.get("food_name", ""), max_chars=255)
                food_type_options = ["Vegetarian", "Non-Vegetarian", "Vegan", "Gluten-Free"]
                food_type = st.selectbox("New Food Type", food_type_options, index=food_type_options.index(current_data.get("food_type", "Vegetarian")) if current_data.get("food_type") else 0, key="upd_food_type")
                meal_type_options = ["Breakfast", "Lunch", "Dinner", "Snacks", "Any"]
                meal_type = st.selectbox("New Meal Type", meal_type_options, index=meal_type_options.index(current_data.get("meal_type", "Any")) if current_data.get("meal_type") else 0, key="upd_meal_type")
                quantity = st.number_input("New Quantity (in kg)", min_value=0.1, step=0.1, value=float(current_data.get("quantity", 0.1)))
                expiry_date = st.date_input("New Expiry Date", value=current_data.get("expiry_date", datetime.now().date()), min_value=datetime.now().date(), key="upd_expiry_date")
                location_city = st.text_input("New Location City", value=current_data.get("location_city", ""), max_chars=100)
                
                # Fetch available provider IDs for selection
                provider_ids_options = []
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT provider_id, name FROM providers ORDER BY name")
                    provider_options = cursor.fetchall()
                    provider_ids_options = [f"{pid} - {name}" for pid, name in provider_options]
                except Exception as e:
                    st.warning(f"Could not fetch provider IDs: {e}. Please ensure providers table is populated.")
                finally:
                    cursor.close()
                
                # Set default index for selectbox
                default_provider_index = 0
                if current_data.get("provider_id"):
                    try:
                        default_provider_str = f"{current_data['provider_id']} - {current_data.get('provider_name', '')}" # Assuming provider_name can be fetched
                        if default_provider_str in provider_ids_options:
                            default_provider_index = provider_ids_options.index(default_provider_str) + 1 # +1 for " " option
                    except:
                        pass # Fallback to default 0 if not found

                selected_provider_id_str = st.selectbox("New Provider ID", [""] + provider_ids_options, index=default_provider_index, key="upd_listing_provider_id")
                
                status_options = ["Available", "Claimed", "Expired", "Pending"]
                status = st.selectbox("New Status", status_options, index=status_options.index(current_data.get("status", "Available")) if current_data.get("status") else 0, key="upd_listing_status")

                submit_update_listing = st.form_submit_button("Update Food Listing")
                if submit_update_listing:
                    if Claim_ID_to_update and food_name and food_type and meal_type and quantity and expiry_date and location_city and selected_provider_id_str and status:
                        try:
                            provider_id = int(selected_provider_id_str.split(' - ')[0])
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE food_listings SET food_name=%s, food_type=%s, meal_type=%s, quantity=%s, expiry_date=%s, location_city=%s, provider_id=%s, status=%s WHERE Claim_ID=%s",
                                (food_name, food_type, meal_type, quantity, expiry_date, location_city, provider_id, status, Claim_ID_to_update)
                            )
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Food listing ID {Claim_ID_to_update} updated successfully!")
                            else:
                                st.warning(f"No changes made or Food listing ID {Claim_ID_to_update} not found.")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error updating food listing: {err}")
                        except ValueError:
                            st.error("❌ Invalid Provider ID selected.")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please fill in Food Listing ID and all required fields.")

        elif update_type == "Claim":
            with st.form("Update Claim Form", clear_on_submit=True):
                st.markdown("#### Update Claim")
                claim_id_to_update = st.number_input("Claim ID to Update*", min_value=1, step=1, key="upd_claim_id")

                current_data = {}
                if claim_id_to_update:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT Claim_ID, receiver_id, quantity_claimed, status, timestamp FROM claims WHERE claim_id = %s", (claim_id_to_update,))
                        result = cursor.fetchone()
                        if result:
                            current_data = {
                                "Claim_ID": result[0], "receiver_id": result[1], "quantity_claimed": result[2],
                                "status": result[3], "timestamp": result[4]
                            }
                            st.info(f"Current data for Claim ID {claim_id_to_update} loaded. Fill fields to update.")
                        else:
                            st.warning(f"No claim found with ID {claim_id_to_update}.")
                    except Exception as e:
                        st.error(f"Error fetching current claim data: {e}")
                    finally:
                        cursor.close()

                # Fetch available food listing IDs
                Claim_IDs_options = []
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT Claim_ID, food_name FROM food_listings ORDER BY food_name")
                    listing_options = cursor.fetchall()
                    Claim_IDs_options = [f"{lid} - {item}" for lid, item in listing_options]
                except Exception as e:
                    st.warning(f"Could not fetch food listing IDs: {e}. Please ensure food listings table is populated.")
                finally:
                    cursor.close()

                # Set default index for selectbox
                default_listing_index = 0
                if current_data.get("Claim_ID"):
                    try:
                        default_listing_str = f"{current_data['Claim_ID']} - {current_data.get('food_name', '')}" 
                        if default_listing_str in Claim_IDs_options:
                            default_listing_index = Claim_IDs_options.index(default_listing_str) + 1
                    except:
                        pass # Fallback to default 0 if not found

                selected_Claim_ID_str = st.selectbox("New Food Listing ID", [""] + Claim_IDs_options, index=default_listing_index, key="upd_claim_Claim_ID")

                # Fetch available receiver IDs
                receiver_ids_options = []
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT receiver_id, name FROM receivers ORDER BY name")
                    receiver_options = cursor.fetchall()
                    receiver_ids_options = [f"{rid} - {name}" for rid, name in receiver_options]
                except Exception as e:
                    st.warning(f"Could not fetch receiver IDs: {e}. Please ensure receivers table is populated.")
                finally:
                    cursor.close()

                # Set default index for selectbox
                default_receiver_index = 0
                if current_data.get("receiver_id"):
                    try:
                        default_receiver_str = f"{current_data['receiver_id']} - {current_data.get('receiver_name', '')}" # Assuming receiver_name can be fetched
                        if default_receiver_str in receiver_ids_options:
                            default_receiver_index = receiver_ids_options.index(default_receiver_str) + 1 # +1 for " " option
                    except:
                        pass # Fallback to default 0 if not found

                selected_receiver_id_str = st.selectbox("New Receiver ID", [""] + receiver_ids_options, index=default_receiver_index, key="upd_claim_receiver_id")
                
                quantity_claimed = st.number_input("New Quantity Claimed (in kg)", min_value=0.1, step=0.1, value=float(current_data.get("quantity_claimed", 0.1)))
                status_options = ["Pending", "Approved", "Rejected", "Completed", "Cancelled"]
                status = st.selectbox("New Claim Status", status_options, index=status_options.index(current_data.get("status", "Pending")) if current_data.get("status") else 0, key="upd_claim_status")
                timestamp = st.date_input("New Claim Date", value=current_data.get("timestamp", datetime.now().date()), key="upd_claim_date")

                submit_update_claim = st.form_submit_button("Update Claim")
                if submit_update_claim:
                    if claim_id_to_update and selected_Claim_ID_str and selected_receiver_id_str and quantity_claimed and status and timestamp:
                        try:
                            Claim_ID = int(selected_Claim_ID_str.split(' - ')[0])
                            receiver_id = int(selected_receiver_id_str.split(' - ')[0])
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE claims SET Claim_ID=%s, receiver_id=%s, quantity_claimed=%s, status=%s, timestamp=%s WHERE claim_id=%s",
                                (Claim_ID, receiver_id, quantity_claimed, status, timestamp, claim_id_to_update)
                            )
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Claim ID {claim_id_to_update} updated successfully!")
                            else:
                                st.warning(f"No changes made or Claim ID {claim_id_to_update} not found.")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error updating claim: {err}")
                        except ValueError:
                            st.error("❌ Invalid Listing ID or Receiver ID selected.")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please fill in Claim ID and all required fields.")

    # --- Delete Record Forms ---
    elif st.session_state.crud_form_view == "delete_record":
        st.subheader("🗑️ Delete Record")
        delete_type = st.radio("Select type of record to delete:", ["Provider", "Receiver", "Food Listing", "Claim"], key="delete_type_radio")

        if delete_type == "Provider":
            with st.form("Delete Provider Form", clear_on_submit=True):
                st.markdown("#### Delete Provider")
                provider_id_to_delete = st.number_input("Provider ID to Delete*", min_value=1, step=1, key="del_prov_id")
                submit_delete_provider = st.form_submit_button("Delete Provider")
                if submit_delete_provider:
                    if provider_id_to_delete:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM providers WHERE provider_id = %s", (provider_id_to_delete,))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Provider ID {provider_id_to_delete} deleted successfully!")
                            else:
                                st.warning(f"No provider found with ID {provider_id_to_delete}.")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error deleting provider: {err}")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please enter a Provider ID to delete.")

        elif delete_type == "Receiver":
            with st.form("Delete Receiver Form", clear_on_submit=True):
                st.markdown("#### Delete Receiver")
                receiver_id_to_delete = st.number_input("Receiver ID to Delete*", min_value=1, step=1, key="del_rec_id")
                submit_delete_receiver = st.form_submit_button("Delete Receiver")
                if submit_delete_receiver:
                    if receiver_id_to_delete:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM receivers WHERE receiver_id = %s", (receiver_id_to_delete,))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Receiver ID {receiver_id_to_delete} deleted successfully!")
                            else:
                                st.warning(f"No receiver found with ID {receiver_id_to_delete}.")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error deleting receiver: {err}")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please enter a Receiver ID to delete.")

        elif delete_type == "Food Listing":
            with st.form("Delete Food Listing Form", clear_on_submit=True):
                st.markdown("#### Delete Food Listing")
                Claim_ID_to_delete = st.number_input("Food Listing ID to Delete*", min_value=1, step=1, key="del_list_id")
                submit_delete_listing = st.form_submit_button("Delete Food Listing")
                if submit_delete_listing:
                    if Claim_ID_to_delete:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM food_listings WHERE Claim_ID = %s", (Claim_ID_to_delete,))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Food Listing ID {Claim_ID_to_delete} deleted successfully!")
                            else:
                                st.warning(f"No food listing found with ID {Claim_ID_to_delete}.")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error deleting food listing: {err}")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please enter a Food Listing ID to delete.")

        elif delete_type == "Claim":
            with st.form("Delete Claim Form", clear_on_submit=True):
                st.markdown("#### Delete Claim")
                claim_id_to_delete = st.number_input("Claim ID to Delete*", min_value=1, step=1, key="del_claim_id")
                submit_delete_claim = st.form_submit_button("Delete Claim")
                if submit_delete_claim:
                    if claim_id_to_delete:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM claims WHERE claim_id = %s", (claim_id_to_delete,))
                            conn.commit()
                            if cursor.rowcount > 0:
                                st.success(f"✅ Claim ID {claim_id_to_delete} deleted successfully!")
                            else:
                                st.warning(f"No claim found with ID {claim_id_to_delete}.")
                        except mysql.connector.Error as err:
                            st.error(f"❌ Error deleting claim: {err}")
                        finally:
                            cursor.close()
                    else:
                        st.error("❌ Please enter a Claim ID to delete.")

    # --- Initial message when no CRUD form is selected ---
    elif st.session_state.crud_form_view is None:
        st.info("Select an operation (Add, Update, Delete) above to manage records.")

#SQL Queries & Visualizations
if choice == "SQL Queries & Visualizations":
    st.subheader("📊 SQL Queries & Visualizations")
    # Clear other session states if they exist (important when integrating into a larger app)
    if 'current_table_view' in st.session_state:
        st.session_state.current_table_view = None
    if 'crud_form_view' in st.session_state:
        st.session_state.crud_form_view = None

    query_buttons_col1, query_buttons_col2, query_buttons_col3 = st.columns(3)

    with query_buttons_col1:
        if st.button("City Wise Providers and Receivers", key="city_wise_pr_btn"):
            st.session_state.current_query_view = "city_wise_pr"
        if st.button("Top Food Provider", key="top_food_provider_btn"):
            st.session_state.current_query_view = "top_food_provider"
        if st.button("Contact Info of Providers in City", key="contact_info_providers_btn"):
            st.session_state.current_query_view = "contact_info_providers"
        if st.button("Receiver with Most Claims", key="receiver_most_claims_btn"):
            st.session_state.current_query_view = "receiver_most_claims"

    with query_buttons_col2:
        if st.button("Total Quantity of Food from Each Provider Type", key="total_qty_by_prov_type_btn"):
            st.session_state.current_query_view = "total_qty_by_prov_type"
        if st.button("City with Most Food Listings", key="city_most_listings_btn"):
            st.session_state.current_query_view = "city_most_listings"
        if st.button("Commonly Available Food Types", key="common_food_types_btn"):
            st.session_state.current_query_view = "common_food_types"
        if st.button("Food Claims by Item Type", key="claims_by_item_type_btn"):
            st.session_state.current_query_view = "claims_by_item_type"

    with query_buttons_col3:
        if st.button("Provider with Highest Number of Claims", key="provider_highest_claims_btn"):
            st.session_state.current_query_view = "provider_highest_claims"
        if st.button("Claims Status Ratio", key="claims_status_ratio_btn"):
            st.session_state.current_query_view = "claims_status_ratio"
        if st.button("Average Quantity Claimed per Receiver", key="avg_qty_claimed_per_receiver_btn"):
            st.session_state.current_query_view = "avg_qty_claimed_per_receiver"
        if st.button("Most Claimed Meal Type", key="most_claimed_meal_type_btn"):
            st.session_state.current_query_view = "most_claimed_meal_type"
        if st.button("Total Quantity Donated by Each Provider", key="total_qty_donated_by_provider_btn"):
            st.session_state.current_query_view = "total_qty_donated_by_provider"

    st.markdown("---")

    # --- Conditional Display of Query Results ---
if "current_query_view" not in st.session_state:
    st.session_state.current_query_view = "home"

    if st.session_state.current_query_view == "city_wise_pr":
        st.subheader("🌆 City Wise Providers and Receivers")
        # Corrected column names: phone, email instead of Contact
        df_providers = pd.read_sql("SELECT provider_id, name, city, phone, email FROM providers ORDER BY city", conn)
        df_receivers = pd.read_sql("SELECT receiver_id, name, city, phone, email FROM receivers ORDER BY city", conn)

        st.write("### Providers")
        st.dataframe(df_providers)

        st.write("### Receivers")
        st.dataframe(df_receivers)

    elif st.session_state.current_query_view == "top_food_provider":
        st.subheader("🥇 Top Food Provider (by Total Quantity Donated)")
        # Corrected: SUM(quantity) from food_listings, grouped by provider type
        # Assuming 'type' is the column in 'providers' table for provider type
        # And 'quantity' is the column in 'food_listings'
        query = """
        SELECT p.type, SUM(fl.quantity) AS Total_Quantity
        FROM food_listings fl
        JOIN providers p ON fl.provider_id = p.provider_id
        GROUP BY p.type
        ORDER BY Total_Quantity DESC
        LIMIT 1
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df)
            # Plotting the top provider with other providers (fetching all for plot)
            df_all_providers_qty = pd.read_sql("""
                SELECT p.type, SUM(fl.quantity) AS Total_Quantity
                FROM food_listings fl
                JOIN providers p ON fl.provider_id = p.provider_id
                GROUP BY p.type
                ORDER BY Total_Quantity DESC
            """, conn)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='type', y='Total_Quantity', data=df_all_providers_qty, ax=ax, palette='viridis')
            ax.set_title('Total Food Quantity Donated by Provider Type', fontsize=16)
            ax.set_xlabel('Provider Type', fontsize=12)
            ax.set_ylabel('Total Quantity (kg)', fontsize=12)
            st.pyplot(fig)
        else:
            st.info("No data available to determine the top food provider.")

    elif st.session_state.current_query_view == "contact_info_providers":
        st.subheader("📞 Contact Info of Providers in a Specific City")
        
        # Add a selectbox for city filter within this view
        try:
            provider_cities_query = "SELECT DISTINCT city FROM providers"
            available_provider_cities_df = pd.read_sql(provider_cities_query, conn)
            available_provider_cities = ["All"] + sorted(available_provider_cities_df["city"].tolist())
        except Exception as e:
            st.error(f"Could not fetch cities for provider contact info. Error: {e}")
            available_provider_cities = ["All"]

        city_selected_contact = st.selectbox("Select City", available_provider_cities, key="contact_prov_city_filter")

        # Corrected column names: phone, email instead of Contact
        query = "SELECT name, address, phone, email, city FROM providers WHERE 1=1"
        params = []
        if city_selected_contact != "All":
            query += " AND city = %s"
            params.append(city_selected_contact)
        query += " ORDER BY city"

        df = pd.read_sql(query, conn, params=tuple(params))
        if not df.empty:
            st.dataframe(df)
        else:
            st.info(f"No provider contact information found for {city_selected_contact}.")

    elif st.session_state.current_query_view == "receiver_most_claims":
        st.subheader("🏆 Receiver with Most Claims (Top 5)")
        # Corrected: Use receiver_id from claims, join with receivers table
        query = """
        SELECT r.name, COUNT(c.claim_id) AS Total_Claims
        FROM claims c
        JOIN receivers r ON c.receiver_id = r.receiver_id
        GROUP BY r.name
        ORDER BY Total_Claims DESC
        LIMIT 5
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='name', y='Total_Claims', data=df, ax=ax, palette='magma')
            ax.set_title('Top 5 Receivers by Number of Claims', fontsize=16)
            ax.set_xlabel('Receiver Name', fontsize=12)
            ax.set_ylabel('Total Claims', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.info("No claims data available to determine receiver with most claims.")

    elif st.session_state.current_query_view == "total_qty_by_prov_type":
        st.subheader("📊 Total Quantity of Food from Each Provider Type")
        # Corrected: SUM(quantity) from food_listings, grouped by provider type
        query = """
        SELECT p.type, SUM(fl.quantity) AS Total_Quantity
        FROM food_listings fl
        JOIN providers p ON fl.provider_id = p.provider_id
        GROUP BY p.type
        ORDER BY Total_Quantity DESC
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='type', y='Total_Quantity', data=df, ax=ax, palette='viridis')
            ax.set_title('Total Food Quantity Donated by Provider Type', fontsize=16)
            ax.set_xlabel('Provider Type', fontsize=12)
            ax.set_ylabel('Total Quantity (kg)', fontsize=12)
            st.pyplot(fig)
        else:
            st.info("No food listings available to calculate total quantity by provider type.")

    elif st.session_state.current_query_view == "city_most_listings":
        st.subheader("🌍 City with Most Food Listings")
        # Corrected: Use location_city from food_listings
        query = """
        SELECT location_city, COUNT(*) AS Total_Listings
        FROM food_listings
        GROUP BY location_city
        ORDER BY Total_Listings DESC
        LIMIT 1
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df)
            # Plotting all cities for context
            df_all_cities = pd.read_sql("""
                SELECT location_city, COUNT(*) AS Total_Listings
                FROM food_listings
                GROUP BY location_city
                ORDER BY Total_Listings DESC
            """, conn)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='location_city', y='Total_Listings', data=df_all_cities, ax=ax, palette='cubehelix')
            ax.set_title('Total Food Listings by City', fontsize=16)
            ax.set_xlabel('City', fontsize=12)
            ax.set_ylabel('Total Listings', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.info("No food listings available to determine the city with most listings.")

    elif st.session_state.current_query_view == "common_food_types":
        st.subheader("🍽️ Commonly Available Food Types")
        # Corrected: Use food_type from food_listings
        query = """
        SELECT food_type, COUNT(*) AS Total
        FROM food_listings
        GROUP BY food_type
        ORDER BY Total DESC
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='food_type', y='Total', data=df, ax=ax, palette='tab10')
            ax.set_title('Commonly Available Food Types', fontsize=16)
            ax.set_xlabel('Food Type', fontsize=12)
            ax.set_ylabel('Total Listings', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.info("No food listings available to determine commonly available food types.")

    elif st.session_state.current_query_view == "claims_by_item_type":
        st.subheader("📋 Food Claims by Item Type")
        # Corrected: Use listing_id from claims, join with food_listings for food_item
        query = """
        SELECT fl.food_item, COUNT(c.claim_id) AS Claim_Count
        FROM claims c
        JOIN food_listings fl ON c.listing_id = fl.listing_id
        GROUP BY fl.food_item
        ORDER BY Claim_Count DESC
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='food_item', y='Claim_Count', data=df, ax=ax, palette='GnBu_d')
            ax.set_title('Food Claims by Item Type', fontsize=16)
            ax.set_xlabel('Food Item', fontsize=12)
            ax.set_ylabel('Claim Count', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.info("No claims data available for food claims by item type.")

    elif st.session_state.current_query_view == "provider_highest_claims":
        st.subheader("🏅 Provider with Highest Number of Claims")
        # Corrected: Join claims -> food_listings -> providers
        query = """
        SELECT p.name, COUNT(c.claim_id) AS Total_Claims
        FROM claims c
        JOIN food_listings fl ON c.listing_id = fl.listing_id
        JOIN providers p ON fl.provider_id = p.provider_id
        GROUP BY p.name
        ORDER BY Total_Claims DESC
        LIMIT 1
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df)
            # Plotting all providers for context
            df_all_providers_claims = pd.read_sql("""
                SELECT p.name, COUNT(c.claim_id) AS Total_Claims
                FROM claims c
                JOIN food_listings fl ON c.listing_id = fl.listing_id
                JOIN providers p ON fl.provider_id = p.provider_id
                GROUP BY p.name
                ORDER BY Total_Claims DESC
            """, conn)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='name', y='Total_Claims', data=df_all_providers_claims, ax=ax, palette='rocket')
            ax.set_title('Total Claims by Provider', fontsize=16)
            ax.set_xlabel('Provider Name', fontsize=12)
            ax.set_ylabel('Total Claims', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.info("No claims data available to determine provider with highest claims.")

    elif st.session_state.current_query_view == "claims_status_ratio":
        st.subheader("📊 Claims Status Ratio")
        # Corrected: Use 'status' column from claims table
        query = "SELECT status, COUNT(*) AS Count FROM claims GROUP BY status"
        df = pd.read_sql(query, conn)
        
        if not df.empty:
            total_claims = df['Count'].sum()
            df['Ratio'] = df['Count'] / total_claims
            st.dataframe(df)
            
            # Plotting the ratio
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x='status', y='Ratio', data=df, ax=ax, palette='pastel')
            ax.set_title('Claims Status Ratio', fontsize=16)
            ax.set_xlabel('Status', fontsize=12)
            ax.set_ylabel('Ratio', fontsize=12)
            st.pyplot(fig)
        else:
            st.info("No claims data available to calculate claims status ratio.")

    elif st.session_state.current_query_view == "avg_qty_claimed_per_receiver":
        st.subheader("📈 Average Quantity of Food Claimed per Receiver")
        # Corrected: Join claims -> food_listings (for quantity) -> receivers
        query = """
        SELECT r.name, AVG(c.quantity_claimed) AS Average_Quantity_Claimed
        FROM claims c
        JOIN receivers r ON c.receiver_id = r.receiver_id
        GROUP BY r.name
        ORDER BY Average_Quantity_Claimed DESC
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='name', y='Average_Quantity_Claimed', data=df, ax=ax, palette='Greens_d')
            ax.set_title('Average Quantity of Food Claimed per Receiver', fontsize=16)
            ax.set_xlabel('Receiver Name', fontsize=12)
            ax.set_ylabel('Average Quantity Claimed (kg)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.info("No claims data available to calculate average quantity claimed per receiver.")

    elif st.session_state.current_query_view == "most_claimed_meal_type":
        st.subheader("🍽️ Most Claimed Meal Type")
        # Corrected: Join claims -> food_listings for meal_type
        query = """
        SELECT fl.meal_type, COUNT(c.claim_id) AS Claim_Count
        FROM claims c
        JOIN food_listings fl ON c.listing_id = fl.listing_id
        GROUP BY fl.meal_type
        ORDER BY Claim_Count DESC
        LIMIT 1
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df)
            # Plotting all meal types for context
            df_all_meal_types = pd.read_sql("""
                SELECT fl.meal_type, COUNT(c.claim_id) AS Claim_Count
                FROM claims c
                JOIN food_listings fl ON c.listing_id = fl.listing_id
                GROUP BY fl.meal_type
                ORDER BY Claim_Count DESC
            """, conn)
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x='meal_type', y='Claim_Count', data=df_all_meal_types, ax=ax, palette='Set2')
            ax.set_title('Claims by Meal Type', fontsize=16)
            ax.set_xlabel('Meal Type', fontsize=12)
            ax.set_ylabel('Claim Count', fontsize=12)
            st.pyplot(fig)
        else:
            st.info("No claims data available to determine the most claimed meal type.")

    elif st.session_state.current_query_view == "total_qty_donated_by_provider":
        st.subheader("📊 Total Quantity of Food Donated by Each Provider")
        # Corrected: Join food_listings -> providers
        query = """
        SELECT p.name, SUM(fl.quantity) AS Total_Quantity
        FROM food_listings fl
        JOIN providers p ON fl.provider_id = p.provider_id
        GROUP BY p.name
        ORDER BY Total_Quantity DESC
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            st.dataframe(df)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='name', y='Total_Quantity', data=df, ax=ax, palette='Blues_d')
            ax.set_title('Total Quantity of Food Donated by Each Provider', fontsize=16)
            ax.set_xlabel('Provider Name', fontsize=12)
            ax.set_ylabel('Total Quantity (kg)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.info("No food listings available to calculate total quantity donated by each provider.")
    
#Learner SQL Queries
if choice == "Learner SQL Queries":
    st.subheader("📝 Learner SQL Queries")
    
    # Query 1: Total Food Listings by Provider Type
    if st.button("Total Food Listings by Provider Type"):
        df = pd.read_sql("SELECT Provider_Type, COUNT(*) AS Total_Listings FROM food_listings GROUP BY Provider_Type", conn)
        st.dataframe(df)
        st.bar_chart(df.set_index('Provider_Type'))

    # Query 2: Total Claims by Status
    if st.button("Total Claims by Status"):
        df = pd.read_sql("SELECT Status, COUNT(*) AS Total_Claims FROM claims GROUP BY Status", conn)
        st.dataframe(df)
        st.bar_chart(df.set_index('Status'))
    
    # Query 3: Food Listings by City
    if st.button("Food Listings by City"):
        city = st.selectbox("Select City", ["All"] + sorted(pd.read_sql("SELECT DISTINCT Location FROM food_listings", conn)["Location"].tolist()))
        
        if city != "All":
            query = "SELECT * FROM food_listings WHERE Location = %s"
            df = pd.read_sql(query, conn, params=(city,))
        else:
            df = pd.read_sql("SELECT * FROM food_listings", conn)

        st.dataframe(df)

    # Query 4: Providers with Most Food Listings
    if st.button("Providers with Most Food Listings"):
        df = pd.read_sql("SELECT p.Name, COUNT(f.Food_ID) AS Total_Listings FROM food_listings f JOIN providers p ON f.Provider_ID = p.Provider_ID GROUP BY p.Name ORDER BY Total_Listings DESC LIMIT 5", conn)
        st.dataframe(df)
        st.bar_chart(df.set_index('Name')['Total_Listings'])
    
    # Query 5: Food Listings by Meal Type
    if st.button("Food Listings by Meal Type"):
        meal_type = st.selectbox("Select Meal Type", ["All"] + sorted(pd.read_sql("SELECT DISTINCT Meal_Type FROM food_listings", conn)["Meal_Type"].tolist()))
        
        if meal_type != "All":
            query = "SELECT * FROM food_listings WHERE Meal_Type = %s"
            df = pd.read_sql(query, conn, params=(meal_type,))
        else:
            df = pd.read_sql("SELECT * FROM food_listings", conn)
        st.dataframe(df)
        st.bar_chart(df.set_index('Meal_Type')['Quantity'])  
    # Query 6 Food Types with Most Listings
    if st.button("Food Types with Most Listings"):
        df = pd.read_sql("SELECT Food_Type, COUNT(*) AS Total_Listings FROM food_listings GROUP BY Food_Type ORDER BY Total_Listings DESC", conn)
        st.dataframe(df)
        st.bar_chart(df.set_index('Food_Type')['Total_Listings'])

    # Query 7: Average Quantity of Food per Listing
    if st.button("Average Quantity of Food per Listing"):
        df = pd.read_sql("SELECT Food_Type, Meal_Type, AVG(Quantity) AS Average_Quantity FROM food_listings", conn)
        st.dataframe(df)
        st.bar_chart(df.set_index(['Food_Type'])['Average_Quantity'])
    
    # Query 8: Food Listings by Provider
    if st.button("Food Listings by Provider"):
        provider_id = st.number_input("Enter Provider ID", min_value=1, step=1)
        df = pd.read_sql("SELECT * FROM food_listings WHERE Provider_ID = %s", conn, params=(provider_id,))

    # Query 9: Claims by Receiver
    if st.button("Claims by Receiver"):
        receiver_id = st.number_input("Enter Receiver ID", min_value=1, step=1)
        df = pd.read_sql("SELECT * FROM claims WHERE Receiver_ID = %s", conn, params=(receiver_id,))
        st.dataframe(df)
    
    # Query 10: Food Listings by Type
    if st.button("Food Listings by Type"):
        food_type = st.selectbox("Select Food Type", ["All"] + sorted(pd.read_sql("SELECT DISTINCT Food_Type FROM food_listings", conn)["Food_Type"].tolist()))
        
        if food_type != "All":
            query = "SELECT * FROM food_listings WHERE Food_Type = %s"
            df = pd.read_sql(query, conn, params=(food_type,))
        else:
            df = pd.read_sql("SELECT * FROM food_listings", conn)
        st.dataframe(df)

# User Introduction
if choice == "User Introduction":
    st.subheader("👤 User Introduction")
    st.write("""
    This project is developed by Muruga Prasaad MD as part of a local initiative to reduce food wastage and support community needs.
    """)