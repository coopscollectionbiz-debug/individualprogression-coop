-- Rollback for data/sql/world/updates/2026_11_18_02_vanilla_ranged_trash_los.sql.
-- Kept outside data/sql so the updater never runs it. Re-runnable.
UPDATE `smart_scripts` SET `action_param2` = 64
 WHERE `action_type` = 11 AND `action_param2` = 512
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
DELETE FROM `updates` WHERE `name` = '2026_11_18_02_vanilla_ranged_trash_los.sql';
