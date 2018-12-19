SELECT 
	* 
FROM 
	records
GROUP BY 
	tab, function, keyword 
HAVING
	count(tab) > 1
ORDER BY 
	tab, function, keyword
;