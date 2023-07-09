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