#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <vector>

using uint8 = uint8_t;
using uint32 = uint32_t;
using ObjectGuid = uint32;
enum ProgressionState
{
    PROGRESSION_MOLTEN_CORE = 1,
    PROGRESSION_PRE_TBC = 8,
    PROGRESSION_TBC_TIER_5 = 13,
    PROGRESSION_WOTLK_TIER_5 = 18
};
enum QuestStatus { QUEST_STATUS_NONE, QUEST_STATUS_REWARDED };
struct Quest { uint32 id; };
struct ObjectMgr
{
    std::map<uint32, Quest> quests;
    Quest const* GetQuestTemplate(uint32 id)
    {
        auto itr = quests.find(id);
        return itr == quests.end() ? nullptr : &itr->second;
    }
} objectMgr;
auto* sObjectMgr = &objectMgr;

struct Player
{
    bool inWorld = true;
    bool normal = false;
    uint32 level = 60;
    std::set<uint32> quests;
    std::map<uint32, bool> pending;
    unsigned rewards = 0;
    unsigned removals = 0;
    unsigned saves = 0;
    bool IsInWorld() const { return inWorld; }
    uint32 GetLevel() const { return level; }
    QuestStatus GetQuestStatus(uint32 id) const
    {
        return quests.count(id) ? QUEST_STATUS_REWARDED : QUEST_STATUS_NONE;
    }
    void RemoveRewardedQuest(uint32 id) { quests.erase(id); pending[id] = false; ++removals; }
    void AddQuest(Quest const*, void*) { }
    void CompleteQuest(uint32) { }
    void RewardQuest(Quest const* quest, int, Player*, bool, bool)
    {
        quests.insert(quest->id);
        pending[quest->id] = true;
        ++rewards;
        SaveToDB(false, false);
    }
    void SaveToDB(bool, bool) { ++saves; pending.clear(); }
};
namespace ObjectAccessor
{
    std::map<ObjectGuid, Player*> players;
    Player* FindPlayer(ObjectGuid guid)
    {
        auto itr = players.find(guid);
        return itr == players.end() ? nullptr : itr->second;
    }
}
struct Group
{
    ObjectGuid leader = 1;
    ObjectGuid GetLeaderGUID() const { return leader; }
};
struct IndividualProgression
{
    bool enabled = true;
    bool enforceGroupRules = false;
    bool isNormalAccount(Player* player) { return player && player->normal; }
    uint8 GetPlayerProgressionFromQuests(Player*) const;
    static void ForceUpdateProgressionState(Player*, ProgressionState);
    void SyncBotsProgressionToLeader(Group*, Player*);
} progression;
auto* sIndividualProgression = &progression;
#include "production.inc"

void Seed(Player& player, unsigned state)
{
    player = Player{};
    for (unsigned i = 1; i <= state; ++i)
        player.quests.insert(66000 + i);
}

