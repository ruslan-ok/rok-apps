--drop view family_vw_indi_families;

create view family_vw_indi_families as 
with cte_family as (
	select
		row_number() over() as id,
		ir.tree_id,
		c.chil_id,
		f.id as fami_id,
		f.husb_id,
		h_pnp.givn as husb_givn,
		h_pnp.surn as husb_surn,
		f.wife_id,
		w_pnp.givn as wife_givn,
		w_pnp.surn as wife_surn,
		lower(coalesce(c.pedi, 'birth')) as pedi
	from family_childtofamilylink c
	join family_individualrecord ir
		on c.chil_id = ir.id
	join family_famrecord f
		on c.fami_id = f.id
	left join family_individualrecord h
		on f.husb_id = h.id
	left join family_personalnamestructure h_pns
		on h.id = h_pns.indi_id
	left join family_personalnamepieces h_pnp
		on h_pns.piec_id = h_pnp.id
	left join family_individualrecord w
		on f.wife_id = w.id
	left join family_personalnamestructure w_pns
		on w.id = w_pns.indi_id
	left join family_personalnamepieces w_pnp
		on w_pns.piec_id = w_pnp.id
)
, cte_husb as (
	select
		f.fami_id,
		f.husb_id,
		mmr.id as mmr_id,
		mmr2.id as mmr2_id,
		row_number() over(partition by f.fami_id order by mmr._prim nulls last) as rn
	from cte_family f
	left join family_multimedialink mml
		on f.husb_id = mml.indi_id
	left join family_multimediarecord mmr
		on mml.obje_id = mmr.id
	left join family_multimediarecord mmr2
		on mmr._pari = mmr2._prin
		and mmr._prim = 'Y'
		and mmr.tree_id = mmr2.tree_id
)
, cte_wife as (
	select
		f.fami_id,
		f.wife_id,
		mmr.id as mmr_id,
		mmr2.id as mmr2_id,
		row_number() over(partition by f.fami_id order by mmr._prim nulls last) as rn
	from cte_family f
	left join family_multimedialink mml
		on f.wife_id = mml.indi_id
	left join family_multimediarecord mmr
		on mml.obje_id = mmr.id
	left join family_multimediarecord mmr2
		on mmr._pari = mmr2._prin
		and mmr._prim = 'Y'
		and mmr.tree_id = mmr2.tree_id
)
select
	f.*,
	coalesce(h.mmr2_id, h.mmr_id) as husb_mmr_id,
	coalesce(w.mmr2_id, w.mmr_id) as wife_mmr_id
from cte_family f
left join cte_husb h
	on f.fami_id = h.fami_id
	and f.husb_id = h.husb_id
	and h.rn = 1
left join cte_wife w
	on f.fami_id = w.fami_id
	and f.wife_id = w.wife_id
	and w.rn = 1;

