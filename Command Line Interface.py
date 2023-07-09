import mysql.connector

conn=mysql.connector.connect(host='localhost',user='root',password='@#megha',database='apna_mart')
if conn.is_connected():
     print("connection established......")
     print("Connection id : ",conn.connection_id)
     
def EMBEDED_QUERIES():
    print("1st embedded query")
    from datetime import date, timedelta

    # Date range for the past month
    today = date.today()
    one_month_ago = today - timedelta(days=30)

    cursor1 = conn.cursor()
    query1 = "SELECT first_name, last_name, phno, street_address, area_address, zip_address FROM Customers WHERE idCustomer IN (SELECT idCustomer FROM orders WHERE orderDate >= %s)"
    cursor1.execute(query1, (one_month_ago,))
    results = cursor1.fetchall()

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


    print("2nd embedded query")

    #Max sold product in last 3 months

    # most ordered product in month 1
    query2 = """
        SELECT order_items.idproduct, SUM(order_items.quantity) AS total_quantity
        FROM orders
        JOIN order_items ON orders.idOrder = order_items.idOrder
        WHERE MONTH(orders.orderDate) = 1
        GROUP BY order_items.idproduct
        ORDER BY total_quantity DESC
        LIMIT 1
    """
    cursor2 = conn.cursor()
    cursor2.execute(query2)
    result1 = cursor2.fetchone()

    # most ordered product in month 2
    query3 = """
        SELECT order_items.idproduct, SUM(order_items.quantity) AS total_quantity
        FROM orders
        JOIN order_items ON orders.idOrder = order_items.idOrder
        WHERE MONTH(orders.orderDate) = 2
        GROUP BY order_items.idproduct
        ORDER BY total_quantity DESC
        LIMIT 1
    """

    cursor2.execute(query3)
    result2 = cursor2.fetchone()

    #most ordered product in month 3
    query4 = """
        SELECT order_items.idproduct, SUM(order_items.quantity) AS total_quantity
        FROM orders
        JOIN order_items ON orders.idorder = order_items.idOrder
        WHERE MONTH(orders.orderDate) = 3
        GROUP BY order_items.idproduct
        ORDER BY total_quantity DESC
        LIMIT 1
    """

    cursor2.execute(query4)
    result3 = cursor2.fetchone()

    # Close the cursor and database connection
    cursor1.close()
    cursor2.close()
   

    # Print the results
    print("Most ordered product in month 1: Product ID = %s, Total Quantity = %s" % result1)
    print("Most ordered product in month 2: Product ID = %s , Total Quantity = %s" % result2)
    print("Most ordered product in month 3: Product ID = %s , Total Quantity = %s" % result3)

def TRIGGER():
    cursor1 = conn.cursor()
    trigger1 = """
    CREATE TRIGGER reduce_product_quantity
    AFTER INSERT ON Order_Items
    FOR EACH ROW
    BEGIN
        -- Update the quantity of the product in the Products table
        UPDATE Products
        SET quantityAvailable = CASE 
                                    WHEN quantityAvailable >= NEW.quantity THEN quantityAvailable - NEW.quantity 
                                    ELSE 0 
                                END
        WHERE idProduct = NEW.idProduct;

        -- Check if the quantity available is less than or equal to 0
        IF (SELECT quantityAvailable FROM Products WHERE idProduct = NEW.idProduct) = 0 THEN
            -- Insert a notification in the Notification table
            INSERT INTO Notification (idAdmin, idProduct, idOrder, idVoucher, Message)
            VALUES (1, NEW.idProduct, NEW.idOrder, NULL, 'Product is out of stock');
        END IF;
    END
    """

    trigger2 = """
    CREATE TRIGGER `order_placed_notification` AFTER INSERT ON `Orders`
    FOR EACH ROW
    BEGIN
    DECLARE wallet_amount DECIMAL(10, 2);
    SELECT wallet INTO wallet_amount FROM customers WHERE idCustomer = NEW.idCustomer;

    IF NEW.totalAmount > wallet_amount THEN
        INSERT INTO Notifications (idAdmin,idCustomer, Message) VALUES (1,NEW.idCustomer, 'Less amount in wallet');
    ELSE
        INSERT INTO Notifications (idAdmin,idCustomer,idOrder, Message) VALUES (1,NEW.idCustomer,New.idOrder, 'Order placed');
    END IF;
    END
    """

    # Execute the triggers
    cursor1.execute(trigger1)
    print(' Trigger To update product table when new order is placed')
    cursor1.execute(trigger2)
    print('Trigger to To send notifications to customers and admins')
    # Commit the changes
    conn.commit()

    # Close the cursor and database connection
    cursor1.close()
   



      

