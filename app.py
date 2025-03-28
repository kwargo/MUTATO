from flask import Flask, render_template, request, send_file
import os
import platform
import networkx as nx
import random
from scripts.mutation import mutate_word
from scripts.visualization import plot_mutation_tree_static, plot_mutation_tree_interactive, save_graph

app = Flask(__name__)

# Создаём директории для результатов
os.makedirs('results', exist_ok=True)
os.makedirs('results/plots', exist_ok=True)

# Главная страница
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Получаем слова от пользователя
        words_input = request.form.get('words', '').strip()
        if not words_input:
            return render_template('index.html', error="Пожалуйста, введите хотя бы одно слово.")

        initial_corpus = words_input.split()

        # Создаём граф
        G = nx.DiGraph()

        # Добавляем начальные слова в граф с их частями речи
        for word in initial_corpus:
            _, pos, _ = mutate_word(word)  # Получаем часть речи
            G.add_node(word, pos=pos)

        # Параметры симуляции
        num_generations = 10
        mutation_rate = 0.3
        max_nodes = 50

        # Генерация мутаций
        with open('results/mutation_history.txt', 'w', encoding='utf-8') as history_file:
            for generation in range(num_generations):
                if len(G.nodes) >= max_nodes:
                    break
                if not G.nodes:
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
        save_graph(G)

        return render_template('result.html')

    return render_template('index.html')

# Маршрут для скачивания файлов
@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join('results', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "Файл не найден.", 404

# Маршрут для отображения интерактивного графа
@app.route('/graph')
def show_graph():
    with open('results/plots/mutation_tree_interactive.html', 'r', encoding='utf-8') as f:
        graph_html = f.read()
    return graph_html

if __name__ == '__main__':
    if platform.system() == "Windows":
        from waitress import serve
        serve(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)