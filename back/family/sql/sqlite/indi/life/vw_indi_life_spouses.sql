-- uses in family_vw_indi_life_children

--drop view family_vw_indi_life_spouses;

CREATE VIEW family_vw_indi_life_spouses as
with cte_indi_in_fam as (
	select 
		id as fam_id,
		tree_id,
		husb_id as indi_id,
		wife_id as spouse_id,
		'husb' as role
	from family_famrecord
	where husb_id is not null
	union all
	select 
		id as fam_id,
		tree_id,
		wife_id as indi_id,
		husb_id as spouse_id,
		'wife' as role
	from family_famrecord
	where wife_id is not null
)
select
	row_number() over (partition by fam.indi_id order by fam.spouse_id) as id,
	fam.tree_id,
	fam.fam_id,
	fam.role,
	fam.indi_id,
	fam.spouse_id,
	indi.sex as indi_sex, 
	indi.full_name as indi_full_name,
	indi.birth_date as indi_birth_date,
	indi.birth_place as indi_birth_place,
	indi.death_date as indi_death_date, 
	indi.death_place as indi_death_place,
	spouse.sex as spouse_sex, 
	spouse.full_name as spouse_full_name,
	spouse.birth_date as spouse_birth_date,
	spouse.birth_place as spouse_birth_place,
	spouse.death_date as spouse_death_date, 
	spouse.death_place as spouse_death_place
from cte_indi_in_fam as fam
join family_vw_indi_life as indi
	on fam.indi_id = indi.id
left join family_vw_indi_life as spouse
	on fam.spouse_id = spouse.id