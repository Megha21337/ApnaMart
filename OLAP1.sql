-- Show sales of each category, product pair ordered after 1 feb, 2023

select
IF(GROUPING(c.nameCategory),'Overall Total of all Categories',c.nameCategory) AS Category,
-- IFNULL(c.nameCategory, 'Overall Total of all Categories') as Category,
IF(GROUPING(p.nameProduct),'Overall Total of Category',p.nameProduct) AS Product,
-- IFNULL(p.nameProduct, 'Overall Total of Category') as Product,
sum(oi.unitPrice*oi.quantity) as Sum
from categories c join products p
	using (idCategory)
join Order_Items oi
	using (idProduct)
join Orders o
	using (idOrder)
where orderDate>"2023-02-01"
group by nameCategory,nameProduct with rollup

