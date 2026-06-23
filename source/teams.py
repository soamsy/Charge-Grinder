# Burn
TEAMS = {
    "BURN": {
        "checks" : ["Burn", "smallBurn", (315, 370), "reBurn", "bigBurn", 0],
        "floors" : ["FlatbrokeGamblers", "toClaimTheirBones", "ACertainWorld", "HatredandDespair", "HellsChicken", "TobeCleaved"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2, "HatredandDespair": 3 },
        "upties": [
            {"hellterfly": 2},
            {"fiery": 2},
            {"glimpse": 4},
        ],
        "tiered_fusions": [
            {"glimpse": 4},   
        ],
        "strict_fusions": [
            {"book": { "paraffin": 1, "stew": 2 }},
            {"soothe": {"book": -1, "dust": 3, "ash": 1}},
        ],
        "buy"    : ["glimpse", "wing", "dust", "stew", "paraffin", "ash", "hellterfly", "fiery"], # order is important
        "all"    : ["glimpse", "dust", "stew", "paraffin", "ash", "book", "hellterfly", "fiery", "wing", "soothe", "disk"],
        "sin"    : True
    },

    "BLEED": {
        "checks" : ["Bleed", "smallBleed", (535, 370), "reBleed", "bigBleed", 0],
        "floors" : ["FlatbrokeGamblers", "toClaimTheirBones", "ACertainWorld", "HatredandDespair", "HellsChicken", "TobeCleaved"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2, "HatredandDespair": 3 },
        "upties": [
            {"clerid": 2},
            {"redstained": 4},
            {"gossypium": 2},
            {"muzzle": 1},
        ],
        "tiered_fusions": [
            {"redstained": 4},
            {"gossypium": 2},
        ],
        "strict_fusions": [
            {"devotion": {"millarca": 2, "hymn": 1} },
            {"redmist": {"devotion": None, "smokeswires": 3, "muzzle": 1}},
        ],
        "buy"    : ["redstained", "gossypium", "smokeswires", "millarca", "muzzle", "hymn", "contaminatedneedle", "fracturedblade", "scripture", "rustedknife", "clerid"],
        "all"    : ["clerid", "wolf", "devotion", "redmist", "redstained", "gossypium", "smokeswires", "millarca", "muzzle", "hymn", "contaminatedneedle", "fracturedblade", "scripture", "rustedknife"],
        "sin"    : True
    },

    "TREMOR": {
        "checks" : ["Tremor", "smallTremor", (755, 370), "reTremor", "bigTremor", 0],
        "floors" : ["FlatbrokeGamblers", "toClaimTheirBones", "ACertainWorld", "HatredandDespair", "HellsChicken", "TobeCleaved"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2, "HatredandDespair": 3 },
        "upties": [
            {"bracelet": 2},
            {"reverberation": 2},
            {"downpour": 4},
            {"truthbell": 3},
        ],
        "tiered_fusions": [
            {"downpour": 4},
            {"eyeball": 3},
        ],
        "strict_fusions": [
            {"oscillation": {"truthbell": 3, "cogs": 2, "nixie": 1}},
        ],
        "buy"    : ["downpour", "truthbell", "cogs", "nixie", "synaesthesia", "spanner", "clockwork", "biovial", "eyeball", "bracelet", "reverberation"],
        "all"    : ["oscillation", "bracelet", "reverberation", "downpour", "truthbell", "cogs", "nixie", "synaesthesia", "spanner", "clockwork", "biovial", "eyeball"],
        "sin"    : True
    },

    "RUPTURE": {
        "checks" : ["Rupture", "smallRupture", (975, 370), "reRupture", "bigRupture", 1],
        "floors" : ["FlatbrokeGamblers", "toClaimTheirBones", "ACertainWorld", "HatredandDespair", "HellsChicken", "TobeCleaved"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2, "HatredandDespair": 3 },
        "upties": [
            {"lamp": 2},
            {"thrill": 4},
            {"thunderbranch": 3},
            {"bundle": 1},
        ],
        "tiered_fusions": [
            {"thrill": 4},
            {"thunderbranch": 3},
        ],
        "strict_fusions": [
            {"trance": {"battery": 3, "rope": 2, "bundle": 1}},
        ],
        "buy"    : ["thrill", "breast", "thunderbranch", "battery", "rope", "bundle", "umbrella", "lamp"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance", "umbrella"],
        "sin"    : True
    },

    # Sinking
    "SINKING": {
        "checks" : ["Sinking", "smallSinking", (315, 665), "reSinking", "bigSinking", 0],
        "floors" : ["FlatbrokeGamblers", "toClaimTheirBones", "ACertainWorld", "HatredandDespair", "HellsChicken", "TobeCleaved"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2, "HatredandDespair": 3 },
        "upties": [
            {"redorder": 2},
            {"artisticsense": 4},
        ],
        "tiered_fusions": [
            {"artisticsense": 4},
        ],
        "strict_fusions": [
            {"musicsheet": {"midwinter": 3, "tangledbones": 2, "headlessportrait": 1}},
        ],
        "buy"    : ["musicsheet", "midwinter", "tangledbones", "headlessportrait", "compass", "crumbs", "meltedspring", "redorder"],
        "all"    : ["redorder", "meltedspring", "artisticsense", "musicsheet", "midwinter", "tangledbones", "headlessportrait", "compass", "crumbs"],
        "sin"    : True
    },

    # Poise
    "POISE": {
        "checks" : ["Poise", "smallPoise", (535, 665), "rePoise", "bigPoise", 1],
        "floors" : ["FlatbrokeGamblers", "toClaimTheirBones", "ACertainWorld", "HatredandDespair", "HellsChicken", "TobeCleaved"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2, "HatredandDespair": 3 },
        "upties": [
            {"stonetomb": 2},
            {"clearmirror": 4},
            {"nebulizer": 2},
            {"devil": 1},
        ],
        "tiered_fusions": [
            {"clearmirror": 4},
            {"nebulizer": 2},
        ],
        "strict_fusions": [
            {"reminiscence": {"recollection": 2, "pendant": 1}},
            {"luckypouch": {"reminiscence": -1, "clover": 3, "horseshoe": 1}},
        ],
        "buy"    : ["clearmirror", "nebulizer", "clover", "recollection", "pendant", "horseshoe", "bamboohat", "brokenblade", "finifugality", "devil"],
        "all"    : ["luckypouch", "stonetomb", "holder", "reminiscence", "clearmirror", "nebulizer", "clover", "recollection", "pendant", "horseshoe", "bamboohat", "brokenblade", "finifugality", "devil"],
        "sin"    : True
    },

    # Charge
    "CHARGE": {
        "checks" : ["Charge", "smallCharge", (755, 665), "reCharge", "bigCharge", 0],
        "floors" : ["FlatbrokeGamblers", "toClaimTheirBones", "ACertainWorld", "HatredandDespair", "HellsChicken", "TobeCleaved"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2, "HatredandDespair": 3 },
        "upties": [
            {"employeecard": 2},
            {"batterysocket": 2},
            {"gloves": 4},
            {"vitae": 1},
            {"wristguards": 1},
        ],
        "tiered_fusions": [
            {"gloves": 4},
        ],
        "strict_fusions": [
            {"T-1": {"forcefield": 3, "bolt": 2, "wristguards": 1}},
        ],
        "buy"    : ["gloves", "forcefield", "bolt", "wristguards", "imitativegenerator", "vitae", "employeecard", "batterysocket"],
        "all"    : ["employeecard", "batterysocket", "T-1", "gloves", "forcefield", "bolt", "wristguards", "imitativegenerator", "vitae"],
        "sin"    : True
    },

    "SLASH": {
        "checks" : ["Slash", "smallSlash", (975, 665), "reSlash", "bigSlash", 1],
        "floors" : ["FlatbrokeGamblers", "toClaimTheirBones", "ACertainWorld", "HatredandDespair", "HellsChicken", "TobeCleaved"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2, "HatredandDespair": 3 },
        "upties": [
            {"shortcane": 2},
            {"slashmemory": 4},
        ],
        "tiered_fusions": [
            {"slashmemory": 4},
        ],
        "strict_fusions": [],
        "buy"    : ["slashmemory"],
        "all"    : ["shortcane", "slashmemory"],
        "sin"    : False
    },

    "PIERCE": {
        "checks" : ["Pierce", "smallPierce", (315, 840), "rePierce", "bigPierce", 1],
        "floors" : ["FlatbrokeGamblers", "toClaimTheirBones", "ACertainWorld", "HatredandDespair", "HellsChicken", "TobeCleaved"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2, "HatredandDespair": 3 },
        "upties": [
            {"plumeproof": 2},
            {"piercememory": 4},
        ],
        "tiered_fusions": [
            {"piercememory": 4},
        ],
        "strict_fusions": [],
        "buy"    : ["piercememory"],
        "all"    : ["plumeproof", "piercememory"],
        "sin"    : False
    },

    "BLUNT": {
        "checks" : ["Blunt", "smallBlunt", (535, 840), "reBlunt", "bigBlunt", 0],
        "floors" : ["FlatbrokeGamblers", "toClaimTheirBones", "ACertainWorld", "HatredandDespair", "HellsChicken", "TobeCleaved"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2, "HatredandDespair": 3 },
        "upties": [
            {"bluntmemory": 4},
        ],
        "tiered_fusions": [
            {"bluntmemory": 4},
        ],
        "strict_fusions": [],
        "buy"    : ["bluntmemory"],
        "all"    : ["bluntmemory"],
        "sin"    : False
    },
}

# HARDMODE
HARD = {
    "BURN": {
        "checks" : ["Burn", "smallBurn", (315, 370), "reBurn", "bigBurn", 0],
        "floors" : ["FlatbrokeGamblers", "HatredandDespair", "HellsChicken", "Line3", "Line2", "The_BE", "Line1", "AbnormalSeismicZone"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2},
        "upties": [
            {"hellterfly": 2},
            {"fiery": 2},
            {"glimpse": 4},
            {"polarization": 1},
        ],
        "tiered_fusions": [
            {"glimpse": 4},   
        ],
        "strict_fusions": [
            {"book": { "paraffin": 1, "stew": 2 }},
            {"soothe": {"book": -1, "dust": 3, "ash": 1}},
            {"purloinedflame"  : {"disk": 3, "hearthflame": 2, "intellect": 1}},
        ],
        "buy"    : ["glimpse", "wing", "dust", "stew", "paraffin", "ash", "disk", "hearthflame", "intellect", "hellterfly", "fiery"], # order is important
        "all"    : ["glimpse", "dust", "stew", "paraffin", "ash", "book", "hellterfly", "fiery", "wing", "soothe",
                    "purloinedflame", "disk", "hearthflame", "intellect", "polarization"],
        "sin"    : True
    },
    "BLEED": {
        "checks" : ["Bleed", "smallBleed", (535, 370), "reBleed", "bigBleed", 0],
        "floors" : ["FlatbrokeGamblers", "HatredandDespair", "HellsChicken", "Line3", "Line2", "The_BE", "Line1", "AbnormalSeismicZone"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2},
        "upties": [
            {"clerid": 2},
            {"redstained": 4},
            {"gossypium": 2},
            {"muzzle": 1},
        ],
        "tiered_fusions": [
            {"redstained": 4},
            {"gossypium": 2},
        ],
        "strict_fusions": [
            {"devotion": {"millarca": 2, "hymn": 1} },
            {"redmist": {"devotion": None, "smokeswires": 3, "muzzle": 1}},
            {"hemorrhagicshock": {"bloodsack": 3, "rustedknife": 3, "ironstake": 1}},
        ],
        "buy"    : ["redstained", "gossypium", "smokeswires", "millarca", "muzzle", "hymn", "bloodsack", "rustedknife", "ironstake", "contaminatedneedle", "fracturedblade", "scripture", "clerid"],
        "all"    : ["clerid", "wolf", "devotion", "redmist", "redstained", "gossypium", "smokeswires", "millarca", "muzzle", "hymn", "contaminatedneedle", 
                    "fracturedblade", "scripture", "hemorrhagicshock", "rustedknife", "bloodsack", "ironstake"],
        "sin"    : True
    },

    "TREMOR": {
        "checks" : ["Tremor", "smallTremor", (755, 370), "reTremor", "bigTremor", 0],
        "floors" : ["FlatbrokeGamblers", "HatredandDespair", "HellsChicken", "Line3", "Line2", "The_BE", "Line1", "AbnormalSeismicZone"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2},
        "upties": [
            {"bracelet": 2},
            {"reverberation": 2},
            {"downpour": 4},
            {"truthbell": 3},
        ],
        "tiered_fusions": [
            {"downpour": 4},
            {"eyeball": 3},
        ],
        "strict_fusions": [
            {"oscillation": {"truthbell": 3, "cogs": 2, "nixie": 1}},
            {"epicenter": {"wobblingkeg": 2, "gemstone": 1}},
            {"vibrobell": {"epicenter": None, "clockwork": 3, "venomousskin": 1}}
        ],
        "buy"    : ["downpour", "truthbell", "cogs", "nixie", "clockwork", "wobblingkeg", "gemstone", "venomousskin", "synaesthesia", "spanner", "biovial", "eyeball", "bracelet", "reverberation"],
        "all"    : ["oscillation", "bracelet", "reverberation", "downpour", "truthbell", "cogs", "nixie", "synaesthesia", "spanner", 
                    "clockwork", "biovial", "eyeball", "vibrobell", "epicenter", "venomousskin", "wobblingkeg", "gemstone"],
        "sin"    : True
    },

    "RUPTURE": {
        "checks" : ["Rupture", "smallRupture", (975, 370), "reRupture", "bigRupture", 1],
        "floors" : ["FlatbrokeGamblers", "HatredandDespair", "HellsChicken", "Line3", "Line2", "The_BE", "Line1", "AbnormalSeismicZone"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2},
        "upties": [
            {"lamp": 2},
            {"thrill": 4},
            {"thunderbranch": 3},
            {"bundle": 1},
        ],
        "tiered_fusions": [
            {"thrill": 4},
            {"thunderbranch": 3},
        ],
        "strict_fusions": [
            {"trance": {"battery": 3, "rope": 2, "bundle": 1}},
            {"effigy": {"apocalypse": 2, "bonestake": 1}},
            {"ruin": {"effigy": -1, "thunderbranch": 3, "gun": 1}},
        ],
        "buy"    : ["thrill", "breast", "thunderbranch", "battery", "rope", "apocalypse", "bundle", "bonestake", "gun", "umbrella", "lamp"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance", "umbrella",
                    "ruin", "effigy", "gun", "apocalypse", "bonestake"],
        "sin"    : True
    },

    # Sinking
    "SINKING": {
        "checks" : ["Sinking", "smallSinking", (315, 665), "reSinking", "bigSinking", 0],
        "floors" : ["FlatbrokeGamblers", "HatredandDespair", "HellsChicken", "Line3", "Line2", "The_BE", "Line1", "AbnormalSeismicZone"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2},
        "upties": [
            {"redorder": 2},
            {"artisticsense": 4},
        ],
        "tiered_fusions": [
            {"artisticsense": 4},
        ],
        "strict_fusions": [
            {"musicsheet": {"midwinter": 3, "tangledbones": 2, "headlessportrait": 1}},
            {"globe": {"overcoat": 2, "cantabile": 1}},
            {"wave": {"globe": -1, "distantstar": 3, "thornypath": 1}},
        ],
        "buy"    : ["musicsheet", "midwinter", "tangledbones", "headlessportrait", "distantstar", "overcoat", "cantabile", "thornypath", "compass", "crumbs", "redorder"],
        "all"    : ["redorder", "meltedspring", "artisticsense", "musicsheet", "midwinter", "tangledbones", "headlessportrait", "compass", "crumbs",
                    "wave", "globe", "distantstar", "thornypath", "overcoat", "cantabile"],
        "sin"    : True
    },

    # Poise
    "POISE": {
        "checks" : ["Poise", "smallPoise", (535, 665), "rePoise", "bigPoise", 1],
        "floors" : ["FlatbrokeGamblers", "HatredandDespair", "HellsChicken", "Line3", "Line2", "The_BE", "Line1", "AbnormalSeismicZone"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2},
        "upties": [
            {"stonetomb": 2},
            {"clearmirror": 4},
            {"nebulizer": 2},
            {"devil": 1},
        ],
        "tiered_fusions": [
            {"clearmirror": 4},
            {"nebulizer": 2},
        ],
        "strict_fusions": [
            {"reminiscence": {"recollection": 2, "pendant": 1}},
            {"luckypouch": {"reminiscence": -1, "clover": 3, "horseshoe": 1}},
            {"spirits": {"endorphinkit": 3, "angel": 2, "devil": 1}},
        ],
        "buy"    : ["clearmirror", "nebulizer", "clover", "recollection", "pendant", "horseshoe", "endorphinkit", "angel", "devil", "bamboohat", "brokenblade", "finifugality"],
        "all"    : ["luckypouch", "stonetomb", "holder", "reminiscence", "clearmirror", "nebulizer", "clover", "recollection", "pendant", 
                    "horseshoe", "bamboohat", "brokenblade", "finifugality", "spirits", "endorphinkit", "angel", "devil"],
        "sin"    : True
    },

    # Charge
    "CHARGE": {
        "checks" : ["Charge", "smallCharge", (755, 665), "reCharge", "bigCharge", 0],
        "floors" : ["FlatbrokeGamblers", "HatredandDespair", "HellsChicken", "Line3", "Line2", "The_BE", "Line1", "AbnormalSeismicZone"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2},
        "upties": [
            {"employeecard": 2},
            {"batterysocket": 2},
            {"gloves": 4},
            {"vitae": 1},
            {"wristguards": 1},
        ],
        "tiered_fusions": [
            {"gloves": 4},
        ],
        "strict_fusions": [
            {"T-1": {"forcefield": 3, "bolt": 2, "wristguards": 1}},
            {"insulator": {"minitelepole": 2, "UPS": 1}},
            {"T-5": {"insulator": -1, "rod": 3, "vitae": 1}},
        ],
        "buy"    : ["gloves", "forcefield", "bolt", "wristguards", "minitelepole", "rod", "vitae", "UPS", "imitativegenerator", "employeecard", "batterysocket"],
        "all"    : ["employeecard", "batterysocket", "T-1", "gloves", "forcefield", "bolt", "wristguards", "imitativegenerator",
                    "T-5", "insulator", "rod", "vitae", "minitelepole", "UPS"],
        "sin"    : True
    },

    "SLASH": {
        "checks" : ["Slash", "smallSlash", (975, 665), "reSlash", "bigSlash", 1],
        "floors" : ["FlatbrokeGamblers", "HatredandDespair", "HellsChicken", "Line3", "Line2", "The_BE", "Line1", "AbnormalSeismicZone"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2},
        "upties": [
            {"shortcane": 2},
            {"slashmemory": 4},
        ],
        "tiered_fusions": [
            {"slashmemory": 4},
        ],
        "strict_fusions": [],
        "buy"    : ["slashmemory"],
        "all"    : ["shortcane", "slashmemory"],
        "sin"    : False
    },

    "PIERCE": {
        "checks" : ["Pierce", "smallPierce", (315, 840), "rePierce", "bigPierce", 1],
        "floors" : ["FlatbrokeGamblers", "HatredandDespair", "HellsChicken", "Line3", "Line2", "The_BE", "Line1", "AbnormalSeismicZone"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2},
        "upties": [
            {"plumeproof": 2},
            {"piercememory": 4},
        ],
        "tiered_fusions": [
            {"piercememory": 4},
        ],
        "strict_fusions": [],
        "buy"    : ["piercememory"],
        "all"    : ["plumeproof", "piercememory"],
        "sin"    : False
    },

    "BLUNT": {
        "checks" : ["Blunt", "smallBlunt", (535, 840), "reBlunt", "bigBlunt", 0],
        "floors" : ["FlatbrokeGamblers", "HatredandDespair", "HellsChicken", "Line3", "Line2", "The_BE", "Line1", "AbnormalSeismicZone"],
        "priority_floors" : {"FlatbrokeGamblers": 1, "HellsChicken": 2},
        "upties": [
            {"bluntmemory": 4},
        ],
        "tiered_fusions": [
            {"bluntmemory": 4},
        ],
        "strict_fusions": [],
        "buy"    : ["bluntmemory"],
        "all"    : ["bluntmemory"],
        "sin"    : False
    },
}

CUSTOM_TEAMS = {
    "SAIKAI": [{
        "checks" : ["Poise", "smallPoise", (535, 665), "rePoise", "bigPoise", 1],
        "upties": [
            {"stonetomb": 2},
            {"clearmirror": 4},
        ],
        "tiered_fusions": [
            {"clearmirror": 4},
        ],
        "strict_fusions": [],
        "buy"    : ["clearmirror", "nebulizer", "holder", "endorphinkit", "emerald"],
        "all"    : ["clearmirror", "nebulizer", "holder", "endorphinkit", "emerald"],
        "sin"    : True
    }, {
        "checks" : ["Burn", "smallBurn", (315, 370), "reBurn", "bigBurn", 0],
        "upties": [
            {"polarization": 1},
        ],
        "tiered_fusions": [],
        "strict_fusions": [],
        "buy"    : ["polarization"], # order is important
        "all"    : ["polarization"],
        "sin"    : True
    }
    ],
}

def DEFAULT_TEAM_MODS():
    mods = { i: {'saikai': True} for i in range(0, 15) }
    return mods

# from utils.paths import PTH
# for team in HARD.keys():
#     for gift in HARD[team]["all"]:
#         print(PTH[gift])