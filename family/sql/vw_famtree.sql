--drop view family_vw_famtree;

create view family_vw_famtree as 
select
	row_number() over (order by t.id, p.user_id) as id,
	p.user_id,
	p.can_view,
	p.can_clone,
	p.can_change,
	p.can_delete,
	p.can_merge,
	t.id as task_id,
    t.sour,
    t.sour_vers,
    t.sour_name,
    t.sour_corp,
    t.sour_corp_addr_id,
    t.sour_data,
    t.sour_data_date,
    t.sour_data_copr,
    t.dest,
    t.date,
    t.time,
    t.subm_id,
    t.file,
    t.copr,
    t.gedc_vers,
    t.gedc_form,
    t.gedc_form_vers,
    t.char,
    t.lang,
    t.note,
    t.mh_id,
    t.mh_prj_id,
    t.mh_rtl,
    t.sort,
    t.created,
    t.last_mod,
    t.mark,
    t.cur_indi as cur_indi_id,
    t.name,
    t.depth
	
from family_famtreepermission p
join family_famtree t
	on p.tree_id = t.id;
