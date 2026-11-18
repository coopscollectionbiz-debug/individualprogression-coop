-- Rollback for data/sql/world/updates/2026_11_18_01_ony40_warder_event_flags.sql.
-- Kept outside data/sql so the updater never runs it. Re-runnable.
UPDATE `smart_scripts` SET `event_flags` = 6
 WHERE `entryorguid` = 301002 AND `source_type` = 0 AND `id` IN (0, 1, 2, 3) AND `event_flags` = 0;
DELETE FROM `updates` WHERE `name` = '2026_11_18_01_ony40_warder_event_flags.sql';
