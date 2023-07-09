--  Show total amount of discount claimed by all customers using Vouchers for every Order,Product pair done using Vouchers

select 
IF(GROUPING(vs.idOrder),'Total Disocunt of all Orders',vs.idOrder) AS 'Order ID',
-- IFNULL(vs.idOrder, 'Total Disocunt of all Orders') as 'Order ID', 
IF(GROUPING(v.idProduct),'Total Discount on Order',v.idProduct) AS 'Product ID',
-- IFNULL(v.idProduct, 'Total Discount of Order') as 'Product ID',
sum((unitPrice*(discount/100))) as 'Discount Amount'
from vouchers v
join voucher_statuses vs
	using(idVoucher)
join order_items oi
	using (idOrder)
where idOrder is not null
group by vs.idOrder, v.idProduct
with rollup

