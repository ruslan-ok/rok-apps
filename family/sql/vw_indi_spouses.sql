--drop view family_vw_indi_spouses;

create view family_vw_indi_spouses as
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
, cte_event_date as (
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
, cte_famevent as (
	select
		e.fam_id as fami_id,
		e.tag,
		e.value,
		e.desc,
		e.husb_age,
		e.wife_age,
		d.type,
		dd.date,
		dd.sort,
		d.agnc,
		d.reli,
		d.caus,
		p.name as plac,
		p.map_lati,
		p.map_long,
		a.addr,
		a.addr_adr1,
		a.addr_adr2,
		a.addr_adr3,
		a.addr_city,
		a.addr_stae,
		a.addr_post,
		a.addr_ctry,
		a.phon,
		a.phon2,
		a.phon3,
		a.email,
		a.email2,
		a.email3,
		a.fax,
		a.fax2,
		a.fax3,
		a.www,
		a.www2,
		a.www3,
		a.owner
	from family_familyeventstructure e
	left join family_eventdetail d
		on e.deta_id = d.id
	left join cte_event_date dd
		on d.id = dd.id
	left join family_placestructure p
		on d.plac_id = p.id
	left join family_addressstructure a
		on d.addr_id = a.id
)
, cte_mml as (
	select
		mml.indi_id,
		mmr.id as mmr_id,
		mmr2.id as mmr2_id,
		row_number() over(partition by mml.indi_id order by mmr._prim nulls last) as rn
	from family_multimedialink mml
	left join family_multimediarecord mmr
		on mml.obje_id = mmr.id
	left join family_multimediarecord mmr2
		on mmr._pari = mmr2._prin
		and mmr._prim = 'Y'
		and mmr.tree_id = mmr2.tree_id
	where mml.indi_id is not null
)
, cte_mmr as (
	select
		l.indi_id,
		coalesce(l.mmr2_id, l.mmr_id) as mmr_id
	from cte_mml l
	where l.rn = 1
)
, cte_husb as (
	select
		ir.tree_id,
		f.wife_id as indi_id,
		ir.id as spou_id,
		pnp.givn,
		pnp.surn,
		pnp._marnm,
		e.*
	from family_individualrecord ir
	left join family_personalnamestructure pns
		on ir.id = pns.indi_id
	left join family_personalnamepieces pnp
		on pns.piec_id = pnp.id
	join family_famrecord f
		on ir.id = f.husb_id
	left join cte_famevent e
		on f.id = e.fami_id
)
, cte_wife as (
	select
		ir.tree_id,
		f.husb_id as indi_id,
		ir.id as spou_id,
		pnp.givn,
		pnp.surn,
		pnp._marnm,
		e.*
	from family_individualrecord ir
	left join family_personalnamestructure pns
		on ir.id = pns.indi_id
	left join family_personalnamepieces pnp
		on pns.piec_id = pnp.id
	join family_famrecord f
		on ir.id = f.wife_id
	left join cte_famevent e
		on f.id = e.fami_id
)
, cte_result as (
	select * from cte_husb
	union all
	select * from cte_wife
)
select 
	row_number() over(order by r.indi_id, r.fami_id, r.sort nulls last) as id,
	min(r.sort) over(partition by r.fami_id order by r.sort nulls last) as spou_sort,
	m.mmr_id as spou_mmr_id,
	r.*
from cte_result r
join cte_mmr m
	on r.indi_id = m.indi_id
where r.indi_id is not null
order by r.indi_id, spou_sort nulls last, r.sort nulls last;
