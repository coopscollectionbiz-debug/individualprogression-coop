-- Naxx40: the spells whose IP script value is the vanilla 1.12 value land at exactly that value,
-- without the WotLK spell's die roll on top. Wowhead Classic shows one value, no range, for each
-- (the classic value is IP's + 1, base points + 1):
--   28783 Impale              (Anub'Rekhan)      3937          +0..1374 removed
--   28796 Poison Bolt Volley  (Faerlina)         1224, DoT 416 +0..750 / +0..240 removed
--   28794 Rain of Fire        (Faerlina)         DoT 1849      +0..374 removed
--   28206 Mutagen Explosion   (Grobbulus)        2379          +0..1000 removed
--   28099 Tesla Shock         (Thaddius)         4374          +0..1874 removed
--   29214 Wrath of the Plaguebringer (Noth)      1757, DoT 874 +0..600 / +0..374 removed
-- Direct damage: spell_ip_exact_custom_damage. Periodic: spell_ip_exact_custom_periodic.
-- Casts without IP's custom value keep their roll (see src/spellScripts/spellScripts.cpp).
-- Re-runnable. Rollback: rollback/world/2026_11_18_03_ip_exact_vanilla_naxx_damage.rollback.sql
DELETE FROM `spell_script_names`
 WHERE (`spell_id` IN (28783, 28796, 28206, 28099, 29214) AND `ScriptName` = 'spell_ip_exact_custom_damage')
    OR (`spell_id` IN (28796, 28794, 29214) AND `ScriptName` = 'spell_ip_exact_custom_periodic');
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES
(28783, 'spell_ip_exact_custom_damage'),
(28796, 'spell_ip_exact_custom_damage'),
(28206, 'spell_ip_exact_custom_damage'),
(28099, 'spell_ip_exact_custom_damage'),
(29214, 'spell_ip_exact_custom_damage'),
(28796, 'spell_ip_exact_custom_periodic'),
(28794, 'spell_ip_exact_custom_periodic'),
(29214, 'spell_ip_exact_custom_periodic');
