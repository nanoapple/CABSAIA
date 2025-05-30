# cabsaia/resources/emotion_dictionary.py

EMOTION_KEYWORDS = {
    "positive": [
        # 基础快乐情感
        "happy", "joy", "joyful", "cheerful", "delighted", "pleased", "content", "satisfied",
        "blissful", "ecstatic", "euphoric", "elated", "upbeat", "bright", "sunny", "radiant",
        "wonderful", "fantastic", "amazing", "awesome", "great", "excellent", "perfect",
        "marvelous", "spectacular", "brilliant", "outstanding", "superb", "fabulous",
        
        # 感激与祝福
        "grateful", "thankful", "blessed", "fortunate", "appreciative", "honored",
        "privileged", "lucky", "gifted", "favored", "special", "chosen",
        
        # 希望与乐观
        "hope", "hopeful", "optimistic", "positive", "encouraged", "inspired",
        "motivated", "determined", "resilient", "strong", "empowered", "uplifted",
        "renewed", "refreshed", "revitalized", "invigorated", "energized",
        
        # 平静与安全
        "calm", "peaceful", "relaxed", "serene", "tranquil", "comfortable", "cozy",
        "safe", "secure", "protected", "relieved", "at ease", "settled", "stable",
        "grounded", "centered", "balanced", "harmonious", "zen", "still",
        
        # 成就与自信
        "proud", "accomplished", "successful", "confident", "capable", "competent",
        "skilled", "talented", "gifted", "brilliant", "smart", "clever", "wise",
        "validated", "worthy", "valuable", "enough", "deserving", "important",
        
        # 爱与连接
        "loved", "supported", "understood", "accepted", "connected", "close",
        "belonging", "cherished", "cared for", "appreciated", "valued", "treasured",
        "adored", "beloved", "dear", "precious", "intimate", "bonded", "united",
        
        # 自由与解脱
        "free", "liberated", "released", "unburdened", "light", "weightless",
        "carefree", "spontaneous", "playful", "fun", "amusing", "entertaining",
        
        # 兴奋与热情
        "excited", "thrilled", "enthusiastic", "passionate", "eager", "keen",
        "pumped", "psyched", "stoked", "fired up", "charged", "buzzing"
    ],
    
    "negative": [
        # 基础悲伤情感
        "sad", "unhappy", "depressed", "melancholy", "gloomy", "miserable", "wretched",
        "heartbroken", "devastated", "crushed", "shattered", "broken", "torn",
        "grief", "grieving", "mourning", "sorrow", "sorrowful", "despair", "despairing",
        "hopeless", "despondent", "dejected", "downcast", "blue", "down", "low",
        "terrible", "awful", "horrible", "dreadful", "horrendous", "atrocious",
        "appalling", "ghastly", "hideous", "disgusting", "revolting", "repulsive",
        
        # 愤怒与仇恨
        "angry", "mad", "furious", "enraged", "livid", "irate", "incensed", "outraged",
        "rage", "wrath", "fury", "irritated", "annoyed", "frustrated", "agitated",
        "resentful", "bitter", "hostile", "aggressive", "violent", "vicious",
        "hate", "hatred", "loathe", "loathing", "despise", "detest", "abhor",
        "disgusted", "repulsed", "sickened", "nauseated", "revolted",
        
        # 焦虑与恐惧
        "anxious", "worried", "nervous", "scared", "afraid", "fearful", "terrified",
        "petrified", "horrified", "panicked", "frantic", "hysterical", "paranoid",
        "overwhelmed", "stressed", "tense", "uptight", "on edge", "jittery",
        "restless", "uneasy", "disturbed", "troubled", "concerned", "apprehensive",
        "dreading", "alarmed", "startled", "shocked", "stunned", "traumatized",
        
        # 羞耻与内疚
        "ashamed", "shameful", "guilty", "embarrassed", "humiliated", "mortified",
        "regretful", "remorseful", "self-conscious", "awkward", "uncomfortable",
        "inadequate", "inferior", "pathetic", "pitiful", "contemptible", "despicable",
        
        # 孤独与疏离
        "lonely", "alone", "isolated", "abandoned", "rejected", "excluded", "ostracized",
        "disconnected", "alienated", "estranged", "misunderstood", "invisible",
        "forgotten", "ignored", "neglected", "unwanted", "unloved", "unworthy",
        
        # 疲惫与绝望
        "tired", "exhausted", "drained", "burnt out", "weary", "fatigued", "depleted",
        "worn out", "spent", "finished", "done", "empty", "hollow", "void",
        "numb", "lifeless", "dead", "defeated", "powerless", "helpless", "useless",
        "worthless", "meaningless", "pointless", "hopeless", "doomed", "lost",
        
        # 痛苦与折磨
        "hurt", "hurting", "pain", "painful", "agonizing", "excruciating", "unbearable",
        "suffering", "tormented", "tortured", "anguished", "distressed", "distraught",
        "devastated", "ruined", "destroyed", "damaged", "scarred", "wounded",
        
        # 失望与挫折
        "disappointed", "let down", "discouraged", "disheartened", "deflated",
        "frustrated", "blocked", "stuck", "trapped", "confined", "imprisoned",
        "limited", "restricted", "constrained", "suffocated", "stifled"
    ],
    
    "arousal_high": [
        # 积极高唤醒
        "excited", "thrilled", "elated", "ecstatic", "euphoric", "exhilarated",
        "energized", "pumped", "enthusiastic", "passionate", "intense", "wild",
        "crazy", "insane", "incredible", "unbelievable", "mind-blowing",
        "electrifying", "explosive", "dynamic", "vibrant", "alive", "buzzing",
        
        # 消极高唤醒
        "furious", "enraged", "livid", "irate", "incensed", "outraged", "raging",
        "panicked", "frantic", "hysterical", "frenzied", "manic", "chaotic",
        "agitated", "worked up", "wound up", "keyed up", "wired", "jacked up",
        "overwhelmed", "terrified", "petrified", "horrified", "traumatized",
        "desperate", "urgent", "critical", "extreme", "severe", "intense",
        
        # 中性高唤醒
        "shocked", "stunned", "amazed", "astonished", "astounded", "flabbergasted",
        "surprised", "startled", "jolted", "shaken", "rattled", "disturbed"
    ],
    
    "arousal_low": [
        # 积极低唤醒
        "calm", "peaceful", "serene", "tranquil", "quiet", "still", "gentle",
        "content", "satisfied", "comfortable", "cozy", "relaxed", "restful",
        "soothing", "mellow", "soft", "tender", "sweet", "pleasant", "nice",
        "at ease", "centered", "balanced", "grounded", "stable", "settled",
        
        # 消极低唤醒
        "sad", "melancholy", "blue", "down", "low", "dejected", "discouraged",
        "disappointed", "resigned", "defeated", "hopeless", "despairing",
        "apathetic", "indifferent", "bored", "dull", "flat", "lifeless",
        "listless", "lethargic", "sluggish", "slow", "heavy", "weighed down",
        "withdrawn", "detached", "distant", "remote", "disconnected",
        "numb", "empty", "hollow", "void", "blank", "nothing"
    ],
    
    "dominant": [
        # 积极支配
        "confident", "assertive", "determined", "strong", "powerful", "mighty",
        "in control", "controlling", "commanding", "authoritative", "leading",
        "decisive", "firm", "resolute", "bold", "courageous", "brave", "fearless",
        "independent", "self-reliant", "autonomous", "capable", "competent",
        "skilled", "talented", "superior", "dominant", "winning", "victorious",
        
        # 消极支配
        "aggressive", "hostile", "violent", "brutal", "cruel", "vicious",
        "dominating", "oppressive", "tyrannical", "dictatorial", "demanding",
        "pushy", "forceful", "coercive", "intimidating", "threatening",
        "defiant", "rebellious", "stubborn", "obstinate", "rigid", "inflexible"
    ],
    
    "submissive": [
        # 积极顺从
        "accepting", "trusting", "cooperative", "agreeable", "compliant",
        "flexible", "adaptable", "open", "receptive", "willing", "eager",
        "humble", "modest", "gentle", "kind", "caring", "nurturing",
        
        # 消极顺从
        "helpless", "powerless", "weak", "vulnerable", "fragile", "delicate",
        "dependent", "needy", "clingy", "submissive", "passive", "meek",
        "defeated", "resigned", "giving up", "surrendering", "victimized",
        "oppressed", "abused", "exploited", "used", "manipulated",
        "trapped", "stuck", "paralyzed", "frozen", "immobilized",
        "overwhelmed", "crushed", "broken", "shattered", "destroyed"
    ],
    
    "trauma_related": [
        "triggered", "flashback", "reliving", "re-experiencing", "haunted",
        "dissociated", "dissociation", "detached", "disconnected", "spaced out",
        "numb", "frozen", "paralyzed", "shut down", "checked out",
        "hypervigilant", "on guard", "alert", "watchful", "suspicious",
        "on edge", "jumpy", "startled", "scared", "terrified", "petrified",
        "unsafe", "threatened", "endangered", "vulnerable", "exposed",
        "violated", "invaded", "attacked", "assaulted", "abused",
        "betrayed", "abandoned", "rejected", "discarded", "thrown away",
        "traumatized", "scarred", "damaged", "broken", "shattered",
        "nightmares", "sleepless", "insomnia", "avoidant", "avoiding"
    ],
    
    "interpersonal": [
        # 连接感
        "connected", "close", "intimate", "bonded", "united", "together",
        "understood", "heard", "seen", "recognized", "acknowledged",
        "accepted", "welcomed", "included", "belonging", "part of",
        "supported", "backed", "encouraged", "cheered", "celebrated",
        "loved", "adored", "cherished", "treasured", "valued", "appreciated",
        
        # 疏离感
        "disconnected", "distant", "remote", "far", "separate", "apart",
        "isolated", "alone", "lonely", "abandoned", "deserted", "left out",
        "excluded", "rejected", "unwanted", "unwelcome", "outcast",
        "misunderstood", "unheard", "unseen", "invisible", "ignored",
        "neglected", "forgotten", "overlooked", "dismissed", "discounted",
        
        # 冲突与背叛
        "betrayed", "deceived", "lied to", "cheated", "used", "exploited",
        "manipulated", "controlled", "dominated", "oppressed", "abused",
        "hurt", "wounded", "damaged", "scarred", "broken", "shattered",
        "conflicted", "torn", "divided", "split", "ambivalent", "confused",
        "uncertain", "doubtful", "suspicious", "distrustful", "wary",
        
        # 嫉妒与竞争
        "jealous", "envious", "resentful", "bitter", "spiteful", "vindictive",
        "competitive", "rival", "opponent", "enemy", "adversary", "hostile"
    ],
    
    "somatic": [
        # 紧张与放松
        "tense", "tight", "rigid", "stiff", "cramped", "knotted", "clenched",
        "relaxed", "loose", "soft", "flexible", "fluid", "flowing", "open",
        
        # 能量状态
        "energized", "charged", "electric", "buzzing", "vibrating", "alive",
        "drained", "depleted", "exhausted", "fatigued", "weary", "tired",
        "heavy", "weighed down", "sluggish", "slow", "lethargic", "lifeless",
        "light", "weightless", "floating", "airy", "buoyant", "elevated",
        
        # 温度感受
        "warm", "hot", "burning", "feverish", "heated", "inflamed",
        "cold", "chilly", "freezing", "icy", "frozen", "numb",
        
        # 运动状态
        "restless", "fidgety", "agitated", "jittery", "shaky", "trembling",
        "still", "calm", "peaceful", "quiet", "motionless", "frozen",
        
        # 身体症状
        "sick", "ill", "unwell", "nauseous", "queasy", "dizzy", "lightheaded",
        "breathless", "suffocating", "choking", "gasping", "panting",
        "heart racing", "pounding", "thumping", "beating fast", "palpitations",
        "sweaty", "clammy", "moist", "dry", "parched", "thirsty"
    ],
    
    "self_worth": [
        # 积极自我价值
        "worthy", "valuable", "precious", "important", "significant", "special",
        "unique", "one of a kind", "irreplaceable", "priceless", "treasured",
        "enough", "good enough", "sufficient", "adequate", "satisfactory",
        "deserving", "entitled", "worthy of love", "lovable", "likeable",
        "acceptable", "okay", "fine", "good", "great", "wonderful",
        "capable", "competent", "skilled", "talented", "gifted", "brilliant",
        "smart", "intelligent", "wise", "clever", "creative", "artistic",
        
        # 消极自我价值
        "worthless", "valueless", "meaningless", "insignificant", "unimportant",
        "useless", "pointless", "waste of space", "burden", "liability",
        "inadequate", "insufficient", "not enough", "lacking", "deficient",
        "flawed", "imperfect", "broken", "damaged", "defective", "faulty",
        "unlovable", "unworthy", "undeserving", "not good enough",
        "failure", "loser", "reject", "outcast", "misfit", "freak",
        "stupid", "dumb", "ignorant", "foolish", "idiotic", "moronic",
        "ugly", "hideous", "disgusting", "repulsive", "revolting",
        "fat", "gross", "nasty", "dirty", "filthy", "contaminated",
        "pathetic", "pitiful", "contemptible", "despicable", "shameful"
    ],
    
    "existential": [
        # 意义与目的
        "purposeful", "meaningful", "significant", "important", "worthwhile",
        "fulfilling", "satisfying", "rewarding", "enriching", "valuable",
        "authentic", "genuine", "real", "true", "honest", "sincere",
        "connected", "grounded", "rooted", "centered", "balanced",
        
        # 空虚与迷失
        "empty", "hollow", "void", "vacant", "blank", "nothing",
        "meaningless", "pointless", "senseless", "absurd", "ridiculous",
        "purposeless", "aimless", "directionless", "wandering", "drifting",
        "lost", "confused", "bewildered", "perplexed", "puzzled",
        "searching", "seeking", "looking for", "questioning", "wondering",
        "doubting", "uncertain", "unsure", "unclear", "ambiguous",
        "fake", "false", "artificial", "pretending", "acting", "mask"
    ],
    
    "growth_change": [
        # 成长与进步
        "growing", "developing", "evolving", "progressing", "advancing",
        "improving", "getting better", "healing", "recovering", "mending",
        "transforming", "changing", "shifting", "moving", "flowing",
        "learning", "understanding", "realizing", "discovering", "exploring",
        "expanding", "stretching", "reaching", "striving", "pushing",
        "ready", "prepared", "willing", "open", "receptive", "eager",
        
        # 停滞与阻抗
        "stuck", "trapped", "imprisoned", "confined", "limited", "restricted",
        "stagnant", "static", "unchanging", "same", "repetitive", "circular",
        "blocked", "obstructed", "hindered", "prevented", "stopped",
        "resistant", "reluctant", "unwilling", "closed", "stubborn",
        "afraid of change", "scared", "terrified", "paralyzed", "frozen",
        "regressing", "going backwards", "deteriorating", "worsening"
    ]
}

