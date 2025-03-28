from mutation import mutate_word
from visualization import plot_mutation_tree_static, plot_mutation_tree_interactive, save_graph
import random
import networkx as nx

# Функция для получения списка слов от пользователя
def get_user_words():
    print("Хотите ввести свои слова для мутации? (да/нет)")
    choice = input().strip().lower()
    
    if choice in ['да', 'yes', 'y']:
        print("Введите слова (по одному в строке). Для завершения ввода нажмите Enter на пустой строке:")
        words = []
        while True:
            word = input().strip()
            if word == "":
                break
            if word:
                words.append(word)
        if not words:
            print("Вы не ввели ни одного слова. Будут использованы слова из corpus.txt.")
            return None
        return words
    else:
        return None

# Загружаем исходный корпус (если пользователь не ввёл свои слова)
def load_corpus():
    with open(r'data/corpus.txt', 'r', encoding='utf-8') as f:
        full_corpus = f.read().splitlines()
    if not full_corpus:
        print("Файл corpus.txt пуст. Добавьте слова в файл или введите свои слова.")
        exit(1)
    return full_corpus

# Получаем начальные слова
user_words = get_user_words()
if user_words:
    initial_corpus = user_words
else:
    full_corpus = load_corpus()
    initial_corpus = random.sample(full_corpus, min(5, len(full_corpus)))

# Создаём граф
G = nx.DiGraph()

# Добавляем начальные слова в граф с их частями речи
for word in initial_corpus:
    _, pos, _ = mutate_word(word)  # Получаем часть речи
    G.add_node(word, pos=pos)

# Параметры симуляции
num_generations = 20
mutation_rate = 0.3
max_nodes = 50

# Генерация мутаций
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

# Сохранение графа
save_graph(G)