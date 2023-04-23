--DROP VIEW vw_tasks;
/* --- SQLITE ---
CREATE VIEW vw_tasks AS
WITH cte_roles AS (
			  SELECT d.id, d.user_id, d.app_task   AS num_role, 'todo'   AS app FROM task_task d WHERE COALESCE(d.app_task, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_note   AS num_role, 'note'   AS app FROM task_task d WHERE COALESCE(d.app_note, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_news   AS num_role, 'news'   AS app FROM task_task d WHERE COALESCE(d.app_news, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_store  AS num_role, 'store'  AS app FROM task_task d WHERE COALESCE(d.app_store, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_doc    AS num_role, 'docs'   AS app FROM task_task d WHERE COALESCE(d.app_doc, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_warr   AS num_role, 'warr'   AS app FROM task_task d WHERE COALESCE(d.app_warr, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_expen  AS num_role, 'expen'  AS app FROM task_task d WHERE COALESCE(d.app_expen, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_trip   AS num_role, 'trip'   AS app FROM task_task d WHERE COALESCE(d.app_trip, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_fuel   AS num_role, 'fuel'   AS app FROM task_task d WHERE COALESCE(d.app_fuel, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_apart  AS num_role, 'apart'  AS app FROM task_task d WHERE COALESCE(d.app_apart, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_health AS num_role, 'health' AS app FROM task_task d WHERE COALESCE(d.app_health, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_work   AS num_role, 'work'   AS app FROM task_task d WHERE COALESCE(d.app_work, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_photo  AS num_role, 'photo'  AS app FROM task_task d WHERE COALESCE(d.app_photo, 0) != 0
)
--SELECT * FROM cte_roles WHERE id = 60065;
, cte_icon(is_base, num_role, role, icon) as (
	VALUES
    (1, 1, 'todo', 'check2-square'),
    (1, 2, 'note', 'sticky'),
    (1, 3, 'news', 'newspaper'),
    (1, 4, 'store', 'key'),
    (0, 38, 'store_hist', 'clock-history'),
    (1, 5, 'doc', 'file-text'),
    (1, 6, 'warr', 'award'),
    (1, 7, 'expense', 'piggy-bank'),
    (1, 9, 'person', 'person'),
    (0, 10, 'trip', 'truck'),
    (0, 8, 'saldo', 'currency-dollar'),
    (1, 12, 'fuel', 'fuel-pump'),
    (0, 11, 'car', 'truck'),
    (0, 13, 'part', 'cart'),
    (0, 14, 'service', 'tools'),
    (0, 15, 'apart', 'building'),
    (0, 16, 'meter', 'speedometer2'),
    (0, 17, 'price', 'tag'),
    (1, 18, 'bill', 'receipt'),
    (1, 19, 'marker', 'heart'),
    (0, 20, 'incident', 'termometer-half'),
    (0, 21, 'weight', 'info-square'),
    (0, 36, 'waist', 'info-square'),
    (0, 37, 'temp', 'info-square'),
    (1, 22, 'period', 'calendar-range'),
    (0, 23, 'department', 'door-closed'),
    (0, 24, 'dep_hist', 'clock-history'),
    (0, 25, 'post', 'display'),
    (0, 26, 'employee', 'people'),
    (0, 27, 'fio_hist', 'clock-history'),
    (0, 28, 'child', 'people'),
    (0, 29, 'appointment', 'briefcase'),
    (0, 30, 'education', 'book'),
    (0, 31, 'empl_per', 'person-lines-fill'),
    (0, 32, 'pay_title', 'pencil-square'),
    (0, 33, 'payment', 'calculator'),
    (1, 34, 'photo', 'image'),
    (1, 35, 'account', 'person-check'),
    (1, 39, 'apache', 'card-list'),
    (1, 40, 'short', 'save'),
    (0, 41, 'full', 'save-fill'),
    (0, 42, 'check', 'card-list')
)
--select * from cte_icon;
, cte_todo_termin as (
	SELECT
		r.id,
		r.app,
		r.num_role,
		ri.role,
		COALESCE(ri.icon, 'search-results') as icon,
		CASE WHEN r.num_role != 1 OR t.stop IS NULL THEN NULL ELSE CAST ((julianday(date(t.stop)) - julianday(date('now'))) AS INTEGER) END as termin,
		t.completed,
		t.task_2_id,
		t.price_service,
		GROUP_CONCAT(bi.is_base || '_' || b.app || '_' || b.num_role || '_' || COALESCE(bi.icon, 'search-results')) as related -- SQLite
		--GROUP_CONCAT(CONCAT(bi.is_base, '_', b.app, '_', b.role, '_', COALESCE(bi.icon, 'search-results'))) as related -- MySQL
	FROM cte_roles r
	JOIN task_task t
		ON r.id = t.id
	LEFT JOIN cte_roles b
		ON r.id = b.id
		AND r.num_role != b.num_role
	LEFT JOIN cte_icon ri
		ON r.num_role = ri.num_role
	LEFT JOIN cte_icon bi
		ON b.num_role = bi.num_role
	GROUP BY
		r.id,
		r.num_role,
		r.app,
		CASE WHEN r.num_role != 1 OR t.stop IS NULL THEN NULL ELSE CAST ((julianday(date(t.stop)) - julianday(date('now'))) AS INTEGER) END,
		t.completed,
		t.task_2_id,
		t.price_service
)
--SELECT * from cte_todo_termin; -- 8327
, cte_subgroup_id as (
	SELECT
		t.id,
		t.app,
		t.num_role,
		t.role,
		t.icon,
		t.related,
		t.completed,
		t.task_2_id,
		t.price_service,
		CASE 
			WHEN t.completed = 1 THEN 6 -- Completed
			WHEN t.num_role = 1 AND t.termin IS NULL THEN 0
			WHEN t.num_role = 1 AND t.termin < 0 THEN 1 -- Earler
			WHEN t.num_role = 1 AND t.termin = 0 THEN 2 -- Today
			WHEN t.num_role = 1 AND t.termin = 1 THEN 3 -- Tomorrow
			WHEN t.num_role = 1 AND t.termin < 8 THEN 4 -- On Week
			WHEN t.num_role = 1 THEN 5 -- Later
			WHEN t.num_role = 14 THEN COALESCE(t.task_2_id, 0) -- FUEL_SERVICE
			WHEN t.num_role = 17 THEN COALESCE(t.price_service, 0) -- APART_PRICE
			ELSE 0
		END as subgroup_id
	FROM cte_todo_termin t
)
--SELECT * from cte_subgroup_id where id = 60065;
, cte_grps_planned (num_role, id, name) as (
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
, cte_grp_role_by_task_role (task_num_role, task_app) as (
	VALUES
		(1, 'todo'),
		(2, 'note'),
		(3, 'news'),
		(4, 'store'),
		(38, 'store'),
		(6, 'warr'),
		(7, 'expense')
)
, cte_task_info as (
	SELECT
		t.id as task_id,
		SUBSTR(REPLACE(t.info, X'0A', ' '), 1, 80) || CASE WHEN LENGTH(REPLACE(t.info, X'0A', ' ')) > 80 THEN '...' ELSE '' END as task_descr,
		CASE WHEN COUNT(tu.href) > 0 THEN 1 ELSE 0 END as has_links
	FROM task_task t
	LEFT JOIN task_urls tu
		ON t.id = tu.task_id
	GROUP BY
		t.id
)
--, q1 as (
	SELECT
		s.app,
		s.num_role,
		s.role,
		s.icon,
		s.related,
		s.subgroup_id,
		CASE
			WHEN s.num_role = 1 THEN COALESCE(p.name, '') -- TODO
			WHEN s.num_role = 14 THEN COALESCE(t2.name, '') -- FUEL_SERVICE
			WHEN s.num_role = 17 THEN COALESCE(a.name, '') -- APART_PRICE
		END as subgroup_name,
		g.group_id, 
		g.role as group_role,
		gr.name as group_name,
		tri.info as custom_attr,
		ti.task_descr,
		CASE WHEN tri.files_qnt > 0 THEN 1 ELSE 0 END as has_files,
		ti.has_links,
		t.*
	FROM cte_subgroup_id s
	JOIN task_task t
		ON s.id = t.id
	LEFT JOIN cte_grp_role_by_task_role r
		ON s.num_role = r.task_num_role
	LEFT JOIN task_taskgroup g
		ON s.id = g.task_id
		AND COALESCE(r.task_app, '') = g.role
	LEFT JOIN task_group gr
		ON g.group_id = gr.id
	LEFT JOIN cte_grps_planned p
		ON s.num_role = p.num_role
		AND s.subgroup_id = p.id
	LEFT JOIN task_task t2
		ON s.task_2_id = t2.id
	LEFT JOIN cte_apart_service a
		ON s.price_service = a.id
	LEFT JOIN task_taskroleinfo tri
		ON s.id = tri.task_id
		AND s.app = tri.app
		AND s.role = tri.role
	LEFT JOIN cte_task_info ti
		ON s.id = ti.task_id
--)
--select * from q1 where id = 60065
;
*/