# 情感强度等级 - 大幅扩展
EMOTION_INTENSITY = {
    "minimal": ["barely", "hardly", "scarcely", "slightly", "faintly", "vaguely"],
    "mild": ["a bit", "a little", "somewhat", "mildly", "gently", "softly", "lightly"],
    "moderate": ["pretty", "quite", "fairly", "moderately", "reasonably", "considerably"],
    "strong": ["very", "really", "truly", "genuinely", "seriously", "significantly"],
    "intense": ["extremely", "incredibly", "immensely", "tremendously", "intensely", "deeply"],
    "extreme": ["completely", "totally", "absolutely", "utterly", "entirely", "wholly"],
    "severe": ["devastatingly", "overwhelmingly", "crushingly", "unbearably", "intolerably"]
}

# 情感表达方式 - 大幅扩展
EMOTION_EXPRESSIONS = {
    "direct": [
        "I feel", "I am", "I'm feeling", "I'm", "feeling", "I experience",
        "I have", "I get", "I sense", "I notice", "I realize", "I recognize"
    ],
    "indirect": [
        "it's like", "seems like", "kind of", "sort of", "maybe", "perhaps",
        "I think", "I believe", "I suppose", "I guess", "it feels like",
        "there's a sense of", "I have this feeling", "something tells me"
    ],
    "somatic": [
        "in my body", "physically", "I notice", "I sense", "feels in my",
        "my body feels", "I can feel it in", "physically I", "somatically",
        "in my chest", "in my stomach", "in my throat", "in my head"
    ],
    "metaphorical": [
        "like", "as if", "reminds me of", "it's similar to", "feels like",
        "imagine", "picture", "it's as though", "comparable to", "analogous to"
    ],
    "temporal": [
        "always", "never", "sometimes", "often", "rarely", "frequently",
        "constantly", "continuously", "occasionally", "periodically",
        "right now", "at this moment", "currently", "lately", "recently"
    ]
}

