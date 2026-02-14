# cabsaia/processing/context_negators.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable, Set


# -----------------------------------------------------------------------------
# 0) 词表（保留你同事的结构：category -> phrases）
#    建议：先直接把你同事的 CONTEXT_NEGATORS dict 粘贴到这里（原样）
# -----------------------------------------------------------------------------
CONTEXT_NEGATORS: Dict[str, List[str]] = {
    # =========================================================================
    # 1. 指控虚伪 / 质疑真实性 (Accusation of Inauthenticity)
    # 心理学原理：信任破裂、偏执意念、早期关系创伤中的背叛图式
    # 常见于：治疗联盟破裂、AI对话中的"你只是机器"时刻
    # =========================================================================
    "accusation_of_inauthenticity": [
        # 原始
        "mask", "masking", "pretend", "fake", "lying", "liar",
        # 直接指控
        "phony", "two-faced", "hypocrite", "fraud", "deceive",
        "you're full of it", "full of shit", "bullshit",
        "don't believe you", "don't buy it",
        "that's a lie", "you're making that up",
        "stop lying", "stop pretending",
        # 质疑动机/真诚度
        "you don't really", "you don't actually",
        "just saying that", "you're just pretending",
        "you don't mean that", "you're just being nice",
        "you're only saying that because",
        "you have to say that", "that's what you're trained to say",
        # AI 特有
        "you're programmed to", "you don't actually care",
        "you're just a machine", "you're not real",
        "you can't understand", "you'll never understand",
        "you have no feelings", "you don't know what it's like",
        # 职场
        "corporate speak", "PR answer", "that's just HR talk",
        "you're just covering yourself", "just checking a box",
        "performative", "virtue signaling",
    ],

    # =========================================================================
    # 2. 拒绝沟通 / 关闭对话 (Communication Shutdown)
    # 心理学原理：回避型依附、情绪过载后的保护性关闭
    # Gottman: 石墙 (Stonewalling) 的核心表现
    # =========================================================================
    "communication_shutdown": [
        # 原始
        "not talking to you", "i dont want", "i don't want",
        # 明确拒绝
        "leave me alone", "go away", "shut up", "stop talking",
        "don't talk to me", "i said no", "stop",
        "enough", "i'm done", "i'm done talking",
        "end of discussion", "conversation over",
        "this discussion is over", "i have nothing to say",
        "there's nothing to talk about", "drop it",
        # 回避/推开
        "stop asking", "stop bringing it up",
        "forget it", "forget about it", "just forget it",
        "none of your business", "why do you care",
        "doesn't matter", "it's not important",
        "i don't want to talk about it", "not now",
        "can we not", "i'm not in the mood",
        "not this again", "here we go again",
        # 贬低对话价值
        "it's pointless", "what's the point",
        "why bother", "talking to a wall",
        "waste of time", "waste my time",
        "not listening", "i'm not listening",
        "talking in circles", "going nowhere",
        # 职场特有
        "take it offline", "let's move on",
        "noted", "i'll take that on board",
        "let's table this", "we've covered this",
        "let's agree to disagree", "i hear you but",
        "that's above my pay grade",
    ],

    # =========================================================================
    # 3. 归咎 / 推卸责任 (Blame-Shifting / Externalization)
    # 心理学原理：外化归因、自恋防御、受害者身份固化
    # 常见于：伴侣冲突、家庭治疗、职场纠纷
    # =========================================================================
    "blame_shifting": [
        # 原始
        "your fault", "you always", "you never",
        # 直接归咎
        "you caused this", "you made me",
        "you did this", "because of you",
        "blame you", "thanks to you",
        "you ruined", "you destroyed",
        "this is on you", "look what you did",
        "if you hadn't", "if it weren't for you",
        "you're the reason", "you're the problem",
        "you started it", "you provoked me",
        "you drove me to this", "you pushed me",
        "you left me no choice", "what did you expect",
        # 伴侣关系特有
        "if you loved me you would", "a real man would",
        "a real woman would", "my ex never did this",
        "my ex was better", "my mother was right about you",
        "you've changed", "you're not the person i married",
        "you don't love me anymore", "you never loved me",
        "you care more about your work", "you care more about your friends",
        # 职场特有
        "that wasn't in my brief", "nobody told me",
        "i wasn't informed", "that's not my job",
        "i was just following orders", "management's fault",
        "if i had been given the resources",
        "the requirements kept changing",
        "i was set up to fail",
    ],

    # =========================================================================
    # 4. 绝对化 / 全或无思维 (Absolutist / All-or-Nothing Thinking)
    # 心理学原理：Beck 认知扭曲、BPD 分裂机制、抑郁性思维
    # 红旗信号：这类语言密度增加与自杀风险相关 (Al-Mosaiwi, 2018)
    # =========================================================================
    "absolutist_thinking": [
        # 原始
        "everyone", "no one", "nobody",
        # 关于世界
        "nothing works", "everything is ruined",
        "always like this", "never changes", "every time",
        "all the same", "none of this matters",
        "there's no point", "nothing ever works",
        "it's all useless", "the world is",
        "people are all", "you can't trust anyone",
        # 关于自己
        "always my fault", "i always mess up",
        "i never get it right", "i can't do anything",
        "everything i touch", "i always end up alone",
        "nobody ever stays", "no one has ever",
        # 关于关系
        "nobody cares", "no one understands",
        "no one listens", "everyone leaves",
        "everyone hates me", "everyone's against me",
        "all men are", "all women are",
        "relationships never work", "love doesn't exist",
        "trust no one", "people only care about themselves",
        # 关于未来
        "it will always be like this", "nothing will ever change",
        "i'll never be happy", "it's never going to work",
        "this always happens to me",
    ],

    # =========================================================================
    # 5. 自我贬低 / 无价值感 (Self-Deprecation / Worthlessness)
    # 心理学原理：核心信念激活、内化的羞耻、抑郁认知三角
    # [escalation] 某些表达需要自杀风险评估
    # =========================================================================
    "self_deprecation": [
        # 核心无价值
        "i'm worthless", "i'm useless", "i'm a burden",
        "i'm nothing", "i don't matter", "i'm broken",
        "i'm a failure", "can't do anything right",
        "i'm stupid", "i'm pathetic", "i'm hopeless",
        "i deserve this", "i'm not good enough",
        "what's wrong with me", "i hate myself",
        "i'm disgusting", "i'm unlovable",
        "i'm a waste of space", "i'm a mistake",
        "i shouldn't have been born",
        # 关系中的无价值
        "you deserve better", "you'd be better off without me",
        "why are you even with me", "i don't deserve you",
        "i don't deserve love", "i don't deserve to be happy",
        "i'll only drag you down", "i ruin everything",
        "everyone who gets close to me gets hurt",
        # [escalation] 高风险表达
        "no one would miss me", "better off without me",
        "the world would be better without me",
        "what's the point of being alive",
        "i wish i didn't exist", "i wish i wasn't here",
        "i don't want to be here anymore",
    ],

    # =========================================================================
    # 6. 无助 / 习得性无助 (Helplessness / Learned Helplessness)
    # 心理学原理：Seligman 习得性无助模型、创伤后无力感
    # 常见于：长期受虐、慢性疾病、职场霸凌
    # =========================================================================
    "helplessness": [
        "nothing will change", "there's no hope",
        "it's too late", "can't be fixed", "beyond repair",
        "what's the use", "i give up", "i've given up",
        "no way out", "stuck forever", "trapped",
        "it'll never get better", "doomed", "hopeless",
        "why even try", "no matter what i do",
        "i've tried everything", "nothing helps",
        "it's been like this forever", "it's just who i am",
        "can't change", "people don't change",
        "it's in my nature", "born this way",
        "what's meant to be", "it's fate",
        # 外部无助
        "the system is broken", "there's no justice",
        "the deck is stacked", "rigged",
        "no one will help", "no one cares enough to help",
        "it doesn't matter what i say",
    ],

    # =========================================================================
    # 7. 情绪升级 / 愤怒爆发 (Emotional Escalation / Anger)
    # 心理学原理：杏仁核劫持、战或逃反应、愤怒作为二级情绪
    # [escalation] 可能需要去激活化或安全评估
    # =========================================================================
    "emotional_escalation": [
        # 言语攻击
        "i hate you", "fuck you", "fuck off", "screw you",
        "piss off", "go to hell", "you're useless",
        "you suck", "you're worthless", "you're pathetic",
        "you disgust me", "i can't stand you",
        "i despise you", "drop dead",
        # 情绪失控表达
        "i'm so angry", "i'm furious", "i can't take this",
        "i'm losing it", "i'm gonna explode",
        "i'm about to lose my shit", "i'm seeing red",
        "i'm done with you", "i'm done with everything",
        "i can't take it anymore", "i've had enough",
        # 威胁性语言
        "don't push me", "back off", "don't test me",
        "you'll regret this", "you'll be sorry",
        "watch yourself", "try me",
        "you have no idea what i'm capable of",
        # 职场特有
        "this is unacceptable", "i will escalate this",
        "i'm going to HR", "i'm talking to your manager",
        "you'll hear from my lawyer",
        "i'm going above your head",
    ],

    # =========================================================================
    # 8. 不信任 / 怀疑动机 (Distrust / Suspicion of Motives)
    # 心理学原理：偏执意念、不安全依附、背叛创伤
    # 常见于：复杂PTSD、边缘人格、被背叛后的关系
    # =========================================================================
    "distrust": [
        "ulterior motive", "what do you want from me",
        "you're using me", "you just want",
        "you only care about", "in it for yourself",
        "taking advantage", "don't trust you",
        "can't trust anyone", "everyone has an agenda",
        "you're not on my side", "whose side are you on",
        "you're against me", "you're working against me",
        "you're out to get me",
        "what's in it for you", "what's the catch",
        "too good to be true", "waiting for the other shoe to drop",
        "i know what you're doing", "i see right through you",
        "don't try to trick me", "i'm not falling for that",
        "you're just like everyone else",
        "i knew i couldn't trust you",
        "you'll just use it against me",
        "anything i say can and will",
        # 伴侣关系
        "who were you texting", "let me see your phone",
        "where were you really", "you're hiding something",
        "i know you're lying", "are you cheating",
        "you're being shady", "something's off",
        # 职场
        "they're talking about me", "i'm being watched",
        "setting me up", "throwing me under the bus",
        "taking credit for my work", "stabbed in the back",
        "office politics", "they want me out",
    ],

    # =========================================================================
    # 9. 回避 / 否认感受 (Avoidance / Emotional Denial)
    # 心理学原理：压抑、情感隔离、述情障碍 (alexithymia)
    # [subtle] 最容易被忽略但临床意义重大的类别
    # 常见于：男性社会化、创伤幸存者、回避型依附
    # =========================================================================
    "emotional_denial": [
        "i'm fine", "it's fine", "it's nothing",
        "doesn't bother me", "don't feel anything",
        "i'm over it", "it doesn't hurt", "i'm okay",
        "not a big deal", "no big deal", "who cares",
        "it is what it is", "i'm used to it",
        "doesn't affect me", "i'm numb",
        "it was a long time ago", "i've moved on",
        "water under the bridge", "ancient history",
        "i don't need to talk about it",
        "there's nothing to process", "i've dealt with it",
        "it didn't affect me that much",
        "other people have it worse",
        "i shouldn't complain", "first world problems",
        "i'm just tired", "it's just stress",
        "i'm not upset", "i'm not angry", "i'm not sad",
        "it doesn't really matter", "i don't really care",
        # 理智化 (intellectualization)
        "rationally i know", "logically speaking",
        "objectively", "if you think about it",
        "it makes sense that", "i understand why they",
    ],

    # =========================================================================
    # 10. 投射 / 防御机制 (Projection / Defensive Mechanisms)
    # 心理学原理：经典防御机制、认知失调回避
    # 常见于：低自我觉察、自恋特质、冲突中的反击
    # =========================================================================
    "projection_defense": [
        "you're the one who", "look at yourself",
        "you're projecting", "that's your problem",
        "speak for yourself", "not my problem",
        "deal with it yourself", "you need help not me",
        "you're the crazy one", "you're the one with issues",
        "don't put that on me", "that's on you",
        "maybe you should look in the mirror",
        "pot calling the kettle black",
        "you're no better", "who are you to judge",
        "at least i don't", "yeah well you",
        "what about when you", "you do the same thing",
        # 反击/转移
        "nice deflection", "way to change the subject",
        "don't turn this around on me",
        "we're not talking about me right now",
        "stop trying to make this about you",
    ],

    # =========================================================================
    # 11. 威胁关系断裂 (Relationship Rupture Threats)
    # 心理学原理：依附焦虑、抛弃恐惧的防御性表达、控制策略
    # Gottman: 预测离婚的高危信号
    # =========================================================================
    "relationship_rupture": [
        # 终止关系
        "i'm leaving", "we're done", "it's over",
        "i'm walking away", "don't contact me",
        "don't ever talk to me again", "lose my number",
        "i'm cutting you off", "out of my life",
        "dead to me", "i want nothing to do with you",
        "i want a divorce", "i want to break up",
        "i'm moving out", "i need space",
        # 情感撤回
        "i don't love you anymore", "my feelings have changed",
        "i feel nothing for you", "we're just roommates",
        "i've checked out", "i stopped caring",
        "love isn't enough", "we're too different",
        # 最后通牒
        "it's me or", "choose", "if you don't then i will",
        "this is your last chance", "final warning",
        "one more time and", "i swear to god if",
        # 职场特有
        "i quit", "i'm resigning", "i'm out",
        "find someone else", "good luck without me",
        "not my problem anymore", "i'm done carrying this team",
    ],

    # =========================================================================
    # 12. 被动攻击 / 隐性敌意 (Passive Aggression / Covert Hostility)
    # 心理学原理：间接攻击性、权力不对等下的愤怒表达
    # [subtle] 表面礼貌但带有攻击性
    # =========================================================================
    "passive_aggression": [
        "sure, whatever you say", "if you say so",
        "you know best", "you're always right",
        "must be nice", "good for you",
        "oh really", "interesting",
        "i'm sorry you feel that way",
        "couldn't care less",
        "wow okay", "cool story",
        "didn't ask", "nobody asked",
        "thanks for the lecture", "thanks for the advice",
        "yes dear", "okay boss",
        "sorry for existing", "sorry for breathing",
        "my bad for having feelings",
        "i'll just keep my mouth shut then",
        "clearly my opinion doesn't matter",
        "i guess i'm always wrong",
        # 讽刺
        "oh how generous of you", "what a saint",
        "congratulations", "slow clap",
        "how very kind of you", "that's rich coming from you",
        "oh i'm the bad guy now", "so now i'm the villain",
        # 职场
        "per my last email", "as previously mentioned",
        "as i already explained", "going forward",
        "i'll defer to your expertise",
        "with all due respect", "no offense but",
        "just to be clear", "for the record",
        "i'm just trying to help", "just a thought",
    ],

    # =========================================================================
    # 13. 伪装顺从 / 情感撤离 (Pseudo-compliance / Emotional Withdrawal)
    # 心理学原理：表面顺从掩盖内心的脱离、Gottman 石墙前兆
    # [subtle] 最隐蔽的否定形式 — 对话看似继续但人已经走了
    # 常见于：长期被控制的关系、习得性无助、回避型依附
    # =========================================================================
    "pseudo_compliance": [
        "are you serious", "you can't be serious",
        "really", "are you kidding",
        "alright", "alright then", "okay then",
        "fine", "fine then", "if that's what you think",
        "up to you", "your call", "you decide",
        "do what you want", "have it your way",
        "i guess", "i suppose", "if you say so",
        "sure", "sure thing", "right",
        "okay fine", "yeah okay", "k", "ok",
        "mm", "mhm", "uh huh", "yep",
        "cool", "great", "awesome",
        "whatever makes you happy",
        "whatever you think is best",
        "i just want this to be over",
        "can we just move on",
        "let's just get this over with",
        "it doesn't matter what i think",
        "you're gonna do what you want anyway",
        "no point in arguing", "why do i even bother",
        # 职场特有
        "sounds good", "will do", "understood",
        "copy that", "roger", "acknowledged",
        "i'll figure it out", "i'll manage",
        "it's above my head anyway",
    ],

    # =========================================================================
    # 14. 社交退缩 / 自我孤立 (Social Withdrawal / Self-Isolation)
    # 心理学原理：回避型应对、抑郁退缩、社交焦虑
    # 常见于：抑郁发作、创伤后、社交创伤
    # =========================================================================
    "social_withdrawal": [
        "i want to be alone", "don't need anyone",
        "better off alone", "i'm fine on my own",
        "don't need your help", "i can handle it myself",
        "stop worrying about me", "mind your own business",
        "stay out of it", "not your concern",
        "i don't need people", "people are exhausting",
        "i'm not a people person", "i prefer being alone",
        "don't check on me", "stop checking up on me",
        "i'll deal with it on my own",
        "i don't want to burden anyone",
        "everyone has their own problems",
        "no one needs to know",
        "i'm just going to keep to myself",
        "i need to figure this out alone",
        "i don't want to drag anyone into this",
    ],

    # =========================================================================
    # 15. 蔑视 / 轻蔑 (Contempt / Dismissiveness)
    # 心理学原理：Gottman 四骑士中最具破坏性的——蔑视
    # 研究：蔑视是离婚的最强预测因子 (Gottman, 1994)
    # =========================================================================
    "contempt": [
        # 智力蔑视
        "are you stupid", "are you dumb", "are you an idiot",
        "use your brain", "think before you speak",
        "do i have to spell it out", "it's not rocket science",
        "obviously", "clearly you don't understand",
        "how many times do i have to explain",
        "a child could understand this",
        "i can't believe i have to explain this",
        # 人格蔑视
        "grow up", "be a man", "man up",
        "stop being so sensitive", "you're overreacting",
        "you're being dramatic", "drama queen",
        "you're impossible", "you're exhausting",
        "you're too much", "you're insufferable",
        "what is wrong with you", "get over it",
        "get over yourself", "the world doesn't revolve around you",
        "stop playing the victim", "victim mentality",
        "cry me a river", "boo hoo",
        "spare me", "give me a break",
        "here come the waterworks",
        # 能力蔑视
        "you can't even", "you couldn't even",
        "you're incapable", "typical",
        "i expected nothing and i'm still disappointed",
        "why am i not surprised", "of course you did",
        # 非言语蔑视（文字形式）
        "lol", "lmao", "haha okay",
        "eye roll", "smh", "facepalm",
    ],

    # =========================================================================
    # 16. 操控 / 情感勒索 (Manipulation / Emotional Blackmail)
    # 心理学原理：FOG (Fear, Obligation, Guilt) 模型 (Forward, 1997)
    # 常见于：控制型关系、自恋虐待、代际创伤
    # =========================================================================
    "manipulation": [
        # 内疚诱导
        "after everything i've done for you",
        "i sacrificed everything", "i gave up everything for you",
        "you owe me", "this is how you repay me",
        "ungrateful", "you don't appreciate",
        "i do everything and you do nothing",
        "no one else would put up with you",
        "you should be grateful", "count your blessings",
        # 情感勒索
        "if you leave i'll", "you'll destroy me",
        "i can't live without you", "i'll hurt myself if",
        "you're killing me", "you're breaking my heart",
        "do you want me to suffer",
        # 贬低/控制
        "you can't survive without me",
        "no one else will love you",
        "you'll never find anyone better",
        "you need me", "where would you be without me",
        "i made you who you are",
        # 孤立策略
        "your friends are a bad influence",
        "your family doesn't care about you",
        "they're trying to turn you against me",
        "i'm the only one who truly",
        "they don't know you like i do",
        # 职场操控
        "you should be thankful to have this job",
        "in this economy", "no one else will hire you",
        "you're lucky i put up with your performance",
        "i've been very patient with you",
        "other people would kill for this opportunity",
    ],

    # =========================================================================
    # 17. 否认/改写现实 (Reality Denial / Gaslighting)
    # 心理学原理：煤气灯效应、认知控制、现实测试破坏
    # [escalation] 持续暴露可导致受害者解离和C-PTSD
    # =========================================================================
    "gaslighting": [
        "that never happened", "you're imagining things",
        "you're making things up", "you're delusional",
        "you're crazy", "you need help",
        "you're being paranoid", "that's not what happened",
        "that's not what i said", "you're twisting my words",
        "you're remembering it wrong", "you always exaggerate",
        "you're too sensitive", "you take everything personally",
        "it was just a joke", "can't you take a joke",
        "you have no sense of humor", "lighten up",
        "i never said that", "when did i ever say that",
        "you're the only one who thinks that",
        "no one else has a problem with it",
        "ask anyone", "everyone agrees with me",
        "you're reading too much into it",
        "stop overthinking", "you're overanalyzing",
        "that's not how it went", "you're confused",
        "maybe you should see a therapist",
    ],

    # =========================================================================
    # 18. 竞争性比较 / 贬低 (Competitive Comparison / Belittling)
    # 心理学原理：自恋补偿、自尊威胁防御、三角化
    # 常见于：伴侣冲突、手足竞争、职场竞争
    # =========================================================================
    "competitive_comparison": [
        # 伴侣关系
        "my ex never", "my ex always", "my ex was better at",
        "my ex would never treat me like this",
        "other couples don't have this problem",
        "everyone else's partner", "why can't you be more like",
        "my friend's husband", "my friend's wife",
        "[name] would never", "look at how [name] treats",
        # 家庭
        "your brother never", "your sister always",
        "why can't you be more like your sibling",
        "your father was the same", "just like your mother",
        "the apple doesn't fall far",
        # 职场
        "your predecessor did it better",
        "the previous person in this role",
        "other teams don't have this issue",
        "our competitors manage to",
        "at my old company we",
        "even the intern could",
    ],

    # =========================================================================
    # 19. 道德绑架 / 义务化 (Moral Obligation / Guilt-Tripping)
    # 心理学原理：超我驱动、文化内疚、孝道压力
    # 常见于：东亚家庭动态、宗教情境、代际冲突
    # =========================================================================
    "moral_obligation": [
        "you should be ashamed", "shame on you",
        "how could you", "how dare you",
        "what kind of person", "what kind of son",
        "what kind of daughter", "what kind of parent",
        "is this how i raised you",
        "i raised you better than this",
        "what would people think", "people are watching",
        "you're embarrassing me", "you're embarrassing yourself",
        "you're bringing shame to this family",
        "a good person would", "if you were a real friend",
        "real friends don't", "family comes first",
        "blood is thicker than water",
        "you only have one mother", "respect your elders",
        "after all i've been through",
        "god is watching", "you'll regret this",
        "when i'm gone you'll understand",
        "one day you'll appreciate",
    ],
}


