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
-- having nameCategory='Total Spendings by Customer in all Categories'
-- order by Total_Spendings desc
-- limit 21