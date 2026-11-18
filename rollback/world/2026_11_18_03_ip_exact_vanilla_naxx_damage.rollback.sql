-- Rollback for data/sql/world/updates/2026_11_18_03_ip_exact_vanilla_naxx_damage.sql.
-- Kept outside data/sql so the updater never runs it. Re-runnable.
DELETE FROM `spell_script_names`
 WHERE (`spell_id` IN (28783, 28796, 28206, 28099, 29214) AND `ScriptName` = 'spell_ip_exact_custom_damage')
    OR (`spell_id` IN (28796, 28794, 29214) AND `ScriptName` = 'spell_ip_exact_custom_periodic');
-- Also remove the updater's record so a later re-deploy applies the update again:
DELETE FROM `updates` WHERE `name` = '2026_11_18_03_ip_exact_vanilla_naxx_damage.sql';
