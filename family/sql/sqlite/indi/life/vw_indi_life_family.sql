-- drop view family_vw_indi_life_family

CREATE VIEW family_vw_indi_life_family as
select 
	i.id as indi_id,
	i.sex as indi_sex,
	i.full_name as indi_full_name,
	i.birth_date as indi_birth_date,
	i.birth_place as indi_birth_place,
	i.birth_place_lati as indi_birth_place_lati,
	i.birth_place_long as indi_birth_place_long,
	i.death_date as indi_death_date,
	i.death_place as indi_death_place,
	i.death_place_lati as indi_death_place_lati,
	i.death_place_long as indi_death_place_long,
	fam.id as fam_id,
	father.id as father_id,
	father.sex as father_sex,
	father.full_name as father_full_name,
	father.birth_date as father_birth_date,
	father.birth_place as father_birth_place,
	father.birth_place_lati as father_birth_place_lati,
	father.birth_place_long as father_birth_place_long,
	father.death_date as father_death_date,
	father.death_place as father_death_place,
	father.death_place_lati as father_death_place_lati,
	father.death_place_long as father_death_place_long,
	mother.id as mother_id,
	mother.sex as mother_sex,
	mother.full_name as mother_full_name,
	mother.birth_date as mother_birth_date,
	mother.birth_place as mother_birth_place,
	mother.birth_place_lati as mother_birth_place_lati,
	mother.birth_place_long as mother_birth_place_long,
	mother.death_date as mother_death_date,
	mother.death_place as mother_death_place,
	mother.death_place_lati as mother_death_place_lati,
	mother.death_place_long as mother_death_place_long
from family_vw_indi_life i
left join family_childtofamilylink ctf
	on ctf.chil_id = i.id
left join family_famrecord fam
	on ctf.fami_id = fam.id
left join family_vw_indi_life father
	on fam.husb_id = father.id
left join family_vw_indi_life mother
	on fam.wife_id = mother.id