team_active_long = {
    "tumeken": "> Channel the power of Tumeken to unleash a blinding solar flare. This effect causes all teams ahead of Tumekenian to lose sight of their current quest and receive a new one.",
    "xeric": "> Tap into the ancient power of the Great Olm to receive the renown purple chest with 1 relic from The Wandering Wares shop.",
    "bandos": "> Wreak havoc on an opponent with General Graardor's vicious ranged attack causing all teams on the same rune to move back 1 tile and reroll their current quest.",
    "armadyl": "> Embrace the serene wings of Armadyl, granting your team unparalleled mobility and protection for the next turn. During this time, your team gains the ability to bypass traps and negative events, soaring over them with ease. Additionally, your next roll will have +2 movement added.",
    "saradomin": "> Call upon the divine grace of Saradomin to instantly complete your current quest and receive double the rewards",
    "zamorak": "> Activate this effect to shuffle all teams' current quests, but quests will be drawn at will from all rune levels. May the power of Zamorak be in your favor as your quest will roll 1 difficulty tier lower than your current quest.",
    "seren": "> Call upon Seren for divine intervention. Activate this effect to nullify the effects of a trap or negative event that has affected your team, ensuring a smoother journey through the game board. Seren's harmonious energy lingers, granting your team the ability to choose between 2 quests for the next turn.",
    "zaros": "> Channel the eldritch powers of Zaros to weave a web of trickery. Activate this effect to instantly swap your team's quest with another team's quest, but beware, for all progress on both quests is reset.",
    "guthix": "> Harness the wisdom of the forest and invoke the power of selective pruning. This divine intervention allows you to reroll your team's current task, aiming for a more manageable challenge. The rerolled task will have a rune tier one difficulty lower than the original, making it easier to achieve progress."
}
team_passive_long = {
    "tumeken": "> Members of the Tumekenian team are accustomed to the harsh desert environment. They receive a 50% bonus to GP earned when completing fire rune quests and all other quests in the desert. The radiant power of Tumeken, the god of the sun, illuminates your team's journey through the Lost Lands. When landing on a Glowing Rune tile, your team has a 25% chance to choose the effect of the rune's power.",
    "xeric": "> Followers of Xeric possess a deep understanding of magic. They receive a 25% discount on shop items' cost, allowing them to acquire items at a reduced price.",
    "bandos": "> When moving across the game board, there is a 10% chance that your team's sheer mass will cause runes to crack under your feet creating new Cracked Runes. Bandos' immense presence remains unshakable, impervious to any form of movement-altering effects within the game.",
    "armadyl": "> Armadylian devotees receive a 25% reduction to their quest length. They are blessed with swiftness and can complete tasks more efficiently.",
    "saradomin": "> Saradominists have the favor of the god of order. They have a 25% chance to avoid negative effects from traps and mend cracked runes completely nullifying the negative energy that embodies them.",
    "zamorak": "> The chaotic energies of Zamorak course through your team's veins, granting them a subtle yet potent advantage. When landing on a Glowing Rune, there is a 20% chance that a burst of Zamorakian energy will be unleashed. This energy surges through all runes of the same type where the cursed catalyst was released causing any team on those runes to reroll their current quest.",
    "seren": "> Serenists are known for their agility and grace. They receive a 10% chance to increase their movement range by 1, allowing them to cover more ground in each turn.",
    "zaros": "> Zarosian scholars possess ancient wisdom. They have a 10% chance of obtaining ancient relics when completing quests.",
    "guthix": "> Embrace the serenity of nature, channeling the spirit of Bob Ross' 'happy trees' to sprout lush trees on all enemy teams' tiles. To progress, each affected team must complete a unique 'Forest Guardians' quest associated with the newly grown trees. These quests may involve challenges ranging from air rune-level difficulty to skill-based or GP-related tasks.",
}
team_passives = {
    "bandos": "*Crushing Path*:\nWith each turn, have a 10% chance to create a new cracked rune and gain immunity to all movement-affecting effects.",
    "armadyl": "*Divine Grace*:\nQuests with multiple items are reduced by 25% (4 dragon meds becomes 3).",
    "tumeken": "*Desert Luminance*:\nEarn 50% more GP for completing fire rune quests while also having a 25% chance to select a glowing rune effect.",
    "xeric": "*Xeric's Wisdom*:\nEnjoy a 25% discount on shop items.",
    "saradomin": "*Holy Protection*:\nGain a 25% chance to nullify cracked runes and trap effects.",
    "zamorak": "*Cursed Catalyst*:\nHave a 20% chance to reroll all team's quests on a glowing rune.",
    "seren": "*Seren's Grace*:\nEnjoy a 10% chance to add +1 to your roll.",
    "zaros": "*Ancient Knowledge*:\nWhen completing quests, there is a 10% chance to receive a random item.",
    "guthix": "*Forest Guardians*:\nHave a 10% chance to add an Air Rune task to the current rune."
}
team_actives = {
    "bandos": "*Warstrike - 5 turn cooldown*:\nInstantly move all teams on the same rune type as Bandos back one tile.",
    "armadyl": "*Wings of Serenity - 6 turn cooldown*:\nAdd +2 to your next roll, gain immunity to traps for the next roll, and choose between two quests.",
    "tumeken": "*Solar Flare - 5 turn cooldown*:\nForce all teams ahead of Tumekenian to reroll their current quests.",
    "xeric": "*Great Olm's Blessing - 5 turn cooldown*:\nReceive a random shop item as a gift.",
    "saradomin": "*Zilyana's Grace - 6 turn cooldown*:\nInstantly complete a quest and earn double rewards.",
    "zamorak": "*Dark Disruption - 6 turn cooldown*:\nReroll all team's quests and reduce the difficulty by one level for Zamorakian quests.",
    "seren": "*Divine Intervention - 4 turn cooldown*:\nRemove all negative effects, gain immunity to traps, and choose between two quests for the next roll.",
    "zaros": "*Eldritch Manipulation - 4 turn cooldown*:\nSwap quests with another team (resets quest progress).",
    "guthix": "*Necessary Pruning - 5 turn cooldown*:\nReroll your current quest one difficulty lower."
}


