import mysql.connector
from datetime import date, timedelta

# Connect to the database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@#megha",
    database="apna_mart"
)

# Calculate the date range for the past month
today = date.today()
one_month_ago = today - timedelta(days=30)

#Embedded SQL query
cursor = conn.cursor()
query = "SELECT first_name, last_name, phno, street_address, area_address, zip_address FROM Customers WHERE idCustomer IN (SELECT idCustomer FROM orders WHERE orderDate >= %s)"
cursor.execute(query, (one_month_ago,))
results = cursor.fetchall()

# A dictionary created. Key=zipcode first 2 numbers / Values=users data belonging to same places.
zip_code_groups = {}
for row in results:
    zip_code = row[5]
    zip_code_group = zip_code[:2]
    if zip_code_group not in zip_code_groups:
        zip_code_groups[zip_code_group] = []
    zip_code_groups[zip_code_group].append(row)

# Print the results for each group
for zip_code_group, group_results in zip_code_groups.items():
    print(f"Zip Code: {zip_code_group}")
    for row in group_results:
        print(row)
    print("\n")

conn.close()
