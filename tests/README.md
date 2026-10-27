# Focused progression synchronization regression tests

Run from the module directory with a C++17 compiler available:

```sh
python tests/run_progression_sync_tests.py
```

For MSVC, use a Developer Command Prompt:

```bat
python tests\run_progression_sync_tests.py --compiler cl
```

The runner extracts the current production implementations of
`GetPlayerProgressionFromQuests`, `ForceUpdateProgressionState`,
`SyncBotsProgressionToLeader`, `OnPlayerCanGroupAccept`, and `OnAddMember`.
It compiles them against instrumented player, group, and quest-template doubles.
Generated sources and executables live in a temporary directory and are removed
after the run. No database or worldserver is needed.

Assertions cover:

- All 361 transitions between progression states 0 through 18, followed by an
  identical request that must perform no rewards, removals, or saves.
- Repeated invitations and joins for a raid of 40 bots, with no additional rewards
  or saves for existing members.
- Enforced Vanilla/TBC/WotLK level eligibility and normal-account restrictions.
- Disabled-module behavior, zero-state leaders, unavailable leaders, and leaders
  who are not normal accounts.
- Explicit correction of missing rewarded quests, preservation of unrelated
  quests, invalid requests, and offline/null targets.

These tests exercise production control flow, not the complete emulator, real
quest side effects, database persistence, or concurrent map workers. They do not
establish that the incident's original memory corruption has been reproduced.
