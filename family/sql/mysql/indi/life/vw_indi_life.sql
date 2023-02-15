CREATE OR REPLACE VIEW family_vw_indi_life as
select
	i.id, 
	i.sex, 
	p.givn,
	p.surn,
	concat(concat(coalesce(p.givn, ''), case when coalesce(p.givn, '') != '' and coalesce(p.surn, '') != '' then ' ' else '' end), coalesce(p.surn, '')) as full_name,
	event_birth.date as birth_date,
	birth_place.name as birth_place,
	birth_place.map_lati as birth_place_lati,
	birth_place.map_long as birth_place_long,
	event_death.date as death_date, 
	death_place.name as death_place,
	death_place.map_lati as death_place_lati,
	death_place.map_long as death_place_long
from family_individualrecord i
join family_personalnamestructure n
	on n.indi_id = i.id
join family_personalnamepieces p
	on n.piec_id = p.id
left join family_individualeventstructure birth
	on birth.indi_id = i.id
	and birth.tag = 'BIRT'
left join family_individualeventstructure death
	on death.indi_id = i.id
	and death.tag = 'DEAT'
left join family_eventdetail event_birth
	on birth.deta_id = event_birth.id
left join family_placestructure birth_place
	on event_birth.plac_id = birth_place.id
left join family_eventdetail event_death
	on death.deta_id = event_death.id
left join family_placestructure death_place
	on event_death.plac_id = death_place.id