int main()
{
    for (uint32 i = 1; i <= 18; ++i)
        objectMgr.quests.emplace(66000 + i, Quest{66000 + i});

    // Exhaust every upgrade, downgrade, zero reset, and repeated explicit request.
    for (unsigned from = 0; from <= 18; ++from)
        for (unsigned to = 0; to <= 18; ++to)
        {
            Player player;
            Seed(player, from);
            progression.ForceUpdateProgressionState(&player, static_cast<ProgressionState>(to));
            assert(player.quests.size() == to);
            assert(player.rewards == (to > from ? to - from : 0));
            assert(player.removals == (from > to ? from - to : 0));
            assert(player.saves == (to > from ? to - from : unsigned(from > to)));
            unsigned saves = player.saves;
            progression.ForceUpdateProgressionState(&player, static_cast<ProgressionState>(to));
            assert(player.saves == saves);
        }

    Player leader;
    Seed(leader, 8);
    leader.normal = true;
    ObjectAccessor::players[1] = &leader;
    Group group;
    Hooks hooks;
    std::vector<Player> bots(40);
    // Repeated invitations to a raid must never save an existing member.
    for (unsigned i = 0; i < bots.size(); ++i)
    {
        ObjectGuid guid = i + 2;
        ObjectAccessor::players[guid] = &bots[i];
        assert(hooks.OnPlayerCanGroupAccept(&bots[i], &group));
        hooks.OnAddMember(&group, guid);
        for (unsigned repeat = 0; repeat < 5; ++repeat)
        {
            assert(hooks.OnPlayerCanGroupAccept(&bots[i], &group));
            hooks.OnAddMember(&group, guid);
        }
        for (unsigned j = 0; j <= i; ++j)
            assert(bots[j].rewards == 8 && bots[j].saves == 8);
    }
    assert(leader.rewards == 0 && leader.saves == 0);

    // Keep all enforced expansion-level gates and normal-player equality checks.
    progression.enforceGroupRules = true;
    for (unsigned state : {1u, 8u, 13u})
    {
        Seed(leader, state);
        leader.normal = true;
        for (unsigned level : {60u, 70u, 80u})
        {
            Player bot;
            bot.level = level;
            bool allowed = (state < 8 && level == 60) || (state == 8 && level == 70)
                || (state == 13 && level == 80);
            assert(hooks.OnPlayerCanGroupAccept(&bot, &group) == allowed);
            assert(bot.rewards == (allowed ? state : 0));
        }
        Player human;
        human.normal = true;
        assert(!hooks.OnPlayerCanGroupAccept(&human, &group));
        assert(human.saves == 0);
    }

    progression.enabled = false;
    Player disabled;
    ObjectAccessor::players[100] = &disabled;
    assert(hooks.OnPlayerCanGroupAccept(&disabled, &group));
    hooks.OnAddMember(&group, 100);
    progression.SyncBotsProgressionToLeader(&group, &disabled);
    assert(disabled.rewards == 0 && disabled.saves == 0);
    progression.enabled = true;

    // A zero-state leader must downgrade the joining bot without changing existing bots.
    Seed(leader, 0);
    leader.normal = true;
    Seed(bots[0], 8);
    assert(hooks.OnPlayerCanGroupAccept(&bots[0], &group));
    hooks.OnAddMember(&group, 2);
    assert(bots[0].quests.empty() && bots[0].saves == 1 && bots[0].rewards == 0);
    assert(bots[1].saves == 8);

    // An unavailable leader is not evidence for progression zero.
    Seed(bots[0], 8);
    group.leader = 999;
    hooks.OnPlayerCanGroupAccept(&bots[0], &group);
    hooks.OnAddMember(&group, 2);
    assert(bots[0].quests.size() == 8 && bots[0].saves == 0);
    group.leader = 1;
    leader.normal = false;
    progression.SyncBotsProgressionToLeader(&group, &bots[0]);
    assert(bots[0].saves == 0);
    leader.normal = true;

    // Explicit force repairs holes, rejects invalid states, and ignores offline players.
    Player holes;
    Seed(holes, 8);
    holes.quests.erase(66003);
    progression.ForceUpdateProgressionState(&holes, PROGRESSION_PRE_TBC);
    assert(holes.quests.size() == 8 && holes.rewards == 1);
    progression.ForceUpdateProgressionState(&holes, static_cast<ProgressionState>(255));
    assert(holes.saves == 1);
    holes.quests.insert(12345);
    progression.ForceUpdateProgressionState(&holes, static_cast<ProgressionState>(0));
    assert(holes.quests == std::set<uint32>{12345} && holes.saves == 2);
    holes.inWorld = false;
    progression.ForceUpdateProgressionState(&holes, PROGRESSION_WOTLK_TIER_5);
    assert(holes.saves == 2);
    progression.ForceUpdateProgressionState(nullptr, PROGRESSION_PRE_TBC);
    std::cout << "Passed: 361 state transitions, repeated requests, 40-bot raid joins, "
        "eligibility, disabled module, holes, invalid/offline/null inputs.\n";
}
