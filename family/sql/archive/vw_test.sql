--CREATE VIEW family_vw_indi_life_events as 
with cte_families as (
	select
		indi_id as indi_id,
		'indi' as role,
		indi_id as role_id
	from family_vw_indi_life_family
	union all
	select
		indi_id as indi_id,
		'father' as role,
		father_id as role_id
	from family_vw_indi_life_family
	where father_id is not null
	union all
	select
		indi_id as indi_id,
		'mother' as role,
		mother_id as role_id
	from family_vw_indi_life_family
	where mother_id is not null
	union all
	select
		indi_id as indi_id,
		'spouse' as role,
		spouse_id as role_id
	from family_vw_indi_life_spouses
	union all
	select
		indi_id as indi_id,
		'child' as role,
		child_id as role_id
	from family_vw_indi_life_children
)
--select * from cte_families where indi_id = 5073;
, cte_events as (
	select
		row_number() over (order by ies.indi_id, ies._sort, ies.tag, ed.date) as id,
		indi.tree_id,
		f.indi_id,
		f.role,
		f.role_id,
		--ies.indi_id,
		ies._sort,
		ies.tag,
		case 
			when ies.tag = 'BIRT' then 'Birth'
			when ies.tag = 'DEAT' then 'Death'
			when ies.tag = 'BURI' then 'Burial'
			when ies.tag = 'CHR' then 'Christening'
			else ed.type 
		end as type_name,
		ies.value,
		ed.date,
		case when substr(ed.date, 1, 4) = 'ABT ' then 1 else 0 end as is_abt,
		replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(
			case when ed.date = '199' then null else ed.date end, 'г.', ''), 
			'ABT ', ''),
			'января', 'JAN '),
			'февраля', ' FEB '),
			'jапреля', 'APR'),
			'апреля', ' APR '),
			'Май', ' MAY'),
			'июня', ' JUN'),
			'Июль', ' JUL'),
			'августа', 'AUG'), 
			'сентября', ' SEP '),
			'г', ''),
			'  ', ' ')
		as clear_date,
		ed.caus,
		plac.name as plac,
		addr.addr
	from cte_families f
	join family_individualeventstructure ies
		on f.role_id = ies.indi_id
	join family_individualrecord indi
		on ies.indi_id = indi.id
	join family_eventdetail ed
		on ies.deta_id = ed.id
	left join family_addressstructure addr
		on ed.addr_id = addr.id
	left join family_placestructure plac
		on ed.plac_id = plac.id
)
--select * from cte_events where id in (566, 561, 549);
, cte_event_date as (
	select
		d.*,
		length(d.clear_date) as len,
		case
			when length(d.clear_date) = 10 and substr(d.clear_date, 3, 3) in ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC') then '0' || substr(d.clear_date, 1, 1)
			when length(d.clear_date) = 11 and substr(d.clear_date, 4, 3) in ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC') then substr(d.clear_date, 1, 2)
			when length(d.clear_date) = 10 and substr(d.clear_date, 3, 2) = ' 0' then substr(d.clear_date, 1, 2)
			else null
		end as day,
		case
			when length(d.clear_date) = 8 and substr(d.clear_date, 1, 3) in ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC') then substr(d.clear_date, 1, 3)
			when length(d.clear_date) = 10 then substr(d.clear_date, 3, 3)
			when length(d.clear_date) = 11 then substr(d.clear_date, 4, 3)
			else null
		end as month,
		case
			when length(d.clear_date) = 4 then substr(d.clear_date, 1, 4)
			when length(d.clear_date) = 5 and substr(d.clear_date, 5, 1) = 'г' then substr(d.clear_date, 1, 4)
			when length(d.clear_date) = 6 and substr(d.clear_date, 5, 2) = 'г.' then substr(d.clear_date, 1, 4)
			when length(d.clear_date) = 7 and substr(d.clear_date, 1, 3) = 'TO ' then substr(d.clear_date, 4, 4)
			when length(d.clear_date) = 8 and substr(d.clear_date, 1, 4) = 'ABT ' then substr(d.clear_date, 5, 4)
			when length(d.clear_date) = 9 and substr(d.clear_date, 1, 5) = 'FROM ' then substr(d.clear_date, 6, 4)
			when length(d.clear_date) = 7 and substr(d.clear_date, 5, 3) = ' ()' then substr(d.clear_date, 1, 4)
			when length(d.clear_date) = 8 and substr(d.clear_date, 1, 3) in ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC') then substr(d.clear_date, 5, 4)
			when length(d.clear_date) = 10 then substr(d.clear_date, 7, 4)
			when length(d.clear_date) = 11 then substr(d.clear_date, 8, 4)
			else null
		end as year
	from cte_events d
	where clear_date is not null
)
--select * from cte_event_date where id in (39, 85) order by year, month, day;
--select max(id), month from cte_event_date group by month order by month desc;
, cte_month_num as (
	select 
		d.*,
		case 
			when d.month = 'JAN' then '01'
			when d.month = 'FEB' then '02'
			when d.month = 'MAR' then '03'
			when d.month = 'APR' then '04'
			when d.month = 'MAY' then '05'
			when d.month = 'JUN' then '06'
			when d.month = 'JUL' then '07'
			when d.month = 'AUG' then '08'
			when d.month = 'SEP' then '09'
			when d.month = 'OCT' then '10'
			when d.month = 'NOV' then '11'
			when d.month = 'DEC' then '12'
			else trim(d.month)
		end as month_num
	from cte_event_date d
)
--select * from cte_month_num;
, cte_full_date as (
	select 
		d.*,
		d.year || 
			case when d.month_num is not null then '-' || d.month_num else '' end || 
			case when d.month_num is not null  and d.day is not null then '-' || d.day else '' end 
		as full_date
	from cte_month_num d
)
--select * from cte_full_date;
select *
from cte_full_date
where indi_id = 5073
--where type_name is null
--where coalesce(value, '') != ''
--where caus is not null
order by full_date;
