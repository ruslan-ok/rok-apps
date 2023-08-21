CREATE VIEW vw_health_stat AS
with cte_weight_values as (
	select 
		user_id,
		'weight' as mark,
		max(bio_weight) as max_value,
		min(bio_weight) as min_value,
		max(date(event)) as max_date,
		min(date(event)) as min_date
	from task_task
	where coalesce(app_health, 0) = 19
		and coalesce(bio_weight, 0) > 0
	group by user_id
)
, cte_max_weight as (
	select 
		t.user_id,
		max(date(t.event)) as max_value_date
	from task_task t,
		cte_weight_values v
	where coalesce(t.app_health, 0) = 19
		and coalesce(t.bio_weight, 0) = v.max_value
		and t.user_id = v.user_id
	group by t.user_id
)
, cte_min_weight as (
	select 
		t.user_id,
		max(date(t.event)) as min_value_date
	from task_task t,
		cte_weight_values v
	where coalesce(t.app_health, 0) = 19
		and coalesce(t.bio_weight, 0) = v.min_value
		and t.user_id = v.user_id
	group by t.user_id
)
, cte_weight as (
	select
		v.*, i.min_value_date, a.max_value_date
	from cte_weight_values v,
		cte_max_weight a,
		cte_min_weight i
)
, cte_waist_values as (
	select 
		user_id,
		'waist' as mark,
		max(bio_waist) as max_value,
		min(bio_waist) as min_value,
		max(date(event)) as max_date,
		min(date(event)) as min_date
	from task_task
	where coalesce(app_health, 0) = 19
		and coalesce(bio_waist, 0) > 0
	group by user_id
)
, cte_max_waist as (
	select 
		t.user_id,
		max(date(t.event)) as max_value_date
	from task_task t, 
		cte_waist_values v
	where coalesce(t.app_health, 0) = 19
		and coalesce(t.bio_waist, 0) = v.max_value
		and t.user_id = v.user_id
	group by t.user_id
)
, cte_min_waist as (
	select 
		t.user_id,
		max(date(t.event)) as min_value_date
	from task_task t,
		cte_waist_values v
	where coalesce(t.app_health, 0) = 19
		and coalesce(t.bio_waist, 0) = v.min_value
		and t.user_id = v.user_id
	group by t.user_id
)
, cte_waist as (
	select
		v.*, i.min_value_date, a.max_value_date
	from cte_waist_values v,
		cte_max_waist a,
		cte_min_waist i
)
, cte_temp_values as (
	select 
		user_id,
		'temp' as mark,
		max(bio_temp) as max_value,
		min(bio_temp) as min_value,
		max(date(event)) as max_date,
		min(date(event)) as min_date
	from task_task
	where coalesce(app_health, 0) = 19
		and coalesce(bio_temp, 0) > 0
	group by user_id
)
, cte_max_temp as (
	select 
		t.user_id,
		max(date(t.event)) as max_value_date
	from task_task t,
		cte_temp_values v
	where coalesce(t.app_health, 0) = 19
		and coalesce(t.bio_temp, 0) = v.max_value
		and t.user_id = v.user_id
	group by t.user_id
)
, cte_min_temp as (
	select 
		t.user_id,
		max(date(t.event)) as min_value_date
	from task_task t, cte_temp_values v
	where coalesce(t.app_health, 0) = 19
		and coalesce(t.bio_temp, 0) = v.min_value
		and t.user_id = v.user_id
	group by t.user_id
)
, cte_temp as (
	select
		v.*, i.min_value_date, a.max_value_date
	from cte_temp_values v,
		cte_max_temp a,
		cte_min_temp i
)
select * from cte_weight
union all
select * from cte_waist
union all
select * from cte_temp;
