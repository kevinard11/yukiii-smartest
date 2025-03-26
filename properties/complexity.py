import math
import json
import networkx as nx

import sys, os
sys.path.append(os.path.abspath("C:/Users/ARD/Desktop/yukiii-smartest"))
from extract_param import java, py, js, php, go

def calculate_halstead_metric(n1, n2, N1, N2):
    # μ = n1 + n2
    miu = n1 + n2
    N = N1 + N2
    # V = N * math.log2(μ) if μ != 0 else 0
    V = N * math.log2(miu) if miu != 0 else 0
    D = (n1 / 2) * (N2 / n2) if n2 != 0 else 0
    E = D * V
    T = E / 18  # Time in seconds
    B = V / 3000  # Estimated bugs

    return {
        "Vocabulary (miu)": miu,
        "Program Length (N)": N,
        "Volume (V)": V,
        "Difficulty (D)": D,
        "Effort (E)": E,
        "Time (T)": T,
        "Estimated Bugs (B)": B
    }

def calculate_halstead_metric_function(functions):
    halstead_metrics = {}
    for key, value in functions.items():
        if 'operands' not in value or 'operators' not in value:
            continue

        operands = value['operands']
        operators = value['operators']
        n1 = len([v for v in operands.values()])
        n2 = len([v for v in operators.values()])
        N1 = len([v for v in operands.keys()])
        N2 = len([v for v in operators.keys()])

        hm = calculate_halstead_metric(n1, n2, N1, N2)
        halstead_metrics[key] = hm
        # print(key, hm, n1, n2, N1, N2)

    return halstead_metrics

def _calculate_aggregation_hm(functions):
    halstead_metric = calculate_halstead_metric_function(functions)
    total_v = sum([v['Volume (V)'] for v in halstead_metric.values()])
    agg_metrics = sum([v['Difficulty (D)'] * v['Volume (V)'] for v in halstead_metric.values()]) / total_v if total_v != 0 else 0

    return agg_metrics

def _calculate_average_agg_hm(total_hm, total_services):
    return total_hm / total_services if total_services != 0 else 0


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
    # print(IC, CM, f, coupf, cohf)
    return coupf / cohf if cohf != 0 else 0

def calculate_coupf(IC, f):
    return IC / (f**2 - f) if (f**2 - f) != 0 else 0

def calculate_cohf(CM, f):
    return CM / (f**2 - f) if (f**2 - f) != 0 else 0

def _calculate_tcm(IC, CM, N, On):
    # print(IC, CM, N, On)
    return (IC + N + On) / CM if CM != 0  else 0

def calculate_cc_function(functions):
    ccs = {}
    for key, value in functions.items():
        if 'edges' not in value or 'nodes' not in value:
            continue

        nodes = value['nodes']
        edges = value['edges']

        cc = calculate_cc(nodes, edges, 1)
        ccs[key] = cc
        # print(key, cc, nodes, edges)

    return ccs

def calculate_cc(nodes, edges, con_com):
    return edges - nodes + (2 * con_com)

def _calculate_avg_ccs(functions):
    ccs = calculate_cc_function(functions)
    avg_cc = sum(ccs.values()) / len(ccs.keys()) if len(ccs.keys()) != 0 else 0

    return avg_cc

def _calculate_avg_ccs_services(total_ccs, total_services):
    return total_ccs / total_services if total_services != 0 else 0

def _calculate_icc(functions, loc):
    total_func = len(functions)
    exec_state = sum([(v['exec_state']) for k,v in functions.items() if 'exec_state' in v])
    total_input = sum([len(v['local_vars']['Parameter']) for k,v in functions.items() if 'Parameter' in v['local_vars']])
    total_output = sum([len(v['local_vars']['Return']) for k,v in functions.items() if 'Return' in v['local_vars']])

    # print(total_func, exec_state, total_input, total_output, loc)

    return (total_func + exec_state + total_input + total_output) / loc if loc != 0 else 0

def _calculate_avg_icc(total_iccs, total_services):
    return total_iccs / total_services if total_services != 0 else 0

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
# dir_path = "C://Users//ARD//Desktop//bqm-repo//agent_management"
# dir_path = "./example/go/rs"
# tree_contents = lang_list[lang]['extract'](dir_path, lang_list[lang]['parse'], lang)
# print(tree_contents)
# variable_func = lang_list[lang]['func'](tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['global_vars'], indent=2))
# print(json.dumps(variable_func['functions'], indent=2))

# ahm = _calculate_aggregation_hm(variable_func['functions'])
# print(ahm)

# avg_cc = _calculate_avg_ccs(variable_func['functions'])
# print(avg_cc)

# icc = _calculate_icc(variable_func['functions'], tree_contents['loc'])
# print(icc)

