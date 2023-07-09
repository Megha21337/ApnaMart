DELIMITER $$
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
END$$
DELIMITER ;

INSERT INTO Orders(idOrder, idCustomer, totalAmount, orderDate, deliveryDate, idVoucher)
VALUES
(104,7,500,'2023-03-30','2023-04-05',NULL),
(105,5,500,'2023-03-28','2023-04-02',NULL),
(106,9,1500,'2023-03-28','2023-04-02',NULL);


