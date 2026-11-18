-- Vanilla dungeons and Zul'Gurub: ranged trash moves again when it loses line of sight.
-- These Shoot/Throw casts carried SMARTCAST_COMBAT_MOVE (64), which stops combat movement after a
-- successful cast and makes the spell the chase distance. That fights the "Within 5-30 Range"
-- rows next to them, which decide when the mob stops and moves. SMARTCAST_ENABLE_COMBAT_MOVE_ON_LOS
-- (512) only lets a mob walk when the cast fails for line of sight, so the range rows stay in charge.
-- Same rows and value as Grimfeather/mod-individual-progression PRs #272, #273 and #289 (their
-- final state); their Karazhan and Sunwell rows wait for the TBC tier.
--   622 id 3: Goblin Engineer - Within Range 5-30yd - Cast Shoot
--   1725 id 3: Defias Watchman - Within Range 5-30yd - Cast Shoot
--   4281 id 3: Scarlet Scout - Within 5-30 Range - Cast Shoot
--   4288 id 3: Scarlet Beastmaster - Within 5-30 Range - Cast Shoot
--   4417 id 3: Defias Taskmaster - Within Range 5-30yd - Cast Shoot
--   4831 id 3: Lady Sarevess - Within 5-30 Range - Cast Shoot
--   7290 id 3: Shadowforge Sharpshooter - Within 5-30 Range - Cast Shoot
--   7332 id 3: Withered Spearhide - Within 5-30 Range - Cast Shoot
--   8896 id 3: Shadowforge Peasant - Within 5-30 Range - Cast Shoot
--   8896 id 4: Shadowforge Peasant - Within 0-30 Range - Cast Throw Dynamite
--   8899 id 3: Doomforge Dragoon - Within 5-30 Range - Cast Shoot
--   8901 id 3: Anvilrage Reservist - Within 5-30 Range - Cast Shoot
--   8902 id 3: Shadowforge Citizen - Within 5-30 Range - Cast Shoot
--   10558 id 3: Hearthsinger Forresten - Within 5-30 Range - Cast Shoot
--   11339 id 3: Hakkari Shadow Hunter - In Combat - Cast Shoot
--   11350 id 3: Gurubashi Axe Thrower - Within 5-30 Range - Cast Throw
--   11351 id 3: Gurubashi Headhunter - Within 5-30 Range - Cast Throw
--   11454 id 3: Wildspawn Betrayer - Within 5-30 Range - Cast Shoot
--   11488 id 3: Illyanna Ravenoak - Within 5-30 Range - Cast Shoot
--   11686 id 3: Ghostly Raider - Within 5-30 Range - Cast Shoot
-- Re-runnable (only rows still at 64 with the same spell change).
-- Rollback: rollback/world/2026_11_18_02_vanilla_ranged_trash_los.rollback.sql
UPDATE `smart_scripts` SET `action_param2` = 512
 WHERE `action_type` = 11 AND `action_param2` = 64
   AND (`entryorguid`, `source_type`, `id`, `action_param1`) IN (
  (622, 0, 3, 6660),
  (1725, 0, 3, 6660),
  (4281, 0, 3, 6660),
  (4288, 0, 3, 6660),
  (4417, 0, 3, 6660),
  (4831, 0, 3, 6660),
  (7290, 0, 3, 6660),
  (7332, 0, 3, 6660),
  (8896, 0, 3, 6660),
  (8896, 0, 4, 7978),
  (8899, 0, 3, 15620),
  (8901, 0, 3, 6660),
  (8902, 0, 3, 15547),
  (10558, 0, 3, 16100),
  (11339, 0, 3, 16496),
  (11350, 0, 3, 16075),
  (11351, 0, 3, 22887),
  (11454, 0, 3, 16100),
  (11488, 0, 3, 16100),
  (11686, 0, 3, 6660));
