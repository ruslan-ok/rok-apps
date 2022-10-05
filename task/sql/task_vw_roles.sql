CREATE VIEW task_vw_roles AS
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
SELECT
	r.role,
	t.*
FROM cte_roles r
JOIN task_task t
	ON r.id = t.id;