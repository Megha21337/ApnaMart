import mysql.connector

# Connect to the database
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@#megha",
    database="apna_mart"
)


# Define the query to get the most ordered product in month 1
query1 = """
    SELECT order_items.idproduct, SUM(order_items.quantity) AS total_quantity
    FROM orders
    JOIN order_items ON orders.idOrder = order_items.idOrder
    WHERE MONTH(orders.orderDate) = 1
    GROUP BY order_items.idproduct
    ORDER BY total_quantity DESC
    LIMIT 1
"""

# Execute the query and fetch the results
cursor = cnx.cursor()
cursor.execute(query1)
result1 = cursor.fetchone()

# Define the query to get the most ordered product in month 2
query2 = """
    SELECT order_items.idproduct, SUM(order_items.quantity) AS total_quantity
    FROM orders
    JOIN order_items ON orders.idOrder = order_items.idOrder
    WHERE MONTH(orders.orderDate) = 2
    GROUP BY order_items.idproduct
    ORDER BY total_quantity DESC
    LIMIT 1
"""

# Execute the query and fetch the results
cursor.execute(query2)
result2 = cursor.fetchone()

# Define the query to get the most ordered product in month 3
query3 = """
    SELECT order_items.idproduct, SUM(order_items.quantity) AS total_quantity
    FROM orders
    JOIN order_items ON orders.idorder = order_items.idOrder
    WHERE MONTH(orders.orderDate) = 3
    GROUP BY order_items.idproduct
    ORDER BY total_quantity DESC
    LIMIT 1
"""

# Execute the query and fetch the results
cursor.execute(query3)
result3 = cursor.fetchone()

# Close the cursor and database connection
cursor.close()
cnx.close()

# Print the results
print("Most ordered product in month 1: Product ID = %s, Total Quantity = %s" % result1)
print("Most ordered product in month 2: Product ID = %s, Total Quantity = %s" % result2)
print("Most ordered product in month 3: Product ID = %s, Total Quantity = %s" % result3)
