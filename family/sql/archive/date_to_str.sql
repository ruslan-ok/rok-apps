with cte_events as (
	select
		d.id,
		d.date,
		length(d.date) as len,
		case
			when length(d.date) = 10 then substr(d.date, 1, 1)
			when length(d.date) = 11 then substr(d.date, 1, 2)
			else null
		end as day,
		case
			when length(d.date) = 8 and substr(d.date, 1, 3) in ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC') then substr(d.date, 1, 3)
			when length(d.date) = 10 then substr(d.date, 3, 3)
			when length(d.date) = 11 then substr(d.date, 4, 3)
			else null
		end as month,
		case
			when length(d.date) = 4 then substr(d.date, 1, 4)
			when length(d.date) = 5 and substr(d.date, 5, 1) = 'г' then substr(d.date, 1, 4)
			when length(d.date) = 6 and substr(d.date, 5, 2) = 'г.' then substr(d.date, 1, 4)
			when length(d.date) = 7 and substr(d.date, 1, 3) = 'TO ' then substr(d.date, 4, 4)
			when length(d.date) = 8 and substr(d.date, 1, 4) = 'ABT ' then substr(d.date, 5, 4)
			when length(d.date) = 9 and substr(d.date, 1, 5) = 'FROM ' then substr(d.date, 6, 4)
			when length(d.date) = 7 and substr(d.date, 5, 3) = ' ()' then substr(d.date, 1, 4)
			when length(d.date) = 8 and substr(d.date, 1, 3) in ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC') then substr(d.date, 5, 4)
			when length(d.date) = 10 then substr(d.date, 7, 4)
			when length(d.date) = 11 then substr(d.date, 8, 4)
			else null
		end as year
	from family_eventdetail d
)
, cte_transform as (
	select
		d.id,
		d.date,
		d.len,
		case
			when length(d.day) = 2 then d.day
			when length(d.day) = 1 then '0' || d.day
			else null
		end as day,
		case
			when d.month is not null then
				replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(d.month, 
					'JAN', '01'), 'FEB', '02'), 'MAR', '03'), 'APR', '04'), 'MAY', '05'), 'JUN', '06'), 
					'JUL', '07'), 'AUG', '08'), 'SEP', '09'), 'OCT', '10'), 'NOV', '11'), 'DEC', '12')
			else null
		end as month,
		d.year
	from cte_events d
)
, cte_date as (
	select
		d.id,
		d.date,
		case
			when d.year is not null and d.month is not null and d.day is not null then d.year || '-' || d.month || '-' || d.day
			when d.year is not null and d.month is not null then d.year || '-' || d.month
			when d.year is not null then d.year
			else null
		end as sort
	from cte_transform d
)
select * 
from cte_date;
