-- Rollback for data/sql/world/updates/2026_11_18_00_ip_exact_custom_damage.sql.
-- Kept outside data/sql so the updater never runs it. Re-runnable.
DELETE FROM `spell_script_names`
 WHERE `spell_id` IN (41926, 90008, 28167) AND `ScriptName` = 'spell_ip_exact_custom_damage';
-- Also remove the updater's record so a later re-deploy applies the update again:
DELETE FROM `updates` WHERE `name` = '2026_11_18_00_ip_exact_custom_damage.sql';
