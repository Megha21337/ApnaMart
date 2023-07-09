DELIMITER $$
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
END$$
DELIMITER ;


INSERT INTO Order_Items(idOrder, idProduct, quantity, unitPrice)
VALUES
(102,1,5,500),
(103,19,4,2500);