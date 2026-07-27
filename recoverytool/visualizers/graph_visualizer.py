"""Graph Visualizer generating interactive HTML browser visualizations."""
import json
import logging
from pathlib import Path

from recoverytool.graph.scene_graph import SceneGraph

logger = logging.getLogger(__name__)


class GraphVisualizer:
    """Generates interactive HTML visualizations for SceneGraph and DependencyGraph."""

    def __init__(self, scene_graph: SceneGraph):
        self.scene_graph = scene_graph

    def generate_dependency_graph_html(self, output_path: Path | str) -> Path:
        """Generates reports/dependency_graph.html."""
        nodes = []
        edges = []

        color_map = {
            "GameObject": "#4CAF50",
            "Transform": "#2196F3",
            "RectTransform": "#2196F3",
            "MeshFilter": "#FF9800",
            "MeshRenderer": "#FF9800",
            "BoxCollider": "#E91E63",
            "MonoBehaviour": "#9C27B0",
            "Mesh": "#00BCD4",
            "Material": "#FF5722",
            "MonoScript": "#673AB7",
        }

        for n, data in self.scene_graph.graph.nodes(data=True):
            type_name = data.get("type_name", "Unknown")
            name = data.get("name", str(n))
            color = color_map.get(type_name, "#9E9E9E")
            nodes.append(
                {
                    "id": n,
                    "label": f"{name}\n({type_name})",
                    "title": f"PathID: {n} | Type: {type_name}",
                    "color": color,
                    "type": type_name,
                }
            )

        for u, v, k, data in self.scene_graph.graph.edges(keys=True, data=True):
            edges.append(
                {
                    "from": u,
                    "to": v,
                    "label": data.get("rel_type", ""),
                    "arrows": "to",
                }
            )

        html_content = self._build_html_template("Interactive Unity Dependency Graph", nodes, edges)
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(html_content, encoding="utf-8")
        return out_p

    def generate_scene_graph_html(self, output_path: Path | str) -> Path:
        """Generates reports/scene_graph.html."""
        return self.generate_dependency_graph_html(output_path)

    @staticmethod
    def _build_html_template(title: str, nodes: list[dict], edges: list[dict]) -> str:
        nodes_json = json.dumps(nodes)
        edges_json = json.dumps(edges)

        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; background-color: #1e1e1e; color: #ffffff; }}
        #header {{ padding: 15px 20px; background-color: #252526; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #333; }}
        #container {{ display: flex; height: calc(100vh - 65px); }}
        #mynetwork {{ flex: 1; height: 100%; }}
        #sidebar {{ width: 320px; background-color: #252526; border-left: 1px solid #333; padding: 15px; overflow-y: auto; }}
        input, select {{ background: #3c3c3c; border: 1px solid #555; color: white; padding: 8px 12px; border-radius: 4px; font-size: 14px; width: 100%; box-sizing: border-box; margin-bottom: 10px; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; font-weight: bold; }}
    </style>
</head>
<body>
    <div id="header">
        <h2>{title}</h2>
        <div>
            <input type="text" id="search" placeholder="Search by name or PathID..." oninput="filterGraph()">
        </div>
    </div>
    <div id="container">
        <div id="mynetwork"></div>
        <div id="sidebar">
            <h3>Inspector Panel</h3>
            <div id="node-info">Click a node in the graph to inspect properties, components, and dependencies.</div>
        </div>
    </div>

    <script type="text/javascript">
        const rawNodes = {nodes_json};
        const rawEdges = {edges_json};

        const nodes = new vis.DataSet(rawNodes);
        const edges = new vis.DataSet(rawEdges);

        const container = document.getElementById('mynetwork');
        const data = {{ nodes: nodes, edges: edges }};
        const options = {{
            nodes: {{ shape: 'box', font: {{ color: '#ffffff' }} }},
            physics: {{ solver: 'forceAtlas2Based', forceAtlas2Based: {{ gravitationalConstant: -50 }} }}
        }};
        const network = new vis.Network(container, data, options);

        network.on("click", function (params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                document.getElementById('node-info').innerHTML = `
                    <h4>${{node.label}}</h4>
                    <p><b>PathID:</b> ${{node.id}}</p>
                    <p><b>Type:</b> ${{node.type}}</p>
                `;
            }}
        }});

        function filterGraph() {{
            const query = document.getElementById('search').value.toLowerCase();
            if (!query) {{
                nodes.forEach(n => nodes.update({{ id: n.id, hidden: false }}));
                return;
            }}
            nodes.forEach(n => {{
                const match = n.label.toLowerCase().includes(query) || String(n.id).includes(query);
                nodes.update({{ id: n.id, hidden: !match }});
            }});
        }}
    </script>
</body>
</html>
"""
