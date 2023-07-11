import mysql.connector
import datetime
import random
conn=mysql.connector.connect(host='localhost',user='root',password='1220',database='apna_mart')

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

def adminFunctions():
    print("-----Welcome Admin-----")
    print("Press 1 for Embedded queries")
    print("Press 2 for Triggers")
    print("Press 3 for OLAP queries")
    print("Press anything else to EXIT")
    n=int(input("Choose: "))
    if(n==1 or n==2 or n==3 ):
        if n==1:
            EMBEDED_QUERIES()
        elif n==2:
            TRIGGER()
        elif n==3:
            OLAP_QUERIES()

def add2Cart(idCustomer,idProduct,q):
    cursor=conn.cursor()
    cursor.execute(f"SELECT * FROM carts WHERE idCustomer={idCustomer} AND idProduct={idProduct}")
    result = cursor.fetchone()
    if result:
        # If the product is already in the cart, update its quantity
        new_quantity = result[2] + q
        cursor.execute(f"UPDATE carts SET quantity={new_quantity} WHERE idCustomer={idCustomer} AND idProduct={idProduct}")
        print(f"\nQuantity updated in cart.\n")
    else:
        # If the product is not in the cart, add it to the cart
        cursor.execute(f"INSERT INTO carts (idCustomer, idProduct, quantity) VALUES ({idCustomer},{idProduct},{q})")
        print(f"\n Product added to cart.\n")

def browseProducts(idCustomer):
    cur=conn.cursor()
    cur.execute("Select idCategory,nameCategory from categories")
    categoryList=cur.fetchall()
    for i in categoryList:
        print(str(i[0])+"  "+str(i[1]))
    category=int(input("Choose a category: "))
    if category in range(1,11):
        cur.execute(f"Select idProduct, nameProduct, price from Products where idCategory={category}")
        productList=cur.fetchall()
        for i in productList:
            print(str(i[0])+"  "+str(i[1])+ " @ "+ str(i[2]))
    else:
        print('Wrong Category ID')
        c=input("Press 1 to retry or anything else to exit: ")
        if c==1: browseProducts()
    product=int(input("Choose a Product: "))
    cur.execute(f"Select Min(idProduct),Max(idProduct) from Products where idCategory={category}")
    pidrange=cur.fetchone()
    cur.execute("Show columns from Products")
    fields=cur.fetchall()
    if product in range(pidrange[0],pidrange[1]+1):
        cur.execute(f"Select * from Products where idProduct={product}")
        productDetails=cur.fetchone()
        for i in range(len(productDetails)):
            print(fields[i][0]+": "+str(productDetails[i]))
    else:
        print('Wrong Product ID')
        c=input("Press 1 to retry or anything else to exit: ")
        if c=='1': browseProducts()
    if idCustomer==None:
        c=input("Press 1 to browse more products or anything else to exit: ")
        if c=="1": browseProducts()
    else:
        c=input("1. Add To Cart\n2. Browse more Products\nor anything else to exit")
        if c=="1":
            q=int(input("Enter Quantity to add to Cart: "))
            if not q.isdigit() or q <= 0:
                print("Invalid quantity")
            else: add2Cart(idCustomer,product,q)
        elif c=="2": browseProducts()

def viewOrders(idCustomer):
    cur=conn.cursor()
    cur.execute(f"Select idOrder,totalAmount,orderDate,deliveryDate,idVoucher from Orders where idCustomer={idCustomer}")
    orders=cur.fetchall()
    cur.execute("Show columns from Orders")
    fields=cur.fetchall()
    del fields[1]
    for i in range(len(orders)):
        for j in range(len(orders[i])):
            print(fields[j][0]+": "+str(orders[i][j]))
        print()
    c=input("Enter Order ID to manage that order or press Enter to exit: ")
    if c=="\n" or c==None or c=="":
        return
    else:
        order_list=[]
        for i in orders:
            order_list.append(str(i[0]))
        if c in order_list:
            print(f"Sorry, It is not possible to Manage Order {c} as of now")
        else:
            print("Wrong Order ID Selected")