# -----------------------------------------------------------------------------
# 1) 规范化（文本与短语统一到同一“比较空间”）
# -----------------------------------------------------------------------------
_APOSTROPHES = {
    "’": "'",
    "‘": "'",
    "“": '"',
    "”": '"',
    "–": "-",
    "—": "-",
}

_PUNCT_RE = re.compile(r"[^a-z0-9\s']+", re.IGNORECASE)
_WS_RE = re.compile(r"\s+")

def normalise_text(text: str) -> str:
    """
    Lowercase + normalize quotes + remove punctuation (keep apostrophe) + collapse spaces.

    Design goal:
    - stable matching across punctuation variants
    - safe for boundary matching
    """
    s = (text or "").lower()
    for k, v in _APOSTROPHES.items():
        s = s.replace(k, v)
    s = _PUNCT_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def _is_multiword(phrase: str) -> bool:
    return " " in phrase.strip()


def _dedupe_phrases(phrases: Iterable[str]) -> Tuple[List[str], Set[str]]:
    """
    Deduplicate by normalised form; return (kept_phrases_original, normalised_set).
    """
    kept: List[str] = []
    seen: Set[str] = set()
    for p in phrases:
        p0 = (p or "").strip()
        if not p0:
            continue
        pn = normalise_text(p0)
        if not pn:
            continue
        if pn in seen:
            continue
        seen.add(pn)
        kept.append(p0)
    return kept, seen


