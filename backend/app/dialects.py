from typing import Final

DIALECTS: Final[list[dict[str, str]]] = [
    {"id": "auto", "name": "Auto detect", "name_ar": "اكتشاف تلقائي", "region": "Automatic"},
    {"id": "msa", "name": "Modern Standard Arabic", "name_ar": "العربية الفصحى", "region": "Standard"},
    {"id": "lebanese", "name": "Lebanese Arabic", "name_ar": "لبناني", "region": "Levant"},
    {"id": "syrian", "name": "Syrian Arabic", "name_ar": "سوري", "region": "Levant"},
    {"id": "palestinian", "name": "Palestinian Arabic", "name_ar": "فلسطيني", "region": "Levant"},
    {"id": "jordanian", "name": "Jordanian Arabic", "name_ar": "أردني", "region": "Levant"},
    {"id": "egyptian", "name": "Egyptian Arabic", "name_ar": "مصري", "region": "Egypt"},
    {"id": "gulf", "name": "Gulf Arabic", "name_ar": "خليجي", "region": "Gulf"},
    {"id": "saudi", "name": "Saudi Arabic", "name_ar": "سعودي", "region": "Gulf"},
    {"id": "hijazi", "name": "Hijazi Arabic", "name_ar": "حجازي", "region": "Saudi Arabia"},
    {"id": "najdi", "name": "Najdi Arabic", "name_ar": "نجدي", "region": "Saudi Arabia"},
    {"id": "iraqi", "name": "Iraqi Arabic", "name_ar": "عراقي", "region": "Iraq"},
    {"id": "yemeni", "name": "Yemeni Arabic", "name_ar": "يمني", "region": "Yemen"},
    {"id": "sudanese", "name": "Sudanese Arabic", "name_ar": "سوداني", "region": "Sudan"},
    {"id": "libyan", "name": "Libyan Arabic", "name_ar": "ليبي", "region": "North Africa"},
    {"id": "tunisian", "name": "Tunisian Arabic", "name_ar": "تونسي", "region": "North Africa"},
    {"id": "algerian", "name": "Algerian Arabic", "name_ar": "جزائري", "region": "North Africa"},
    {"id": "moroccan", "name": "Moroccan Arabic (Darija)", "name_ar": "مغربي / دارجة", "region": "North Africa"},
]

DIALECT_IDS: Final[set[str]] = {dialect["id"] for dialect in DIALECTS}
DIALECT_NAMES: Final[dict[str, str]] = {dialect["id"]: dialect["name"] for dialect in DIALECTS}

DIALECT_GUIDANCE: Final[dict[str, str]] = {
    "msa": "Use natural Modern Standard Arabic, not colloquial forms.",
    "lebanese": "Use broadly understandable Lebanese wording; avoid forcing hyper-local village vocabulary.",
    "syrian": "Use broadly understandable Syrian wording, primarily urban Levantine unless context suggests otherwise.",
    "palestinian": "Use broadly understandable Palestinian wording and preserve the speaker's intent.",
    "jordanian": "Use broadly understandable Jordanian wording without caricature.",
    "egyptian": "Use natural contemporary Egyptian Arabic suitable for everyday written conversation.",
    "gulf": "Use neutral, broadly understandable Gulf Arabic rather than an overly specific local variety.",
    "saudi": "Use neutral contemporary Saudi Arabic unless the user chooses Hijazi or Najdi.",
    "hijazi": "Use broadly understandable Hijazi Arabic.",
    "najdi": "Use broadly understandable Najdi Arabic.",
    "iraqi": "Use natural, broadly understandable Iraqi Arabic.",
    "yemeni": "Use neutral broadly understandable Yemeni Arabic and flag highly regional ambiguity.",
    "sudanese": "Use natural broadly understandable Sudanese Arabic.",
    "libyan": "Use natural broadly understandable Libyan Arabic.",
    "tunisian": "Use contemporary Tunisian Arabic and preserve French code-switching only when meaningful.",
    "algerian": "Use contemporary Algerian Arabic and preserve code-switching only when meaningful.",
    "moroccan": "Use contemporary Moroccan Darija and preserve code-switching only when meaningful.",
}