def viewVouchers(idCustomer):
    cur=conn.cursor()
    cur.execute(f"Select v.idVoucher,idProduct,discount,expiry_date, dateUsed,idOrder from Vouchers v join voucher_statuses on v.idVoucher=voucher_statuses.idVoucher where idCustomer={idCustomer} ")
    vouchers=cur.fetchall()
    fields=['Voucher ID', 'Product ID', "Discount %", "Expiry Date", "Date Used, if used", "Order ID, if used"]
    for i in range(len(vouchers)):
        for j in range(len(vouchers[i])):
            print(fields[j]+": "+str(vouchers[i][j]))
        print()

def checkout(idCustomer):
    cur=conn.cursor()
    cur.execute(f"SELECT c.quantity,p.price,p.idProduct FROM apna_mart.carts c join apna_mart.products p on c.idProduct=p.idProduct where idCustomer={idCustomer}")
    cart=cur.fetchall()
    total_amount=0
    # Fetch the last order ID from the database
    cur.execute("SELECT MAX(idOrder) FROM orders")
    lastidOrder = cur.fetchone()
    newidOrder=lastidOrder[0]+1 if lastidOrder!=[None] else 1
    for i in cart:
        #Calculate total Amount of Current Cart
        total_amount+=i[0]*i[1]
        #Check if there is enough stock
        cur.execute(f"SELECT quantityAvailable FROM products WHERE idProduct = {i[2]} FOR UPDATE;")
        stock=cur.fetchone()[0]
        if stock>=i[0]:
            # Update the product quantities in the database
            cur.execute(f"Update products set quantityAvailable=quantityAvailable-{i[0]} where idProduct={i[2]}")
        else:
            print(f"Not enough quantity available for product ID {i[2]}")
            conn.rollback
            return
        cur.execute(f"Delete from carts where idProduct={i[2]} AND idCustomer={idCustomer}")
    current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    delivery_date=(datetime.datetime.now()+datetime.timedelta(days=random.randint(2,6))).strftime("%Y-%m-%d")
    idVoucher=0
    # Add the current order to the database
    # cur.execute(f"INSERT INTO orders (idOrder,idCustomer, totalAmount, orderDate, deliveryDate,idVoucher) VALUES ({newidOrder},{idCustomer}, {total_amount}, {current_time}, {delivery_date},NULL)")
    query = "INSERT INTO orders (idOrder, idCustomer, totalAmount, orderDate, deliveryDate, idVoucher) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (newidOrder, idCustomer, total_amount, current_time, delivery_date, None)
    cur.execute(query, values)

    for i in cart:
        # Add the  order items to the database
        cur.execute(f"INSERT INTO order_items (idOrder,idProduct, quantity, unitPrice) VALUES ({newidOrder},{i[2]}, {i[0]}, {i[1]})")
    # Check if the customer has enough balance in their wallet
    cur.execute(f"SELECT wallet FROM customers WHERE idCustomer={idCustomer}")
    wallet = cur.fetchone()[0]
    if total_amount > wallet:
        print("Insufficient balance in Wallet! Payment failed")
        conn.rollback()
        return
    # Deduct the amount from the customer's wallet
    cur.execute(f"UPDATE customers SET wallet={wallet-total_amount} WHERE idCustomer={idCustomer}")
    current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Add the payment to the database
    query = "INSERT INTO payments (idOrder, datePayment) VALUES (%s, %s)"
    values = (newidOrder, current_time)
    cur.execute(query, values)
    # Add the order status to the database
    query = "INSERT INTO order_statuses (idOrder, shipped, outForDelivery, delivered) VALUES (%s, %s, %s, %s)"
    values = (newidOrder, 0, 0, 0)
    cur.execute(query, values)
    # Commit the changes to the database
    conn.commit()
    print("Payment successful! Order is Placed, Go to My Orders to Track")

