-- Onyxia 40: let the Onyxian Warders (301002) use their abilities.
-- Their four SmartAI casts (Fire Nova, Flame Lash, Cleave, Pierce Armor) carried event_flags 6:
-- SMART_EVENT_FLAG_DIFFICULTY_0 | _1. SmartScript only keeps such an event when
-- (1 << (spawnMode + 1)) & event_flags (SmartScript.cpp), and Onyxia 40 runs at spawn mode 2
-- (bit 0x8): the Warders only ever meleed. They only spawn in Onyxia 40 (spawnMask 4), so no
-- difficulty flag is needed. Same change as Grimfeather/mod-individual-progression's
-- dungeon_onyxia.sql (event_flags 0).
-- Re-runnable. Rollback: rollback/world/2026_11_18_01_ony40_warder_event_flags.rollback.sql
UPDATE `smart_scripts` SET `event_flags` = 0
 WHERE `entryorguid` = 301002 AND `source_type` = 0 AND `id` IN (0, 1, 2, 3) AND `event_flags` = 6;
