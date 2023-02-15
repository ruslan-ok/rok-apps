--drop view family_vw_indi_life_events;

CREATE VIEW family_vw_indi_life_events as 
select
	row_number() over (partition by ies.indi_id order by ies._sort) as id,
	ies.indi_id,
	ies._sort,
	ies.tag,
	ed.type,
	ies.value,
	ed.date,
	ed.caus,
	plac.name as plac,
	addr.addr
from family_individualeventstructure ies
join family_eventdetail ed
	on ies.deta_id = ed.id
left join family_addressstructure addr
	on ed.addr_id = addr.id
left join family_placestructure plac
	on ed.plac_id = plac.id