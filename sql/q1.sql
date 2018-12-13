SELECT 
	* 
FROM 
	records, dependencies 
WHERE 
	dependencies.record_id = records.id and 
	keyword = 'odsDualChannel'
;