def OLAP_QUERIES():
    # Query 1: Show sales of each category, product pair ordered after 1 feb, 2023
    cursor1 = conn.cursor()
    q1 = """
    Select 
    IFNULL(c.nameCategory, 'Overall Total of all Categories') as Category,
    IFNULL(p.nameProduct, 'Overall Total of Category') as Product,
    sum(oi.unitPrice*oi.quantity) as Sum
    from categories c join products p
        using (idCategory)
    join Order_Items oi
        using (idProduct)
    join Orders o
        using (idOrder)
    where orderDate>"2023-02-01"
    group by nameCategory,nameProduct with rollup
    """
    cursor1.execute(q1)
    result1 = cursor1.fetchall()
    print('Sales of each category, product pair ordered after 1 feb, 2023:')
    for answer in result1:
        print(answer)

    # Query 2: Show discount amount for each order and product pair
    cursor2 = conn.cursor()
    q2 = """
        SELECT
    IFNULL(vs.idOrder, 'Total Disocunt of all Orders') as 'Order ID', 
    IFNULL(v.idProduct, 'Total Discount of Order') as 'Product ID',
    sum((unitPrice*(discount/100))) as 'Discount Amount'
    from vouchers v
    join voucher_statuses vs
        using(idVoucher)
    join order_items oi
        using (idOrder)
    where idOrder is not null
    group by vs.idOrder, v.idProduct
    with rollup

    """
    cursor2.execute(q2)
    result2 = cursor2.fetchall()
    print('\nDiscount amount for each order and product pair:')
    for answer in result2:
        print(answer)

    # Commit the changes
    conn.commit()

    # Close the cursor and database connection
    cursor1.close()
    cursor2.close()

    cursor3 = conn.cursor()
    q3 = """
       select 
    concat(s.first_nameSupplier,' ',s.last_nameSupplier) as Supplier_name,
    IF(GROUPING(c.nameCategory), 'Total_products_by_supplier', c.nameCategory) AS namecategory,
    count(ih.idProduct) as count_of_product_in_that_category from
    suppliers s
    join inventory_history ih
    using (idSupplier)
    join products p 
    using (idProduct)
    join categories c
    using (idCategory)
    group by supplier_name, nameCategory with rollup
    """
    cursor3.execute(q3)
    result3 = cursor3.fetchall()
    print('\nCustomer category wise spending:')
    for answer  in result3:
     print(answer)

    cursor4 = conn.cursor()
    q4 = """
       Select idCustomer, nameCategory,Total_Spendings from
    (Select 
    IF(GROUPING(c.idCustomer), 'Total Spendings by all Customers', c.idCustomer) as idCustomer,
    IF(GROUPING(ca.nameCategory), 'Total Spendings by Customer in all Categories', ca.nameCategory) AS nameCategory, 
    sum(oi.unitPrice*oi.quantity) as Total_Spendings
    from customers c 
    join orders o using (idCustomer)
    join order_items oi using (idOrder)
    join products p using (idProduct)
    join categories ca using (idCategory)
    group by c.idCustomer,nameCategory with rollup) as t1
    """
    cursor4.execute(q4)
    result4 = cursor3.fetchall()
    print('\nCategory wise product supplied by supplier:')
    for answer  in result4:
     print(answer)
     
print("-----------Welcome to APNAMART-----------\n")
def choose():
    print("Press 1 for Embedded queries")
    print("Press 2 for Triggers")
    print("Press 3 for OLAP queries")
    print("Press 4 to EXIT")

    n=int(input("Choose: "))
    if(n==1 or n==2 or n==3 ):
          fun(n)
    else:
        print("Program finished")
              
def fun(n):
    if n==1:
        EMBEDED_QUERIES()
        choose()
    elif n==2:
        TRIGGER()
        choose()
    elif n==3:
        OLAP_QUERIES()
        choose()
choose()
        
        

                                

