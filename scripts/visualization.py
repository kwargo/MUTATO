import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from networkx.drawing.nx_agraph import graphviz_layout
import os
from typing import Optional

def plot_mutation_tree_static(graph: nx.DiGraph) -> None:
    """
    Статично визуализирует дерево мутаций слов и сохраняет изображение.

    :param graph: Направленный граф NetworkX с узлами-словами и атрибутами 'pos'.
    :return: None. Сохраняет PNG в папке results/plots.
    """
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

    node_colors = [plt.cm.RdYlGn(depths.get(node, 0) / max_depth) for node in graph.nodes]
    node_sizes = [3000 + 1000 * graph.degree(node) for node in graph.nodes]
    
    edge_colors = []
    for u, v in graph.edges():
        depth_u, depth_v = depths.get(u, 0), depths.get(v, 0)
        avg = (depth_u + depth_v) / 2 / max_depth
        edge_colors.append(plt.cm.coolwarm(avg))
    
    nx.draw_networkx_edges(
        graph, pos,
        edge_color=edge_colors,
        arrows=True,
        arrowstyle='->',
        arrowsize=25,
        width=2,
        alpha=0.7
    )
    nx.draw_networkx_nodes(
        graph, pos,
        node_color=node_colors,
        node_size=node_sizes,
        edgecolors='black',
        linewidths=1.5,
        alpha=0.9
    )
    
    labels = {node: f"{node}\n({graph.nodes[node]['pos']})" for node in graph.nodes}
    nx.draw_networkx_labels(
        graph, pos,
        labels=labels,
        font_size=12,
        font_weight='bold',
        font_family='Arial',
        font_color='black'
    )
    
    edge_labels = {(u, v): graph[u][v]['mutation'] for u, v in graph.edges()}
    nx.draw_networkx_edge_labels(
        graph, pos,
        edge_labels=edge_labels,
        font_size=10,
        font_color='red'
    )
    
    plt.title(
        "Дерево мутаций слов: Эволюция слов",
        fontsize=20,
        pad=30,
        fontweight='bold',
        color='#333333'
    )
    
    sm = plt.cm.ScalarMappable(
        cmap=plt.cm.RdYlGn,
        norm=plt.Normalize(vmin=0, vmax=max_depth)
    )
    plt.colorbar(sm, ax=ax, label='Глубина мутации', shrink=0.5, pad=0.02)
    
    plt.axis('off')
    
    static_path = os.path.join(output_dir, 'mutation_tree_static.png')
    plt.savefig(static_path, dpi=300, bbox_inches='tight')
    print(f"Статичный график сохранён по пути: {static_path}")
    plt.show()


def plot_mutation_tree_interactive(graph: nx.DiGraph) -> None:
    """
    Создаёт интерактивное дерево мутаций с помощью Plotly и сохраняет HTML-файл.

    :param graph: Directed graph NetworkX с узлами и атрибутами 'pos'.
    :return: None. Сохраняет HTML в results/plots.
    """
    if not graph.nodes:
        print("Граф пуст, визуализация невозможна.")
        return

    output_dir = os.path.join(os.getcwd(), 'results', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    
    pos = graphviz_layout(graph, prog='dot', args='-Granksep=3 -Gnodesep=2')
    depths = nx.shortest_path_length(graph, list(graph.nodes)[0]) if graph.nodes else {}
    max_depth = max(depths.values()) if depths else 1
    if max_depth == 0:
        max_depth = 1

    edge_x, edge_y, edge_text = [], [], []
    annotations = []
    for u, v in graph.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        mutation = graph[u][v]['mutation']
        edge_text += [mutation, mutation, None]
        mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
        annotations.append(
            dict(
                x=mid_x,
                y=mid_y,
                xref="x",
                yref="y",
                text=mutation,
                showarrow=False,
                font=dict(size=10, color="red"),
                align="center"
            )
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
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
    node_labels = [f"{node} ({graph.nodes[node]['pos']})" for node in graph.nodes()]
    node_text = [
        f"Слово: {node}<br>Часть речи: {graph.nodes[node]['pos']}<br>"
        f"Глубина: {depths.get(node, 0)}<br>Степень: {graph.degree(node)}"
        for node in graph.nodes()
    ]
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
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
            dragmode='zoom',
            uirevision='true'
        )
    )

    config = {
        'scrollZoom': True,
        'displayModeBar': True,
        'modeBarButtonsToAdd': ['zoomIn2d', 'zoomOut2d', 'autoScale2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'mutation_tree_interactive',
            'height': 600,
            'width': 800,
            'scale': 1
        }
    }

    output_path = os.path.join(output_dir, 'mutation_tree_interactive.html')
    try:
        fig.write_html(output_path, config=config)
        print(f"Интерактивный граф сохранён по пути: {output_path}")
    except Exception as e:
        print("Ошибка при сохранении HTML-файла:", e)
    
    fig.show(config=config)


def save_graph(graph: nx.DiGraph) -> None:
    """
    Сохраняет граф мутаций в формате GraphML.

    :param graph: NetworkX граф мутаций.
    :return: None. Сохраняет файл в папке results.
    """
    output_dir = os.path.join(os.getcwd(), 'results')
    os.makedirs(output_dir, exist_ok=True)
    graph_path = os.path.join(output_dir, 'mutation_graph.graphml')
    nx.write_graphml(graph, graph_path)
    print(f"Граф сохранён в формате GraphML по пути: {graph_path}")