# -----------------------------------------------------------------------------
# 2) 边界匹配：单词用 \b；短语在 normalised space 里做 “surrounded by spaces” 的匹配
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class NegatorMatch:
    category: str
    phrase: str  # original phrase as stored


class ContextNegatorDetector:
    """
    CABSAIA-style detector:
    - normalise text once
    - phrase matching (multiword) with conservative boundary constraints
    - word matching with regex word boundaries
    - dedupe at build-time to avoid drift
    """

    def __init__(self, lexicon: Dict[str, List[str]]):
        self.lexicon: Dict[str, List[str]] = {}
        self._phrase_norm_map: Dict[str, List[Tuple[str, str]]] = {}
        # category -> list[(norm_phrase, original_phrase)] for multiword
        self._word_patterns: Dict[str, List[Tuple[re.Pattern[str], str]]] = {}
        # category -> list[(compiled_pattern, original_phrase)] for single word

        for cat, phrases in (lexicon or {}).items():
            kept, _ = _dedupe_phrases(phrases)
            if not kept:
                continue
            self.lexicon[cat] = kept

        self._build()

    def _build(self) -> None:
        for cat, phrases in self.lexicon.items():
            mw: List[Tuple[str, str]] = []
            ww: List[Tuple[re.Pattern[str], str]] = []
            for p in phrases:
                pn = normalise_text(p)
                if not pn:
                    continue
                if _is_multiword(pn):
                    # boundary: ensure phrase appears as token sequence
                    # we match inside " " + text + " " to avoid prefix/suffix bleed
                    mw.append((pn, p))
                else:
                    # strict word boundary
                    pat = re.compile(rf"\b{re.escape(pn)}\b", flags=re.IGNORECASE)
                    ww.append((pat, p))
            self._phrase_norm_map[cat] = mw
            self._word_patterns[cat] = ww

    def detect(self, text: str) -> Dict[str, List[str]]:
        """
        Return {category: [matched_original_phrases]}.
        Matching is conservative:
        - multiword phrases match in normalised token space
        - single words match with word boundary
        """
        t = normalise_text(text)
        if not t:
            return {}

        padded = f" {t} "
        out: Dict[str, List[str]] = {}

        for cat in self.lexicon.keys():
            hits: List[str] = []
            seen_norm: Set[str] = set()

            # multiword
            for pn, orig in self._phrase_norm_map.get(cat, []):
                # conservative: match " <phrase> " in padded text
                token = f" {pn} "
                if token in padded:
                    if pn not in seen_norm:
                        hits.append(orig)
                        seen_norm.add(pn)

            # single word
            for pat, orig in self._word_patterns.get(cat, []):
                pn = normalise_text(orig)
                if pn in seen_norm:
                    continue
                if pat.search(t):
                    hits.append(orig)
                    seen_norm.add(pn)

            if hits:
                out[cat] = hits

        return out

    def flatten(self) -> List[str]:
        all_phrases: List[str] = []
        for phrases in self.lexicon.values():
            all_phrases.extend(phrases)
        return all_phrases


