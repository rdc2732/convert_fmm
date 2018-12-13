update dependencies set record_id = 31
where record_id in 
(
select id from records
where 	(tab, function, keyword) = 
	(
		select tab, function, keyword from records 
		where id = 31
	)
);