# 常见心理咨询主题关键词 - 大幅扩展
COUNSELING_THEMES = {
    "depression": [
        "depressed", "depression", "sad", "sadness", "hopeless", "hopelessness",
        "empty", "emptiness", "worthless", "worthlessness", "tired", "fatigue",
        "unmotivated", "no energy", "can't get out of bed", "nothing matters",
        "dark", "darkness", "black hole", "pit", "heavy", "weight", "burden",
        "numb", "numbness", "lifeless", "dead inside", "broken", "shattered"
    ],
    
    "anxiety": [
        "anxious", "anxiety", "worried", "worry", "nervous", "nervousness",
        "panicked", "panic", "overwhelmed", "stressed", "stress", "fearful",
        "fear", "scared", "afraid", "terrified", "terror", "dread", "dreading",
        "racing thoughts", "can't stop thinking", "catastrophizing", "what if",
        "worst case scenario", "heart racing", "can't breathe", "sweating"
    ],
    
    "trauma": [
        "trauma", "traumatic", "triggered", "trigger", "flashback", "nightmares",
        "unsafe", "danger", "threatened", "violated", "attacked", "assaulted",
        "abused", "abuse", "violence", "violent", "hypervigilant", "on guard",
        "dissociated", "dissociation", "numb", "frozen", "paralyzed", "stuck",
        "memories", "haunted", "can't forget", "reliving", "re-experiencing"
    ],
    
    "relationships": [
        "relationship", "partner", "spouse", "husband", "wife", "boyfriend",
        "girlfriend", "family", "parents", "mother", "father", "siblings",
        "friends", "friendship", "conflict", "fight", "argument", "disagreement",
        "communication", "talking", "listening", "understanding", "boundaries",
        "trust", "betrayal", "cheating", "infidelity", "divorce", "breakup",
        "love", "hate", "intimacy", "sex", "attraction", "connection"
    ],
    
    "self_esteem": [
        "self-esteem", "self-worth", "confidence", "self-confidence", "inadequate",
        "not enough", "not good enough", "perfectionism", "perfectionist",
        "comparison", "comparing", "self-criticism", "self-critical", "harsh",
        "inner critic", "negative self-talk", "put myself down", "beat myself up",
        "failure", "failing", "success", "achievement", "approval", "validation"
    ],
    
    "grief": [
        "grief", "grieving", "loss", "losing", "death", "died", "dying",
        "funeral", "cemetery", "grave", "mourning", "mourn", "miss", "missing",
        "gone", "left", "goodbye", "farewell", "end", "ending", "over",
        "memories", "remember", "remembering", "honor", "tribute", "legacy"
    ],
    
    "addiction": [
        "addiction", "addicted", "substance", "alcohol", "drinking", "drunk",
        "drugs", "using", "high", "wasted", "sober", "sobriety", "clean",
        "craving", "crave", "need", "want", "urge", "temptation", "relapse",
        "recovery", "recovering", "rehabilitation", "rehab", "treatment", "help",
        "control", "out of control", "powerless", "rock bottom", "intervention"
    ],
    
    "eating_disorders": [
        "eating", "food", "weight", "fat", "thin", "skinny", "body", "body image",
        "mirror", "appearance", "looks", "ugly", "disgusting", "calories",
        "diet", "dieting", "restrict", "binge", "purge", "vomit", "exercise",
        "control", "obsessed", "compulsive", "anorexia", "bulimia", "disorder"
    ],
    
    "work_stress": [
        "work", "job", "career", "boss", "manager", "supervisor", "coworker",
        "colleague", "office", "workplace", "pressure", "stress", "deadline",
        "overtime", "burnout", "burned out", "workload", "responsibility",
        "performance", "evaluation", "promotion", "fired", "quit", "resign"
    ],
    
    "identity": [
        "identity", "who am I", "who I am", "sense of self", "authentic",
        "real self", "true self", "fake", "pretending", "acting", "mask",
        "role", "expectations", "should", "supposed to", "conformity",
        "different", "unique", "special", "normal", "fit in", "belong",
        "acceptance", "rejection", "judgment", "criticized", "approved"
    ]
}

# 新增：情感组合模式
EMOTION_COMBINATIONS = {
    "mixed_feelings": [
        "mixed feelings", "conflicted", "torn", "ambivalent", "confused",
        "don't know how to feel", "part of me", "on one hand", "but also"
    ],
    "emotional_numbness": [
        "numb", "nothing", "empty", "void", "blank", "hollow", "dead inside",
        "can't feel", "no emotions", "shut down", "disconnected", "detached"
    ],
    "emotional_overwhelm": [
        "overwhelmed", "too much", "can't handle", "drowning", "suffocating",
        "intense", "powerful", "strong", "flooding", "overloaded", "maxed out"
    ]
}

# 新增：情感变化模式
EMOTION_TRANSITIONS = {
    "improving": [
        "getting better", "feeling better", "improving", "progress", "healing",
        "recovery", "moving forward", "growing", "stronger", "lighter"
    ],
    "worsening": [
        "getting worse", "deteriorating", "declining", "spiraling", "downward",
        "darker", "heavier", "more intense", "escalating", "deepening"
    ],
    "fluctuating": [
        "up and down", "roller coaster", "back and forth", "changing", "shifting",
        "unstable", "unpredictable", "waves", "cycles", "patterns", "episodes"
    ]
}