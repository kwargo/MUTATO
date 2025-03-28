import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from networkx.drawing.nx_agraph import graphviz_layout
import os
import matplotlib.colors as mcolors

def plot_mutation_tree_static(graph):
    if not graph.nodes:
        print("Граф пуст, визуализация невозможна.")
        return

    output_dir = os.path.join(os.getcwd(), 'results', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    
    fig = plt.figure(figsize=(25, 18), facecolor='#f0f0f0')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#e6f3ff')
    
    pos = graphviz_layout(graph, prog='dot', args='-Granksep=3 -Gnodesep=2')
    
    depths = nx.shortest_path_length(graph, list(graph.nodes)[0]) if graph.nodes else {}
    max_depth = max(depths.values()) if depths else 1
    if max_depth == 0:
        max_depth = 1

    node_colors = [mcolors.to_hex(plt.cm.RdYlGn(depths.get(node, 0) / max_depth)) for node in graph.nodes]
    node_sizes = [3000 + 1000 * graph.degree(node) for node in graph.nodes]
    
    edge_colors = []
    for u, v in graph.edges():
        depth_u = depths.get(u, 0)
        depth_v = depths.get(v, 0)
        avg_depth = (depth_u + depth_v) / 2 / max_depth
        edge_colors.append(plt.cm.coolwarm(avg_depth))
    
    nx.draw_networkx_edges(graph, pos, edge_color=edge_colors, arrows=True, 
                          arrowstyle='->', arrowsize=25, width=2, alpha=0.7)
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=node_sizes, 
                           edgecolors='black', linewidths=1.5, alpha=0.9)
    
    # Подписи узлов: добавляем часть речи
    labels = {node: f"{node}\n({graph.nodes[node]['pos']})" for node in graph.nodes}
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=12, font_weight='bold', 
                            font_family='Arial', font_color='black')
    
    # Подписи рёбер: информация о мутации
    edge_labels = {(u, v): graph[u][v]['mutation'] for u, v in graph.edges()}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=10, font_color='red')
    
    plt.title("Дерево мутаций слов: Эволюция слов", fontsize=20, pad=30, fontweight='bold', color='#333333')
    
    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn, norm=plt.Normalize(vmin=0, vmax=max_depth))
    plt.colorbar(sm, ax=ax, label='Глубина мутации', shrink=0.5, pad=0.02)
    
    plt.axis('off')
    
    static_path = os.path.join(output_dir, 'mutation_tree_static.png')
    plt.savefig(static_path, dpi=300, bbox_inches='tight')
    print(f"Статичный график сохранён по пути: {static_path}")
    plt.show()

def plot_mutation_tree_interactive(graph):
    if not graph.nodes:
        print("Граф пуст, визуализация невозможна.")
        return

    output_dir = os.path.join(os.getcwd(), 'results', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    
    pos = graphviz_layout(graph, prog='dot', args='-Granksep=3 -Gnodesep=2')
    
    edge_x = []
    edge_y = []
    edge_color_values = []
    edge_text = []
    depths = nx.shortest_path_length(graph, list(graph.nodes)[0]) if graph.nodes else {}
    max_depth = max(depths.values()) if depths else 1
    if max_depth == 0:
        max_depth = 1

    # Список для аннотаций рёбер
    annotations = []

    for u, v in graph.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        depth_u = depths.get(u, 0)
        depth_v = depths.get(v, 0)
        avg_depth = (depth_u + depth_v) / 2 / max_depth
        edge_color_values.extend([avg_depth, avg_depth, None])
        edge_text.extend([graph[u][v]['mutation'], graph[u][v]['mutation'], None])
        
        # Добавляем аннотацию для ребра
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        annotations.append(
            dict(
                x=mid_x,
                y=mid_y,
                xref="x",
                yref="y",
                text=graph[u][v]['mutation'],
                showarrow=False,
                font=dict(size=10, color="red"),
                align="center",
                ax=0,
                ay=0
            )
        )
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=2, color='#888'),
        hoverinfo='text',
        text=edge_text,
        opacity=0.7
    )
    
    node_x = [pos[node][0] for node in graph.nodes()]
    node_y = [pos[node][1] for node in graph.nodes()]
    node_colors = [depths.get(node, 0) / max_depth for node in graph.nodes()]
    node_sizes = [20 + 10 * graph.degree(node) for node in graph.nodes()]
    
    # Подписи узлов: добавляем часть речи
    node_labels = [f"{node} ({graph.nodes[node]['pos']})" for node in graph.nodes()]
    node_text = [f"Слово: {node}<br>Часть речи: {graph.nodes[node]['pos']}<br>Глубина: {depths.get(node, 0)}<br>Степень: {graph.degree(node)}"
                 for node in graph.nodes()]
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_labels,
        textposition='top center',
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale='Plasma',
            size=node_sizes,
            color=node_colors,
            colorbar=dict(
                thickness=15,
                title=dict(text='Глубина'),
                xanchor='left'
            ),
            line=dict(width=2, color='black')
        ),
        opacity=0.9
    )
    
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text='Интерактивное дерево мутаций слов',
                font=dict(size=24, color='#333333'),
                x=0.5,
                xanchor='center'
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=20, r=20, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='#e6f3ff',
            paper_bgcolor='#f0f0f0',
            annotations=annotations,
            # Настройки для масштабирования
            dragmode='zoom',  # Режим по умолчанию — масштабирование
            uirevision='true',  # Сохраняем состояние графа при обновлении
            hoverdistance=100,  # Увеличиваем дистанцию для ховера
            spikedistance=100,  # Увеличиваем дистанцию для спайков
            xaxis_range=None,  # Автоматический диапазон по оси X
            yaxis_range=None,  # Автоматический диапазон по оси Y
            scene=dict(
                aspectmode="data",  # Масштабирование с сохранением пропорций
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.25, y=1.25, z=1.25)
                )
            )
        )
    )

    # Устанавливаем конфигурацию для масштабирования
    config = {
        'scrollZoom': True,  # Включаем масштабирование с помощью колесика мыши
        'displayModeBar': True,  # Показываем панель инструментов
        'modeBarButtonsToAdd': ['zoomIn2d', 'zoomOut2d', 'autoScale2d'],  # Добавляем кнопки масштабирования
        'toImageButtonOptions': {
            'format': 'png',  # Формат изображения для скачивания
            'filename': 'mutation_tree_interactive',
            'height': 600,
            'width': 800,
            'scale': 1
        }
    }

    # Обновляем layout без scrollZoom
    fig.update_layout(
        dragmode='zoom',
        hovermode='closest',
        modebar_add=['zoomIn2d', 'zoomOut2d', 'autoScale2d']
    )

    output_path = os.path.join(output_dir, 'mutation_tree_interactive.html')
    try:
        fig.write_html(output_path, config=config)
        print("Интерактивный граф сохранён по пути:", output_path)
    except Exception as e:
        print("Ошибка при сохранении HTML-файла:", e)
    
    fig.show(config=config)

# Функция для сохранения графа
def save_graph(graph):
    output_dir = os.path.join(os.getcwd(), 'results')
    os.makedirs(output_dir, exist_ok=True)
    graph_path = os.path.join(output_dir, 'mutation_graph.graphml')
    nx.write_graphml(graph, graph_path)
    print(f"Граф сохранён в формате GraphML по пути: {graph_path}")