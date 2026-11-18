-- Bind spell_ip_exact_custom_damage (src/spellScripts/spellScripts.cpp) to the spells whose IP
-- script picks its own final damage, so the spell's die roll no longer lands on top:
--   41926 Hateful Strike (Naxx40 Patchwerk, urand 22100-22850; die 4501)
--   90008 Slime Spray    (Naxx40 Grobbulus, urand 3200-4800;   die 1401)
--   28167 Chain Lightning (Naxx40 Thaddius, urand 1850-2150;   die 675)
-- Casts of these spells without a custom value keep their roll (see the script).
-- Re-runnable. Rollback: rollback/world/2026_11_18_00_ip_exact_custom_damage.rollback.sql
DELETE FROM `spell_script_names`
 WHERE `spell_id` IN (41926, 90008, 28167) AND `ScriptName` = 'spell_ip_exact_custom_damage';
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES
(41926, 'spell_ip_exact_custom_damage'),
(90008, 'spell_ip_exact_custom_damage'),
(28167, 'spell_ip_exact_custom_damage');
