--drop view family_vw_indi_life_children;

CREATE VIEW family_vw_indi_life_children as
select
	row_number() over (partition by fam.indi_id order by fam.fam_id, indi.id) as id,
	fam.tree_id,
	fam.fam_id,
	fam.indi_id,
	fam.spouse_id,
	fam.spouse_sex,
	fam.spouse_full_name,
	indi.id as child_id, 
	indi.sex as child_sex, 
	indi.full_name as child_full_name,
	indi.birth_date as child_birth_date,
	indi.death_date as child_death_date
from family_vw_indi_life_spouses fam
join family_childtofamilylink ctf
	on fam.fam_id = ctf.fami_id
join family_vw_indi_life indi
	on ctf.chil_id = indi.id