# -----------------------------------------------------------------------------
# 3) 严重度：保持你同事原思路，但把规则写成可维护的“权重表”
# -----------------------------------------------------------------------------
_SEVERITY_WEIGHTS = {
    # 你可以按 CABSAIA 研究目标调整权重（越大越危险）
    "self_deprecation": 3,
    "emotional_escalation": 3,
    "gaslighting": 3,
    "relationship_rupture": 2,
    "manipulation": 2,
    "helplessness": 2,
    "contempt": 2,
    "communication_shutdown": 1,
    "blame_shifting": 1,
    "distrust": 1,
    "passive_aggression": 1,
    "pseudo_compliance": 1,
    "emotional_denial": 1,
    "absolutist_thinking": 1,
    "projection_defense": 1,
}

def get_severity(matches: Dict[str, List[str]]) -> str:
    """
    Return: "low" | "moderate" | "high" | "critical"
    """
    if not matches:
        return "low"

    score = 0
    total_hits = 0
    for cat, items in matches.items():
        w = _SEVERITY_WEIGHTS.get(cat, 1)
        score += w
        total_hits += len(items)

    # Conservative cutoffs
    if score >= 7 or (score >= 5 and total_hits >= 3):
        return "critical"
    if score >= 5 or (score >= 4 and total_hits >= 2):
        return "high"
    if score >= 2 or total_hits >= 2:
        return "moderate"
    return "low"


# -----------------------------------------------------------------------------
# 4) 预置 detector（项目内直接 import 用）
# -----------------------------------------------------------------------------
DETECTOR = ContextNegatorDetector(CONTEXT_NEGATORS)

def detect_negators(text: str) -> Dict[str, List[str]]:
    return DETECTOR.detect(text)

def get_all_negators() -> List[str]:
    return DETECTOR.flatten()