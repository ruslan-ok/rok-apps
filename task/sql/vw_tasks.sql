--DROP VIEW vw_tasks;
CREATE VIEW vw_tasks AS
WITH cte_roles AS (
			  SELECT d.id, d.user_id, d.app_task   AS role FROM task_task d WHERE COALESCE(d.app_task, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_note   AS role FROM task_task d WHERE COALESCE(d.app_note, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_news   AS role FROM task_task d WHERE COALESCE(d.app_news, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_store  AS role FROM task_task d WHERE COALESCE(d.app_store, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_doc    AS role FROM task_task d WHERE COALESCE(d.app_doc, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_warr   AS role FROM task_task d WHERE COALESCE(d.app_warr, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_expen  AS role FROM task_task d WHERE COALESCE(d.app_expen, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_trip   AS role FROM task_task d WHERE COALESCE(d.app_trip, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_fuel   AS role FROM task_task d WHERE COALESCE(d.app_fuel, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_apart  AS role FROM task_task d WHERE COALESCE(d.app_apart, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_health AS role FROM task_task d WHERE COALESCE(d.app_health, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_work   AS role FROM task_task d WHERE COALESCE(d.app_work, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_photo  AS role FROM task_task d WHERE COALESCE(d.app_photo, 0) != 0
)
--SELECT * FROM cte_roles;
, cte_todo_termin as (
	SELECT
		r.id,
		r.role,
		CASE WHEN r.role != 1 OR t.stop IS NULL THEN NULL ELSE CAST ((julianday(t.stop) - julianday('now')) AS INTEGER) END as termin,
		t.completed,
		t.task_2_id,
		t.price_service
	FROM cte_roles r
	JOIN task_task t
		ON r.id = t.id
)
--SELECT * from cte_todo_termin where termin > 0;
, cte_subgroup_id as (
	SELECT
		t.id,
		t.role,
		t.completed,
		t.task_2_id,
		t.price_service,
		CASE 
			WHEN t.completed = 1 THEN 6 -- Completed
			WHEN t.role = 1 AND t.termin IS NULL THEN 0
			WHEN t.role = 1 AND t.termin < 0 THEN 1 -- Earler
			WHEN t.role = 1 AND t.termin = 0 THEN 2 -- Today
			WHEN t.role = 1 AND t.termin = 1 THEN 3 -- Tomorrow
			WHEN t.role = 1 AND t.termin < 8 THEN 4 -- On Week
			WHEN t.role = 1 THEN 5 -- Later
			WHEN t.role = 14 THEN COALESCE(t.task_2_id, 0) -- FUEL_SERVICE
			WHEN t.role = 17 THEN COALESCE(t.price_service, 0) -- APART_PRICE
			ELSE 0
		END as subgroup_id
	FROM cte_todo_termin t
)
--SELECT * from cte_subgroup_id;
, cte_grps_planned (role, id, name) as (
	VALUES
    (1, 0, ''),
    (1, 1, 'Earlier'),
    (1, 2, 'Today'),
    (1, 3, 'Tomorrow'),
    (1, 4, 'On the week'),
    (1, 5, 'Later'),
    (1, 6, 'Completed')
)
, cte_apart_service (id, name) as (
	VALUES
    (0, 'не задано'),
    (1, 'электроснабжение'),
    (2, 'газоснабжение'),
    (3, 'вода'),
    (4, 'водоснабжение'),
    (5, 'водоотведение'),
    (6, 'не задано'),
    (7, '!?-7'),
    (9, '!?-8'),
    (10, 'kill'),
    (11, 'электроснабжение'),
    (12, '!?-11'),
    (13, 'kill-1'),
    (14, 'kill-3'),
    (15, 'kill-2'),
    (16, '!?-15'),
    (17, 'членские взносы'),
    (18, '!?-17'),
    (19, '!?-18'),
    (20, '!?-19'),
    (21, '!?-20')
)
, cte_grp_role_by_task_role (task_role, task_app) as (
	VALUES
		(1, 'todo'),
		(2, 'note'),
		(3, 'news'),
		(4, 'store'),
		(38, 'store'),
		(6, 'warr'),
		(7, 'expense')
)
--, Q1 AS (
	SELECT
		s.role as task_role,
		s.subgroup_id,
		CASE
			WHEN s.role = 1 THEN COALESCE(p.name, '') -- TODO
			WHEN s.role = 14 THEN COALESCE(t2.name, '') -- FUEL_SERVICE
			WHEN s.role = 17 THEN COALESCE(a.name, '') -- APART_PRICE
		END as subgroup_name,
		g.group_id, 
		g.role as group_role,
		t.*
	FROM cte_subgroup_id s
	JOIN task_task t
		ON s.id = t.id
	JOIN cte_grp_role_by_task_role r
		ON s.role = r.task_role
	LEFT JOIN task_taskgroup g
		ON s.id = g.task_id
		AND r.task_app = g.role
	LEFT JOIN cte_grps_planned p
		ON s.role = p.role
		AND s.subgroup_id = p.id
	LEFT JOIN task_task t2
		ON s.task_2_id = t2.id
	LEFT JOIN cte_apart_service a
		ON s.price_service = a.id

--)
--SELECT *
--FROM Q1
--where task_role = 2 and user_id = 16 order by event desc;

--SELECT *
--FROM Q1
--WHERE ID = 67116;