def viewCart(idCustomer):
    cur=conn.cursor()
    cur.execute(f"Select c.idProduct,p.nameProduct,quantity,p.price from carts c join products p on c.idProduct=p.idProduct where idCustomer={idCustomer}")
    products=cur.fetchall()
    fields=['Product ID', 'Name','Quantity','Price per 1']
    for i in range(len(products)):
        for j in range(len(products[i])):
            print(fields[j]+": "+str(products[i][j]))
        print()
    productIDs = [i[0] for i in products]
    c=input("Enter 0 to Checkout,or Enter Product ID to manage Product in Cart, or Press Enter to Exit: ")
    if c=="0":
        checkout(idCustomer)
    elif int(c) in productIDs:
        print("Sorry its not possible to edit your Cart as of now")
    else:
        return

def userFunctions(id):
    while True:
        cur=conn.cursor()
        cur.execute(f"Select first_name,last_name from Customers where idCustomer={id}")
        name=cur.fetchall()
        print(f"-----Welcome {name[0][0]} {name[0][1]}, Choose to proceed-----")
        print("1. Explore Products")
        print("2. Manage/View Orders")
        print("3. View Vouchers")
        print("4. Manage/View Cart")
        print("5. Add Money to Wallet")
        print("6. Logout")
        c = int(input("Enter your choice: "))
        if c == 1:
            browseProducts(id)
        elif c == 2:
            viewOrders(id)
        elif c == 3:
            viewVouchers(id)
        elif c == 4:
            viewCart(id)
        elif c==5:
            inc=int(input("Enter Amount to add in Rs: "))
            cur.execute( f"Update customers set wallet = wallet+{inc} where idCustomer={id}")
            conn.commit()
            print(f"Added Rs{id} successfully!")
        elif c==6:
            return
        else:
            print("Invalid choice Please try again.")
            userFunctions(id)

def adminLogin():
    id = int(input("Enter User id: "))
    password = input("Enter password: ")
    cur= conn.cursor()
    cur.execute("Select * from admins")
    admin_list=cur.fetchall()
    for i in admin_list:
        if i[0]==id and i[1]==password:
            adminFunctions()
            return
    print("Given id and password doesn't match, Try Again or Exit")
    c=input("Press 1 to try again or anything else to exit: ")
    if c=="1":
        adminLogin()

def userLogin():
    id = int(input("Enter User id: "))
    password = input("Enter password: ")
    cur= conn.cursor()
    cur.execute("Select idCustomer,password from customers")
    customer_list=cur.fetchall()
    for i in customer_list:
        if i[0]==id and i[1]==password:
            userFunctions(id)
            return
    print("Given id and password doesn't match, Try Again or exit to Signup as new Customer")
    c=input("Press 1 to try again or anything else to exit: ")
    if c=="1":
        userLogin()

def userSignup():
    print("-----Welcome, Please register as new Customer!-----")

if conn.is_connected():
    # cur=conn.cursor()
    # newidOrder=198
    # idCustomer=20
    # total_amount=100
    # current_time="2023-04-25 12:04:21"
    # delivery_date="2023-05-01"
    # query = "INSERT INTO orders (idOrder, idCustomer, totalAmount, orderDate, deliveryDate, idVoucher) VALUES (%s, %s, %s, %s, %s, %s)"
    # values = (newidOrder, idCustomer, total_amount, current_time, delivery_date, None)
    # cur.execute(query, values)
    viewCart(20)
    # while True:
    #     print("-----Welcome to APNA MART-----")
    #     print("1. Login as Admin")
    #     print("2. Explore Products")
    #     print("3. Login as User")
    #     print("4. Sign Up as New User")
    #     print("5. Exit")
    #     c=int(input("Choose: "))
    #     if c==1:
    #         adminLogin()
    #     elif c==2:
    #         browseProducts(None)
    #     elif c==3:
    #         userLogin()
    #     elif c==4:
    #         userSignup()
    #     elif c==5:
    #         conn.close()
    #         break
    #     else:
    #         print("-----Wrong choice, Please choose again-----")
else:
    print("Error Connecting to Server, Exiting")

