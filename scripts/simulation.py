import random
from typing import List, Optional
from mutation import mutate_word
from visualization import plot_mutation_tree_static, plot_mutation_tree_interactive, save_graph
import networkx as nx


def get_user_words() -> Optional[List[str]]:
    """
    Запрашивает у пользователя список слов для мутации.

    При запросе пользователю предлагается ввести слова по одному в строке.
    Ввод завершается пустой строкой. Если пользователь не вводит ни одного слова,
    возвращается None и будут использованы слова из корпуса.

    :return: Список введённых слов или None, если пользователь отказался вводить.
    """
    print("Хотите ввести свои слова для мутации? (да/нет)")
    choice = input().strip().lower()

    if choice in ['да', 'yes', 'y']:
        print("Введите слова (по одному в строке). Для завершения ввода нажмите Enter на пустой строке:")
        words: List[str] = []
        while True:
            word = input().strip()
            if not word:
                break
            words.append(word)
        if not words:
            print("Вы не ввели ни одного слова. Будут использованы слова из corpus.txt.")
            return None
        return words
    return None


def load_corpus() -> List[str]:
    """
    Загружает список слов из файла data/corpus.txt.

    Файл читается построчно. Если файл пуст или не найден,
    программа выводит сообщение об ошибке и завершает работу.

    :raises FileNotFoundError: если файл не найден.
    :return: Список слов из корпуса.
    """
    try:
        with open('data/corpus.txt', 'r', encoding='utf-8') as f:
            full_corpus = f.read().splitlines()
    except FileNotFoundError:
        print("Файл corpus.txt не найден. Пожалуйста, добавьте файл в папку data.")
        exit(1)

    if not full_corpus:
        print("Файл corpus.txt пуст. Добавьте слова в файл или введите свои слова.")
        exit(1)
    return full_corpus


# Основной блок исполнения
if __name__ == '__main__':
    # Получаем начальные слова
    user_words = get_user_words()
    if user_words is not None:
        initial_corpus: List[str] = user_words
    else:
        full_corpus = load_corpus()
        initial_corpus = random.sample(full_corpus, min(5, len(full_corpus)))

    # Создаём направленный граф мутаций
    G = nx.DiGraph()

    # Добавляем начальные слова в граф с их частями речи
    for word in initial_corpus:
        _, pos, _ = mutate_word(word)
        G.add_node(word, pos=pos)

    # Параметры симуляции
    num_generations: int = 20
    mutation_rate: float = 0.3
    max_nodes: int = 50

    # Файл для истории мутаций
    with open('results/mutation_history.txt', 'w', encoding='utf-8') as history_file:
        for generation in range(num_generations):
            if len(G.nodes) >= max_nodes:
                print(f"Достигнут лимит узлов ({max_nodes}), симуляция остановлена.")
                break
            if not G.nodes:
                print("Граф пуст, мутации невозможны.")
                break
            num_to_mutate = max(1, int(len(G.nodes) * mutation_rate))
            words_to_mutate = random.sample(list(G.nodes), min(num_to_mutate, len(G.nodes)))
            for word in words_to_mutate:
                new_word, pos, mutation_info = mutate_word(word)
                G.add_node(new_word, pos=pos)
                G.add_edge(word, new_word, mutation=mutation_info)
                history_file.write(f"{word} ({G.nodes[word]['pos']}) -> {new_word} ({pos}): {mutation_info}\n")

    # Визуализация графа
    plot_mutation_tree_static(G)
    plot_mutation_tree_interactive(G)

    # Сохранение графа в файл
    save_graph(G)