item_definitions = {
    ## offensive items
    "gertrude's rat": {
        "emoji": ":Rat:1167108968951324692",
        "type": "o",
        "description": "Steal a random item from an enemy team's inventory.",
        "price": 6,
    },
    "pirate pete's parrot": {
        "emoji": ":Parrot:1167108966875148318",
        "type": "o",
        "description": "Steal 4-8 GP from an enemy team's inventory.",
        "price": 6,
    },
    "duplication glitch": {
        "emoji": ":dupeglitch:1162937831459663872",
        "type": "o",
        "description": "Assign your current task to an enemy team.",
        "price": 6,
    },
    # "questmaster's gauntlets": {
    #     "emoji": ":QuestmastersGauntlet:1167108968150216724",
    #     "type": "o",
    #     "description": "Steal an enemy team's quest and reroll them.",
    #     "price": 8,
    # },
    "mind goblin": {
        "emoji": ":MindGoblin:1167108965239373844",
        "type": "o",
        "description": "Choose an enemy team's quest.",
        "price": 10,
    },
    "blood tithe": {
        "emoji": ":bloodtithe:1162947504539701279",
        "type": "o",
        "description": "Move an enemy team back 1 tile, but your team moves back as well. Both team's quests are rerolled.",
        "price": 10,
    },
    "questmaster's gauntlets": {
        "emoji": ":QuestmastersGauntlet:1167108968150216724",
        "type": "o",
        "description": "Steal an enemy team's task, forcing them to re-roll in the process.",
        "price": 8,
    },
    "dragon spear": {
        "emoji": ":dspear:1162948200374747196",
        "type": "o",
        "description": "Move an enemy team forward or backward depending on your own team's position.",
        "price": 10,
    },
    "shadow barrage": {
        "emoji": ":shadowbarrage:1162948807684804729",
        "type": "o",
        "description": "Silences an enemy team from using items and abilities for 12 hours.",
        "price": 8,
    },
    "ice barrage": {
        "emoji": ":IceBarrage:1119686930255315055",
        "type": "o",
        "description": "Freeze an enemy team causing them to complete an additional quest after they're done with their current quest.",
        "price": 10,
    },
    ##defensive items
    "nieve's elysian": {
        "emoji": ":ely:1162949609056911572",
        "type": "d",
        "description": "Protect your team against items and abilities 1 time only.",
        "price": 10,
    },
    "ward of the leech": {
        "emoji": ":leech:1163141930822140005",
        "type": "d",
        "description": "Steal an enemy team's item when it's used on your team.",
        "price": 8,
    },
    "ward of mending": {
        "emoji": ":elidinisward:1163141286283456543",
        "type": "d",
        "description": "50% Chance to nullify Cracked Rune. MUST BE USED PRIOR TO LANDING ON ONE.",
        "price": 6,
    },
    "hunter's box traps": {
        "emoji": ":boxtrap:1163142310389887066",
        "type": "d",
        "description": "Protect your team against pests like Getrude's Rat.",
        "price": 6,
    },
    "barrelchest anchor": {
        "emoji": ":barrelchest:1163142813744103504",
        "type": "d",
        "description": "Protect your team against any movement-based items and abilities.",
        "price": 8,
    },
    "smoke barrage": {
        "emoji": ":smokebarrage:1163143244541071440",
        "type": "d",
        "description": "Hides your team from all targetable items and abilities.",
        "price": 8,
    },
    ##enchanted items
    "binding necklace": {
        "emoji": ":BindingNecklace:1119686932943867974",
        "type": "e",
        "description": "Roll 2 dice.",
        "price": 8,
    },
    "strange old man's spade": {
        "emoji": ":spade:1163180326609244211",
        "type": "e",
        "description": "Dig up a random item from the shop.",
        "price": 6,
    },
    # "rune scroll": {
    #     "emoji": ":rune_scroll:1163181564599996416",
    #     "type": "e",
    #     "description": "Receive an additional, random quest. Complete for 2x GP.",
    #     "price": 4,
    # },
    # "ancient rune": {
    #     "emoji": ":ancienttorva:1163181867944661063",
    #     "type": "e",
    #     "description": "Instantly complete your team's current quest.",
    #     "price": 12,
    # },
    "alchemist's blessing": {
        "emoji": ":alchemy:1163182326386282627",
        "type": "e",
        "description": "2x GP from your team's next quest completion.",
        "price": 4,
    },
    "lightbearer": {
        "emoji": ":lightbearer:1163182778901340302",
        "type": "e",
        "description": "Instantly reduce your team's active ability's cooldown by 50%.",
        "price": 10,
    },
    "ghommal's lucky penny": {
        "emoji": ":luckypenny:1163183111400607884",
        "type": "e",
        "description": "Instantly reroll your team's current quest.",
        "price": 6,
    },
    ## trap items
    "dinh's bulwark": {
        "emoji": ":DinhsBulwark:1119687103505248347",
        "type": "t",
        "description": "Blocks all teams from passing this rune until a quest is completed on it.",
        "price": 10,
    },
    # "teleportation tablet": {
    #     "emoji": ":teleport:1163183587554758746",
    #     "type": "t",
    #     "description": "Randomly teleport an enemy team (1-5 runes) forward or backward.",
    #     "price": 10,
    # },
    # "the mimic": {
    #     "emoji": ":mimic:1163183867885264916",
    #     "type": "t",
    #     "description": "Assign your current quest to the mimic and force any passing team to complete it.",
    #     "price": 10,
    # },
    # "hespori's vines": {
    #     "emoji": ":hespori:1163184154846973982",
    #     "type": "t",
    #     "description": "Blocks all teams from passing this rune and silences them from using items and abilities.",
    #     "price": 10,
    # },
    # "tumekenian's quicksand": {
    #     "emoji": "a:tumeksand:1163184621396176970",
    #     "type": "t",
    #     "description": "Moves the next passing team back 2 runes.",
    #     "price": 8,
    # }
}