/* --- MYSQL ---
CREATE VIEW vw_tasks AS
WITH cte_roles AS (
			  SELECT d.id, d.user_id, d.app_task   AS num_role, 'todo'   AS app FROM task_task d WHERE COALESCE(d.app_task, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_note   AS num_role, 'note'   AS app FROM task_task d WHERE COALESCE(d.app_note, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_news   AS num_role, 'news'   AS app FROM task_task d WHERE COALESCE(d.app_news, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_store  AS num_role, 'store'  AS app FROM task_task d WHERE COALESCE(d.app_store, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_doc    AS num_role, 'docs'   AS app FROM task_task d WHERE COALESCE(d.app_doc, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_warr   AS num_role, 'warr'   AS app FROM task_task d WHERE COALESCE(d.app_warr, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_expen  AS num_role, 'expen'  AS app FROM task_task d WHERE COALESCE(d.app_expen, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_trip   AS num_role, 'trip'   AS app FROM task_task d WHERE COALESCE(d.app_trip, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_fuel   AS num_role, 'fuel'   AS app FROM task_task d WHERE COALESCE(d.app_fuel, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_apart  AS num_role, 'apart'  AS app FROM task_task d WHERE COALESCE(d.app_apart, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_health AS num_role, 'health' AS app FROM task_task d WHERE COALESCE(d.app_health, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_work   AS num_role, 'work'   AS app FROM task_task d WHERE COALESCE(d.app_work, 0) != 0
	UNION ALL SELECT d.id, d.user_id, d.app_photo  AS num_role, 'photo'  AS app FROM task_task d WHERE COALESCE(d.app_photo, 0) != 0
)
, cte_icon(is_base, num_role, role, icon) as (
	VALUES
    ROW(1, 1, 'todo', 'check2-square'),
    ROW(1, 2, 'note', 'sticky'),
    ROW(1, 3, 'news', 'newspaper'),
    ROW(1, 4, 'store', 'key'),
    ROW(0, 38, 'store_hist', 'clock-history'),
    ROW(1, 5, 'doc', 'file-text'),
    ROW(1, 6, 'warr', 'award'),
    ROW(1, 7, 'expense', 'piggy-bank'),
    ROW(1, 9, 'person', 'person'),
    ROW(0, 10, 'trip', 'truck'),
    ROW(0, 8, 'saldo', 'currency-dollar'),
    ROW(1, 12, 'fuel', 'fuel-pump'),
    ROW(0, 11, 'car', 'truck'),
    ROW(0, 13, 'part', 'cart'),
    ROW(0, 14, 'service', 'tools'),
    ROW(0, 15, 'apart', 'building'),
    ROW(0, 16, 'meter', 'speedometer2'),
    ROW(0, 17, 'price', 'tag'),
    ROW(1, 18, 'bill', 'receipt'),
    ROW(1, 19, 'marker', 'heart'),
    ROW(0, 20, 'incident', 'termometer-half'),
    ROW(0, 21, 'weight', 'info-square'),
    ROW(0, 36, 'waist', 'info-square'),
    ROW(0, 37, 'temp', 'info-square'),
    ROW(1, 22, 'period', 'calendar-range'),
    ROW(0, 23, 'department', 'door-closed'),
    ROW(0, 24, 'dep_hist', 'clock-history'),
    ROW(0, 25, 'post', 'display'),
    ROW(0, 26, 'employee', 'people'),
    ROW(0, 27, 'fio_hist', 'clock-history'),
    ROW(0, 28, 'child', 'people'),
    ROW(0, 29, 'appointment', 'briefcase'),
    ROW(0, 30, 'education', 'book'),
    ROW(0, 31, 'empl_per', 'person-lines-fill'),
    ROW(0, 32, 'pay_title', 'pencil-square'),
    ROW(0, 33, 'payment', 'calculator'),
    ROW(1, 34, 'photo', 'image'),
    ROW(1, 35, 'account', 'person-check'),
    ROW(1, 39, 'apache', 'card-list'),
    ROW(1, 40, 'short', 'save'),
    ROW(0, 41, 'full', 'save-fill'),
    ROW(0, 42, 'check', 'card-list')
)
, cte_todo_termin as (
	SELECT
		r.id,
		r.app,
		r.num_role,
		ri.role,
		COALESCE(ri.icon, 'search-results') as icon,
		CASE WHEN r.num_role != 1 OR t.stop IS NULL THEN NULL ELSE DATEDIFF(t.stop, CURRENT_DATE()) END as termin,
		t.completed,
		t.task_2_id,
		t.price_service,
		GROUP_CONCAT(CONCAT(bi.is_base, '_', b.app, '_', b.num_role, '_', COALESCE(bi.icon, 'search-results'))) as related
	FROM cte_roles r
	JOIN task_task t
		ON r.id = t.id
	LEFT JOIN cte_roles b
		ON r.id = b.id
		AND r.num_role != b.num_role
	LEFT JOIN cte_icon ri
		ON r.num_role = ri.num_role
	LEFT JOIN cte_icon bi
		ON b.num_role = bi.num_role
	GROUP BY
		r.id,
		r.app,
		r.num_role,
		ri.role,
		COALESCE(ri.icon, 'search-results'),
		CASE WHEN r.num_role != 1 OR t.stop IS NULL THEN NULL ELSE DATEDIFF(t.stop, CURRENT_DATE()) END,
		t.completed,
		t.task_2_id,
		t.price_service
)
, cte_subgroup_id as (
	SELECT
		t.id,
		t.app,
		t.num_role,
		t.role,
		t.icon,
		t.related,
		t.completed,
		t.task_2_id,
		t.price_service,
		CASE 
			WHEN t.completed = 1 THEN 6
			WHEN t.num_role = 1 AND t.termin IS NULL THEN 0
			WHEN t.num_role = 1 AND t.termin < 0 THEN 1
			WHEN t.num_role = 1 AND t.termin = 0 THEN 2
			WHEN t.num_role = 1 AND t.termin = 1 THEN 3
			WHEN t.num_role = 1 AND t.termin < 8 THEN 4
			WHEN t.num_role = 1 THEN 5
			WHEN t.num_role = 14 THEN COALESCE(t.task_2_id, 0)
			WHEN t.num_role = 17 THEN COALESCE(t.price_service, 0)
			ELSE 0
		END as subgroup_id
	FROM cte_todo_termin t
)
, cte_grps_planned (num_role, id, name) as (
	VALUES
    ROW(1, 0, ''),
    ROW(1, 1, 'Earlier'),
    ROW(1, 2, 'Today'),
    ROW(1, 3, 'Tomorrow'),
    ROW(1, 4, 'On the week'),
    ROW(1, 5, 'Later'),
    ROW(1, 6, 'Completed')
)
, cte_apart_service (id, name) as (
	VALUES
    ROW(0, 'не задано'),
    ROW(1, 'электроснабжение'),
    ROW(2, 'газоснабжение'),
    ROW(3, 'вода'),
    ROW(4, 'водоснабжение'),
    ROW(5, 'водоотведение'),
    ROW(6, 'не задано'),
    ROW(7, '!?-7'),
    ROW(9, '!?-8'),
    ROW(10, 'kill'),
    ROW(11, 'электроснабжение'),
    ROW(12, '!?-11'),
    ROW(13, 'kill-1'),
    ROW(14, 'kill-3'),
    ROW(15, 'kill-2'),
    ROW(16, '!?-15'),
    ROW(17, 'членские взносы'),
    ROW(18, '!?-17'),
    ROW(19, '!?-18'),
    ROW(20, '!?-19'),
    ROW(21, '!?-20')
)
, cte_grp_role_by_task_role (task_num_role, task_app) as (
	VALUES
		ROW(1, 'todo'),
		ROW(2, 'note'),
		ROW(3, 'news'),
		ROW(4, 'store'),
		ROW(38, 'store'),
		ROW(6, 'warr'),
		ROW(7, 'expense')
)
, cte_task_info as (
	SELECT
		t.id as task_id,
        CONCAT(SUBSTR(REPLACE(REPLACE(t.info, CHAR(13), ' '), CHAR(10), ''), 1, 80), CASE WHEN LENGTH(REPLACE(REPLACE(t.info, CHAR(13), ' '), CHAR(10), '')) > 80 THEN '...' ELSE '' END) as task_descr,
		CASE WHEN COUNT(tu.href) > 0 THEN 1 ELSE 0 END as has_links
	FROM task_task t
	LEFT JOIN task_urls tu
		ON t.id = tu.task_id
	GROUP BY
		t.id
)
	SELECT
		s.app,
		s.num_role,
		s.role,
		s.icon,
		s.related,
		s.subgroup_id,
		CASE
			WHEN s.num_role = 1 THEN COALESCE(p.name, '')
			WHEN s.num_role = 14 THEN COALESCE(t2.name, '')
			WHEN s.num_role = 17 THEN COALESCE(a.name, '')
		END as subgroup_name,
		g.group_id, 
		g.role as group_role,
		gr.name as group_name,
		tri.info as custom_attr,
		ti.task_descr,
		CASE WHEN tri.files_qnt > 0 THEN 1 ELSE 0 END as has_files,
		ti.has_links,
		t.*
	FROM cte_subgroup_id s
	JOIN task_task t
		ON s.id = t.id
	LEFT JOIN cte_grp_role_by_task_role r
		ON s.num_role = r.task_num_role
	LEFT JOIN task_taskgroup g
		ON s.id = g.task_id
		AND COALESCE(r.task_app, '') = g.role
	LEFT JOIN task_group gr
		ON g.group_id = gr.id
	LEFT JOIN cte_grps_planned p
		ON s.num_role = p.num_role
		AND s.subgroup_id = p.id
	LEFT JOIN task_task t2
		ON s.task_2_id = t2.id
	LEFT JOIN cte_apart_service a
		ON s.price_service = a.id
	LEFT JOIN task_taskroleinfo tri
		ON s.id = tri.task_id
		AND s.app = tri.app
		AND s.role = tri.role
	LEFT JOIN cte_task_info ti
		ON s.id = ti.task_id
;

*/