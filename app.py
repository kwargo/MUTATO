from flask import Flask, render_template, request, send_file, Response
import os
import platform
import networkx as nx
import random
from typing import Optional
from scripts.mutation import mutate_word
from scripts.visualization import (
    plot_mutation_tree_static,
    plot_mutation_tree_interactive,
    save_graph
)

app = Flask(__name__)

# Создаём директории для результатов
os.makedirs('results/plots', exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index() -> str:
    """
    Обрабатывает главную страницу: получение слов от пользователя,
    генерацию и визуализацию мутаций, сохранение результатов.

    GET: Возвращает шаблон index.html.
    POST: Принимает слова, генерирует граф мутаций,
    сохраняет историю, статичный и интерактивный графы,
    сохраняет GraphML и возвращает шаблон result.html.

    :return: Рендеринг HTML-страницы.
    """
    if request.method == 'POST':
        words_input: str = request.form.get('words', '').strip()
        if not words_input:
            return render_template('index.html', error="Пожалуйста, введите хотя бы одно слово.")

        initial_corpus = words_input.split()
        G = nx.DiGraph()

        # Добавляем начальные узлы
        for word in initial_corpus:
            _, pos, _ = mutate_word(word)
            G.add_node(word, pos=pos)

        # Параметры симуляции
        num_generations: int = 10
        mutation_rate: float = 0.3
        max_nodes: int = 50

        # Генерация мутаций и запись истории
        history_path = os.path.join('results', 'mutation_history.txt')
        os.makedirs('results', exist_ok=True)
        with open(history_path, 'w', encoding='utf-8') as history_file:
            for _ in range(num_generations):
                if len(G.nodes) >= max_nodes or not G.nodes:
                    break
                count = max(1, int(len(G.nodes) * mutation_rate))
                to_mutate = random.sample(list(G.nodes), min(count, len(G.nodes)))
                for w in to_mutate:
                    new_word, pos, info = mutate_word(w)
                    G.add_node(new_word, pos=pos)
                    G.add_edge(w, new_word, mutation=info)
                    history_file.write(f"{w} ({G.nodes[w]['pos']}) -> {new_word} ({pos}): {info}\n")

        # Визуализация и сохранение графа
        plot_mutation_tree_static(G)
        plot_mutation_tree_interactive(G)
        save_graph(G)

        return render_template('result.html')

    # GET-запрос
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename: str) -> Response or tuple[str, int]:
    """
    Предоставляет файл для скачивания из папки results.

    :param filename: Имя файла в папке results.
    :return: Отправка файла или ошибка 404.
    """
    file_path = os.path.join('results', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "Файл не найден.", 404

@app.route('/graph')
def show_graph() -> str:
    """
    Возвращает HTML контент интерактивного графа мутаций.

    :return: Строка с HTML-файлом графа.
    """
    html_path = os.path.join('results', 'plots', 'mutation_tree_interactive.html')
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Граф не найден.", 404

if __name__ == '__main__':
    """
    Запускает Flask-приложение через waitress на Windows или встроенный сервер для других ОС.
    """
    port = int(os.environ.get('PORT', 5000))
    if platform.system() == 'Windows':
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
    else:
        app.run(host='0.0.0.0', port=port, debug=False)
