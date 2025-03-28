import random
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, Doc

# Инициализация Natasha
segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)

# Функция для определения части речи с помощью Natasha
def get_pos_natasha(word):
    clean_word = word
    while "?" in clean_word:
        clean_word = clean_word.replace("?", "")
    
    doc = Doc(clean_word)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    
    if doc.tokens:
        pos = doc.tokens[0].pos
        if pos in ["NOUN", "VERB", "ADJ", "ADV", "PREP", "CONJ", "PRON", "NUM", "INTJ"]:
            return pos
    return "Unknown"

# Функция для определения части речи
def get_pos(word):
    clean_word = word
    while "?" in clean_word:
        clean_word = clean_word.replace("?", "")
    
    return get_pos_natasha(clean_word)

# Функция для определения, является ли последняя буква согласной
def is_consonant(char):
    consonants = "бвгджзйклмнпрстфхцчшщ"
    return char.lower() in consonants

# Функция для чередования согласных
def alternate_consonant(word):
    alternations = {
        "к": "ч",  # бег → бежал
        "г": "ж",  # бег → бежал
        "х": "ш",  # муха → мушонка
        "т": "ч",  # свет → свечка
        "д": "ж W",  # еда → ежа
        "ск": "щ",  # плеск → плещу
        "ст": "щ",  # мост → мощу
    }
    for old, new in alternations.items():
        if word.endswith(old):
            return word[:-len(old)] + new
    return word

# Функция для определения рода существительного 
def get_gender(word):
    doc = Doc(word)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    if doc.tokens and "Gender" in doc.tokens[0].feats:
        return doc.tokens[0].feats["Gender"].lower()
    return "unknown"

# Функция мутации слова
def mutate_word(word):
    clean_word = word
    while "?" in clean_word:
        clean_word = clean_word.replace("?", "")
    
    pos = get_pos(clean_word)
    mutation_info = ""
    new_word = clean_word

    if pos == "NOUN":
        gender = get_gender(clean_word)
        last_char = clean_word[-1].lower()
        mutation_type = random.choice(["suffix", "prefix", "diminutive"])
        
        if mutation_type == "suffix":
            # Выбираем суффикс в зависимости от окончания и рода
            if is_consonant(last_char):
                # После согласных добавляем суффикс с гласной
                if gender == "masc":
                    suffix = random.choice(["ок", "ец", "ище"])
                    new_word = clean_word + suffix
                    mutation_info = f"+{suffix}"
                elif gender == "fem":
                    suffix = random.choice(["ка", "ица", "очка"])
                    new_word = clean_word + suffix
                    mutation_info = f"+{suffix}"
                else:
                    suffix = random.choice(["ко", "це"])
                    new_word = clean_word + suffix
                    mutation_info = f"+{suffix}"
            else:
                # После гласных добавляем согласный суффикс
                if gender == "masc":
                    suffix = random.choice(["к", "ц"])
                    new_word = clean_word + suffix
                    mutation_info = f"+{suffix}"
                elif gender == "fem":
                    suffix = random.choice(["к", "ц"])
                    new_word = clean_word + suffix
                    mutation_info = f"+{suffix}"
                else:
                    suffix = random.choice(["к", "ц"])
                    new_word = clean_word + suffix
                    mutation_info = f"+{suffix}"
        
        elif mutation_type == "prefix":
            # Добавляем префикс
            prefix = random.choice(["по", "за", "на", "пере", "при"])
            new_word = prefix + clean_word
            mutation_info = f"+{prefix}"
        
        elif mutation_type == "diminutive":
            # Уменьшительно-ласкательная форма
            if is_consonant(last_char):
                if gender == "masc":
                    suffix = random.choice(["ёк", "ик", "очек"])
                    new_word = clean_word + suffix
                    mutation_info = f"уменьш. +{suffix}"
                elif gender == "fem":
                    suffix = random.choice(["ка", "очка", "енька"])
                    new_word = clean_word + suffix
                    mutation_info = f"уменьш. +{suffix}"
                else:
                    suffix = random.choice(["ко", "ечко"])
                    new_word = clean_word + suffix
                    mutation_info = f"уменьш. +{suffix}"
            else:
                # Удаляем последнюю гласную и добавляем суффикс
                new_word = clean_word[:-1]
                if gender == "masc":
                    suffix = random.choice(["ик", "ёк"])
                    new_word = new_word + suffix
                    mutation_info = f"уменьш. -{last_char}+{suffix}"
                elif gender == "fem":
                    suffix = random.choice(["ка", "очка"])
                    new_word = new_word + suffix
                    mutation_info = f"уменьш. -{last_char}+{suffix}"
                else:
                    suffix = random.choice(["ко", "ечко"])
                    new_word = new_word + suffix
                    mutation_info = f"уменьш. -{last_char}+{suffix}"

    elif pos == "VERB":
        mutation_type = random.choice(["prefix", "suffix", "alternate"])
        
        if mutation_type == "prefix":
            # Добавляем префикс
            prefix = random.choice(["по", "за", "на", "пере", "при", "у"])
            new_word = prefix + clean_word
            mutation_info = f"+{prefix}"
        
        elif mutation_type == "suffix":
            # Добавляем суффикс с учётом окончания
            last_char = clean_word[-1].lower()
            if last_char == "ь":
                new_word = clean_word[:-1] + random.choice(["ить", "еть"])
                mutation_info = f"-ь+{new_word[-3:]}"
            else:
                suffix = random.choice(["ить", "еть", "ать"])
                new_word = clean_word + suffix
                mutation_info = f"+{suffix}"
        
        elif mutation_type == "alternate":
            # Чередование согласных в корне
            new_word = alternate_consonant(clean_word)
            if new_word != clean_word:
                suffix = random.choice(["ать", "ить"])
                new_word = new_word + suffix
                mutation_info = f"черед. +{suffix}"
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
            if clean_word.endswith("ый"):
                new_word = clean_word[:-2] + "ая"
                mutation_info = "род: муж → жен"
            elif clean_word.endswith("ий"):
                new_word = clean_word[:-2] + "ая"
                mutation_info = "род: муж → жен"
            else:
                new_word = clean_word + "ая"
                mutation_info = "+ая"
        
        elif mutation_type == "comparative":
            # Сравнительная степень
            if clean_word.endswith("ый") or clean_word.endswith("ий"):
                new_word = clean_word[:-2] + "ее"
                mutation_info = "сравн. +ее"
            else:
                new_word = clean_word + "ее"
                mutation_info = "сравн. +ее"

    elif pos == "Unknown":
        # Если часть речи неизвестна, применяем нейтральную мутацию
        mutation_type = random.choice(["suffix", "prefix"])
        if mutation_type == "suffix":
            suffix = random.choice(["ик", "ок"])
            new_word = clean_word + suffix
            mutation_info = f"+{suffix}"
        else:
            prefix = random.choice(["по", "за"])
            new_word = prefix + clean_word
            mutation_info = f"+{prefix}"
    
    else:
        # Для других частей речи (PREP, CONJ и т.д.) оставляем слово без изменений
        new_word = clean_word
        mutation_info = "без изменений"

    return new_word, pos, mutation_info