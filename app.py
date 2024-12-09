import streamlit as st
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import seaborn as sns


# Database connection for Streamlit
def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="crpm"
        )
        return conn
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None


# Display customer data with search
def view_customers(conn):
    st.write("### Customers")
    search_term = st.text_input("Search for a customer (by name, email, or phone):")
    try:
        cursor = conn.cursor(dictionary=True)
        if search_term:
            cursor.execute("""
                SELECT * FROM customers 
                WHERE (name LIKE %s OR email LIKE %s OR phone LIKE %s) AND status = 'Active'
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        else:
            cursor.execute("SELECT * FROM customers WHERE status = 'Active'")
        data = cursor.fetchall()
        if data:
            st.dataframe(data)
        else:
            st.info("No customers found.")
    except Error as e:
        st.error(f"Error fetching customers: {e}")


# Add new customer functionality
def add_new_customer(conn):
    st.write("### Add New Customer")
    with st.form(key="new_customer_form"):
        name = st.text_input("Customer Name")
        email = st.text_input("Customer Email")
        phone = st.text_input("Customer Phone")
        submitted = st.form_submit_button("Add Customer")
        
        if submitted:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)",
                               (name, email, phone))
                conn.commit()
                st.success("Customer added successfully!")
            except Error as e:
                st.error(f"Error: {e}")


# Display product data with search
def view_products(conn):
    st.write("### Products")
    search_term = st.text_input("Search for a product (by name or status):")
    try:
        cursor = conn.cursor(dictionary=True)
        if search_term:
            cursor.execute("""
                SELECT * FROM products 
                WHERE (name LIKE %s OR status LIKE %s)
            """, (f"%{search_term}%", f"%{search_term}%"))
        else:
            cursor.execute("SELECT * FROM products WHERE status = 'Available'")
        data = cursor.fetchall()
        if data:
            st.dataframe(data)
        else:
            st.info("No products found.")
    except Error as e:
        st.error(f"Error fetching products: {e}")


# Record purchase functionality
def record_purchase(conn):
    st.write("### Record a Purchase")
    with st.form(key="purchase_form"):
        customer_id = st.number_input("Customer ID", min_value=1, step=1)
        product_id = st.number_input("Product ID", min_value=1, step=1)
        quantity = st.number_input("Quantity", min_value=1, step=1)
        submitted = st.form_submit_button("Record Purchase")
        
        if submitted:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO purchases (customer_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                """, (customer_id, product_id, quantity))
                conn.commit()
                st.success("Purchase recorded successfully!")
            except Error as e:
                st.error(f"Error: {e}")


# Display analytics with visualizations
def show_analytics(conn):
    try:
        # Total purchases
        cursor = conn.cursor(dictionary=True)
        
        # Total revenue over time
        cursor.execute("""
            SELECT p.purchase_date, SUM(pr.price * p.quantity) AS total_revenue
            FROM purchases p
            JOIN products pr ON p.product_id = pr.product_id
            GROUP BY p.purchase_date
        """)
        data = cursor.fetchall()
        if data:
            dates = [row["purchase_date"] for row in data]
            revenue = [row["total_revenue"] for row in data]
            sns.set_style("whitegrid")
            plt.figure(figsize=(10, 5))
            sns.lineplot(x=dates, y=revenue, marker='o')
            plt.xticks(rotation=45)
            plt.title("Total Revenue Over Time")
            plt.xlabel("Purchase Date")
            plt.ylabel("Revenue ($)")
            st.pyplot(plt)
        else:
            st.info("No purchase data to analyze.")
    except Error as e:
        st.error(f"Error fetching analytics: {e}")


# Streamlit App UI
st.set_page_config(
    page_title="Customer, Product & Purchase Dashboard",
    layout="wide",
)

st.title("Customer, Product & Purchase Dashboard")

# Database connection
conn = create_connection()

if conn:
    # Sidebar navigation menu
    menu = st.sidebar.selectbox(
        "Menu",
        [
            "View Customers",
            "Add New Customer",
            "View Products",
            "Add New Product",
            "Record Purchase",
            "Analytics"
        ]
    )

    if menu == "View Customers":
        with st.expander("Customer Search Section", expanded=True):
            view_customers(conn)

    elif menu == "Add New Customer":
        with st.expander("Add New Customer", expanded=True):
            add_new_customer(conn)

    elif menu == "View Products":
        with st.expander("Product Search Section", expanded=True):
            view_products(conn)

    elif menu == "Add New Product":
        with st.expander("Add New Product", expanded=True):
            st.write("### Add Product")
            with st.form(key="new_product_form"):
                name = st.text_input("Product Name")
                price = st.number_input("Price", min_value=0.0, step=0.01)
                stock = st.number_input("Stock", min_value=0, step=1)
                submitted = st.form_submit_button("Add Product")
                if submitted:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
                                       (name, price, stock))
                        conn.commit()
                        st.success("Product added successfully!")
                    except Error as e:
                        st.error(f"Error: {e}")

    elif menu == "Record Purchase":
        with st.expander("Record a new purchase", expanded=True):
            record_purchase(conn)

    elif menu == "Analytics":
        with st.expander("View Analytics", expanded=True):
            show_analytics(conn)

    # Close database connection after finishing navigation
    conn.close()
else:
    st.error("Could not establish database connection.")
