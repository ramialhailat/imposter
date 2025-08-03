"""
Game data containing domains and items
"""

DOMAINS = [
    "Clothes / الملابس",
    "Food / الطعام",
    "Animals / الحيوانات",
    "Sports / الرياضة",
    "Jobs / المهن",
    "Places / الأماكن"
]

ITEMS = {
    "Clothes / الملابس": [
        "Thobe / ثوب",
        "Abaya / عباية",
        "Ghutrah / غترة",
        "Bisht / بشت",
        "Sandals / نعال",
        "Tarha / طرحة",
        "Belt / حزام",
        "Ring / خاتم"
    ],
    "Food / الطعام": [
        "Kabsa / كبسة",
        "Shawarma / شاورما",
        "Hummus / حمص",
        "Falafel / فلافل",
        "Dates / تمر",
        "Kunafa / كنافة",
        "Coffee / قهوة",
        "Tea / شاي"
    ],
    "Animals / الحيوانات": [
        "Camel / جمل",
        "Horse / حصان",
        "Falcon / صقر",
        "Lion / أسد",
        "Cat / قط",
        "Dog / كلب",
        "Fish / سمك",
        "Bird / طير"
    ],
    "Sports / الرياضة": [
        "Football / كرة قدم",
        "Basketball / كرة سلة",
        "Swimming / سباحة",
        "Running / جري",
        "Tennis / تنس",
        "Volleyball / كرة طائرة",
        "Boxing / ملاكمة",
        "Cycling / ركوب الدراجات"
    ],
    "Jobs / المهن": [
        "Teacher / معلم",
        "Doctor / طبيب",
        "Engineer / مهندس",
        "Pilot / طيار",
        "Chef / طباخ",
        "Driver / سائق",
        "Police / شرطي",
        "Nurse / ممرض"
    ],
    "Places / الأماكن": [
        "Mosque / مسجد",
        "Mall / مول",
        "Beach / شاطئ",
        "Desert / صحراء",
        "Mountain / جبل",
        "School / مدرسة",
        "Hospital / مستشفى",
        "Park / حديقة"
    ]
}

def get_items_for_domain(domain: str) -> list:
    """Get the list of items for a given domain"""
    return ITEMS.get(domain, [])
