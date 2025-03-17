import java, py, js, php, go
import math
import json
import networkx as nx

def calculate_halstead_metrics(n1, n2, N1, N2):
    μ = n1 + n2
    N = N1 + N2
    V = N * math.log2(μ) if μ != 0 else 0
    D = (n1 / 2) * (N2 / n2) if n2 != 0 else 0
    E = D * V
    T = E / 18  # Time in seconds
    B = V / 3000  # Estimated bugs

    return {
        "Vocabulary (μ)": μ,
        "Program Length (N)": N,
        "Volume (V)": V,
        "Difficulty (D)": D,
        "Effort (E)": E,
        "Time (T)": T,
        "Estimated Bugs (B)": B
    }


def get_indirect_coupling(graph):
    IC = {}

    for node in graph.nodes:
        # Find all nodes reachable from the current node (excluding itself)
        reachable_nodes = set(nx.descendants(graph, node))
        IC[node] = reachable_nodes

    return IC

def _calculate_comf(IC, CM, N, On):
    f = N + On
    coupf = calculate_coupf(IC, f)
    cohf = calculate_cohf(CM, f)
    return coupf / cohf if cohf != 0 else 0

def calculate_coupf(IC, f):
    return IC / (f**2 - f) if (f**2 - f) != 0 else 0

def calculate_cohf(CM, f):
    return CM / (f**2 - f) if (f**2 - f) != 0 else 0

def _calculate_tcm(IC, CM, N, On):
    # print(IC, CM, N, On)
    return (IC + N + On) / CM if CM != 0  else 0

# def get_operands_and_operators

'''Run command'''
lang_list = {
    'java': {'lang': 'java', 'extract': java._extract_from_dir, 'parse' : java._parse_tree_content, 'func': java._parse_function_variable},
    'py': {'lang': 'py', 'extract': py._extract_from_dir, 'parse' : py._parse_tree_content, 'func': py._parse_function_variable},
    'js': {'lang': 'js', 'extract': js._extract_from_dir, 'parse' : js._parse_tree_content, 'func': js._parse_function_variable},
    'php': {'lang': 'php', 'extract': php._extract_from_dir, 'parse' : php._parse_tree_content, 'func': php._parse_function_variable},
    'go': {'lang': 'go', 'extract': go._extract_from_dir, 'parse' : go._parse_tree_content, 'func': go._parse_function_variable}
}

lang = 'java'
# dir_path = "D://DATA//java//intellij//bravo-branch-service//src//main"
# dir_path = 'C://Users//ARD//Desktop//DeathStarBench-master//hotelReservation//services'
# dir_path = "C://Users//ARD//Desktop//robot-shop"
dir_path = "./java/rs"
tree_contents = lang_list[lang]['extract'](dir_path, lang_list[lang]['parse'], lang)
# print(tree_contents)
variable_func = lang_list[lang]['func'](tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['global_vars'], indent=2))
# print(json.dumps(variable_func['functions'], indent=2))
