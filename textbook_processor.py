import re
import random


def clean_text(text):
    """تنظيف النص من الرموز والأحرف غير المرغوبة"""
    text = re.sub('<.*?>', '', text)
    text = re.sub(r'[^\w\s\.\,\?\!\:\;\-؟]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_paragraphs(text):
    """تقسيم النص إلى فقرات"""
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]


def extract_sentences(text):
    """تقسيم النص إلى جمل (بدون NLTK)"""
    return re.split(r'(?<=[.!؟])\s+', text)


def tokenize_words(text):
    """تقسيم النص إلى كلمات (بدون NLTK)"""
    return re.findall(r'\b\w+\b', text)


def identify_main_concepts(text, num_concepts=5):
    """تحديد المفاهيم الرئيسية في النص"""
    clean = clean_text(text)
    words = tokenize_words(clean)

    words = [word.lower() for word in words if len(word) > 3]

    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:num_concepts]]


def generate_objectives(grade_level, concepts):
    templates = [
        "فهم المفهوم الأساسي لـ {concept}",
        "شرح العلاقة بين {concept} والمفاهيم الأخرى",
        "تطبيق مبادئ {concept} في حل المشكلات",
        "تحليل خصائص {concept} وتأثيرها",
        "تقييم أهمية {concept} في السياق المناسب"
    ]

    return [
        random.choice(templates).format(concept=concept)
        for concept in concepts
    ]


def generate_introduction(grade_level, topic, concepts):
    if len(concepts) >= 2:
        return f"""مقدمة عن {topic}:

سيتعرف الطلاب في هذا الدرس على {concepts[0]} و{concepts[1]}، وأهمية هذه المفاهيم في فهم {topic}."""
    elif concepts:
        return f"""مقدمة عن {topic}:

سيتعرف الطلاب في هذا الدرس على مفهوم {concepts[0]} وأهميته."""
    else:
        return f"مقدمة عن {topic}"


def generate_main_activities(grade_level, topic, concepts, text):
    paragraphs = extract_paragraphs(text)
    important_sentences = []

    for para in paragraphs[:3]:
        sentences = extract_sentences(para)
        if sentences:
            important_sentences.append(sentences[0])

    return f"""نشاط 1: مناقشة حول {topic}
الوقت: 15 دقيقة

نشاط 2: تحليل النص
"{important_sentences[0] if important_sentences else text[:100]}"

نشاط 3: تطبيق المفاهيم
يطبق الطلاب المفاهيم المتعلقة بـ {topic}
"""


def generate_assessment(grade_level, topic, concepts):
    return f"""التقييم:
- مناقشة شفهية
- تلخيص المفاهيم الرئيسية
- تطبيق عملي على {concepts[0] if concepts else topic}
"""


def generate_conclusion(grade_level, topic, concepts):
    return f"""الخاتمة:
- مراجعة المفاهيم
- التأكيد على أهمية {topic}
"""


def generate_materials(grade_level, topic, concepts):
    return f"""المواد المطلوبة:
- كتاب الطالب
- أوراق عمل
- سبورة
"""


def process_textbook_content(grade_level, topic, teaching_strategy, textbook_content):
    cleaned_text = clean_text(textbook_content)
    main_concepts = identify_main_concepts(cleaned_text)

    objectives = generate_objectives(grade_level, main_concepts)
    objectives_text = "\n".join([f"- {o}" for o in objectives])

    return f"""
# خطة درس: {topic}
## الصف: {grade_level}
## استراتيجية التدريس: {teaching_strategy}

### الأهداف:
{objectives_text}

{generate_introduction(grade_level, topic, main_concepts)}

{generate_main_activities(grade_level, topic, main_concepts, cleaned_text)}

{generate_assessment(grade_level, topic, main_concepts)}

{generate_conclusion(grade_level, topic, main_concepts)}

{generate_materials(grade_level, topic, main_concepts)}
"""
