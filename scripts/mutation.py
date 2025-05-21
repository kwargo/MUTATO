import random
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, Doc
from typing import Tuple, Optional

# Инициализация Natasha
segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)


def get_pos_natasha(word: str) -> Optional[str]:
    """
    Определяет часть речи для одного слова с помощью библиотеки Natasha.

    :param word: Входное слово (возможно с вопросительными знаками).
    :return: Метка части речи или None.
    """
    clean_word = word.replace("?", "")
    doc = Doc(clean_word)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    return doc.tokens[0].pos if doc.tokens else None


def get_pos(word: str) -> str:
    """
    Обёртка над get_pos_natasha: очищает слово и возвращает часть речи.

    :param word: Входное слово (возможно с вопросительными знаками).
    :return: Метка части речи или "Unknown".
    """
    clean_word = word.replace("?", "")
    return get_pos_natasha(clean_word)


def is_consonant(char: str) -> bool:
    """
    Проверяет, является ли символ согласной буквой русского алфавита.

    :param char: Одиночный символ.
    :return: True, если символ — согласная, иначе False.
    """
    consonants = "бвгджзйклмнпрстфхцчшщ"
    return char.lower() in consonants


def alternate_consonant(word: str) -> str:
    """
    Применяет правило чередования согласных в корне слова.

    :param word: Слово для трансформации.
    :return: Модифицированное слово, если правило применимо, иначе исходное.
    """
    alternations = {
        "к": "ч",
        "г": "ж",
        "х": "ш",
        "т": "ч",
        "д": "ж",
        "ск": "щ",
        "ст": "щ",
    }
    for old, new in alternations.items():
        if word.endswith(old):
            return word[:-len(old)] + new
    return word


def get_gender(word: str) -> str:
    """
    Определяет грамматический род существительного.

    :param word: Существительное в именительном падеже.
    :return: Метка рода: "masc", "fem", "neut" или "unknown".
    """
    doc = Doc(word)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    if doc.tokens and "Gender" in doc.tokens[0].feats:
        return doc.tokens[0].feats["Gender"].lower()
    return "unknown"


def mutate_word(word: str) -> Tuple[str, str, str]:
    """
    Генерирует мутацию для слова: добавляет префикс, суффикс, чередование или другие изменения.

    :param word: Входное слово (любая часть речи).
    :return: Кортеж (новая_форма, исходная_часть_речи, информация_о_мутации).
    """
    clean_word = word.replace("?", "")
    pos = get_pos(clean_word)
    mutation_info = ""
    new_word = clean_word

    if pos == "NOUN":
        gender = get_gender(clean_word)
        last_char = clean_word[-1].lower()
        mutation_type = random.choice(["suffix", "prefix", "diminutive"])

        # Логика мутаций для существительных
        if mutation_type == "suffix":
            if is_consonant(last_char):
                if gender == "masc":
                    suffix = random.choice(["ок", "ец", "ище"])
                elif gender == "fem":
                    suffix = random.choice(["ка", "ица", "очка"])
                else:
                    suffix = random.choice(["ко", "це"])
            else:
                suffix = random.choice(["к", "ц"])
            new_word = clean_word + suffix
            mutation_info = f"+{suffix}"

        elif mutation_type == "prefix":
            prefix = random.choice(["по", "за", "на", "пере", "при"])
            new_word = prefix + clean_word
            mutation_info = f"+{prefix}"

        else:  # diminutive
            if is_consonant(last_char):
                if gender == "masc":
                    suffix = random.choice(["ёк", "ик", "очек"])
                elif gender == "fem":
                    suffix = random.choice(["ка", "очка", "енька"])
                else:
                    suffix = random.choice(["ко", "ечко"])
                new_word = clean_word + suffix
                mutation_info = f"уменьш. +{suffix}"
            else:
                root = clean_word[:-1]
                suffix = random.choice(["ик", "ёк"] if gender == "masc" else ["ка", "очка"])  # пример
                new_word = root + suffix
                mutation_info = f"уменьш. -{last_char}+{suffix}"

    elif pos == "VERB":
        mutation_type = random.choice(["prefix", "suffix", "alternate"])
        last_char = clean_word[-1].lower()

        if mutation_type == "prefix":
            prefix = random.choice(["по", "за", "на", "пере", "при", "у"])
            new_word = prefix + clean_word
            mutation_info = f"+{prefix}"

        elif mutation_type == "suffix":
            if last_char == "ь":
                ending = random.choice(["ить", "еть"])
                new_word = clean_word[:-1] + ending
                mutation_info = f"-ь+{ending}"
            else:
                ending = random.choice(["ить", "еть", "ать"])
                new_word = clean_word + ending
                mutation_info = f"+{ending}"

        else:  # alternate
            root_alt = alternate_consonant(clean_word)
            if root_alt != clean_word:
                ending = random.choice(["ать", "ить"])
                new_word = root_alt + ending
                mutation_info = f"черед. +{ending}"
            else:
                new_word = clean_word + "ить"
                mutation_info = "+ить"

    elif pos == "ADJ":
        mutation_type = random.choice(["suffix", "gender", "comparative"])

        if mutation_type == "suffix":
            suffix = random.choice(["ый", "ий", "ой"])
            new_word = clean_word + suffix
            mutation_info = f"+{suffix}"

        elif mutation_type == "gender":
            if clean_word.endswith(("ый", "ий")):
                new_word = clean_word[:-2] + "ая"
            else:
                new_word = clean_word + "ая"
            mutation_info = "род: муж → жен"

        else:  # comparative
            if clean_word.endswith(("ый", "ий")):
                new_word = clean_word[:-2] + "ее"
            else:
                new_word = clean_word + "ее"
            mutation_info = "сравн. +ее"

    else:
        # Для неизвестных или иных частей речи
        mutation_type = random.choice(["suffix", "prefix"])
        if mutation_type == "suffix":
            suffix = random.choice(["ик", "ок"])
            new_word = clean_word + suffix
            mutation_info = f"+{suffix}"
        else:
            prefix = random.choice(["по", "за"])
            new_word = prefix + clean_word
            mutation_info = f"+{prefix}"

    return new_word, pos, mutation_info