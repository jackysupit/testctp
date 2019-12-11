SELECT min("purchase_report".id) AS id,
 count("purchase_report".id) AS "__count" ,
 sum("purchase_report"."price_total") AS "price_total",
sum("purchase_report"."unit_quantity") AS "unit_quantity",
avg("purchase_report"."price_average") AS "price_average",
"purchase_report"."name" as "name" ,
"purchase_report"."partner_id" as "partner_id" 
FROM "purchase_report" 
LEFT JOIN "res_partner" as "purchase_report__partner_id" ON ("purchase_report"."partner_id" = "purchase_report__partner_id"."id")
WHERE ((("purchase_report"."date_order" >= \'2019-04-30 17:00:00\')  AND  ("purchase_report"."date_order" < \'2019-05-31 17:00:00\'))  AND  (("purchase_report"."state" != \'draft\')  AND  ("purchase_report"."state" != \'cancel\'))) AND ("purchase_report"."company_id" IS NULL   OR  ("purchase_report"."company_id" in (1,
2,
3,
4,
5)))
GROUP BY "purchase_report"."name",
"purchase_report"."partner_id",
"purchase_report__partner_id"."display_name"
ORDER BY "name",
 "purchase_report__partner_id"."display_name"  


