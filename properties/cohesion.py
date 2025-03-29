import networkx as nx

import sys, os
sys.path.append(os.path.abspath("C:/Users/ARD/Desktop/yukiii-smartest"))
from extract_param import java, py, js, php, go

from collections import defaultdict
from itertools import combinations

from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from typing import Dict, Tuple

def get_all_params(functions):
    all_params = []
     # Loop melalui setiap fungsi dalam class
    for func_name, func_data in functions.items():
        for param_name, param_type in func_data['local_vars'].items():
            if param_name == 'Parameter':
                for param in param_type:
                    # print(func_name, param)
                    all_params.append(f"{param['type']} {param['name']}")

    return all_params

def get_unique_params(functions):
    unique_params = set()
     # Loop melalui setiap fungsi dalam class
    for func_name, func_data in functions.items():
        for param_name, param_type in func_data['local_vars'].items():
            if param_name == 'Parameter':
                for param in param_type:
                    unique_params.add(f"{param['type']} {param['name']}")

    return unique_params

def get_all_func(functions):
    all_func = []
     # Loop melalui setiap fungsi dalam class
    for func_name, func_data in functions.items():
        all_func.append(func_name)

    return all_func

def calculate_lcom(total_all_params, total_unique_params, total_all_func):
    # print(total_all_params, total_unique_params, total_all_func)
    return 1 - (total_all_params / (total_unique_params * total_all_func)) if (total_unique_params * total_all_func) > 0 else 0

def get_all_func_params(functions):
    all_func = {}
     # Loop melalui setiap fungsi dalam class
    for func_name, func_data in functions.items():
        all_func_params = []
        for param_name, param_type in func_data['local_vars'].items():
            if param_name == 'Parameter':
                for param in param_type:
                    all_func_params.append(f"{param['type']} {param['name']}")

        all_func[func_name] = all_func_params

    return all_func

def build_function_graph(functions_param):
    """ Build a graph where nodes are methods, and edges exist if two methods share attributes. """
    G = nx.Graph()

    for func_name, func_param in functions_param.items():
        for func_name2, func_param2 in functions_param.items():
            if func_name != func_name2:
                if set(func_param) & set(func_param2):
                    G.add_edge(func_name, func_name2)

    # for func_name in functions_param.keys():
    #     G.add_node(func_name)

    return G

def get_all_class(functions):
    return {item.rsplit('.', 1)[0] for item in functions.keys()}

def get_all_function(functions):
    function = {item.rsplit('.', 1)[-1] for item in functions.keys()}

    # function = {item.rsplit('.', 1)[-1] for item in functions.keys() if not item.rsplit('.', 1)[-1].startswith(("set", "get"))}
    return function

def get_all_other_function(functions):
    function = {item.rsplit('.', 1)[-1] for item in functions.keys()}

    for item in functions.values():
        if 'called_methods' in item.keys():
            for fun in item['called_methods']:
                function.update(fun['method'])

    return function


def get_function_name(function_path):
    return function_path.rsplit('.', 1)[-1]

def get_function_path(function_path):
    return function_path.rsplit('.', 1)[0]

def get_all_func_params_type(functions):
    all_func = {}
     # Loop melalui setiap fungsi dalam class
    for func_name, func_data in functions.items():
        all_func_params_type = []
        for param_name, param_type in func_data['local_vars'].items():
            if param_name == 'Parameter':
                for param in param_type:
                    all_func_params_type.append(param['type'])

        all_func[func_name] = all_func_params_type

    return all_func

def get_all_func_params_type_without_get_set(functions, all_get_set):
    all_func = get_all_func_params_type(functions)

    return {k: v for k, v in all_func.items() if k not in all_get_set}

def get_all_func_return_type_without_get_set(functions, all_get_set):
    all_func = get_all_func_return_type(functions)

    return {k: v for k, v in all_func.items() if k not in all_get_set}

def get_all_get_set_func(functions):
    all_get_set_func = []
     # Loop melalui setiap fungsi dalam class
    for func_name, func_data in functions.items():
        for param_name, param_type in func_data['local_vars'].items():
            if param_name == 'Parameter':
                if len(param_type) == 1:
                    if join_camel_case("set", param_type[0]['name']) == get_function_name(func_name):
                        all_get_set_func.append(func_name)
                        all_get_set_func.append(get_function_path(func_name)+"."+ join_camel_case("get", param_type[0]['name']))

    return all_get_set_func

def join_camel_case(s1, s2):
    return s1.lower() + s2.capitalize()

def get_all_func_return_type(functions):
    all_func = {}
     # Loop melalui setiap fungsi dalam class
    for func_name, func_data in functions.items():
        all_func_return_type = []
        for param_name, param_type in func_data['local_vars'].items():
            if param_name == 'Return':
                for param in param_type:
                    # print(func_name, param)
                    all_func_return_type.append(param['type'])

        all_func[func_name] = all_func_return_type

    return all_func

def calculate_sidc1(method_param, method_return) -> Tuple[float, int, int, int]:

    """Menghitung SIDC1 berdasarkan parameter yang dibagikan antar metode."""
    method_params = method_param.copy()
    method_returns = method_return.copy()

    clean_empty_keys(method_params, method_returns)

    # method_params = {k: v for k, v in method_params.items() if v}
    # method_returns = {k: v for k, v in method_returns.items() if v}
    # print(method_params)

    # Hitung pasangan metode yang memiliki parameter input yang sama
    common_param = get_common_pair(method_params)
    common_return = get_common_pair(method_returns)
    # print(common_param, "\n", common_return)

    if len(common_param) == 0:
        method_params = method_param
        common_param = get_common_pair(method_params)

        method_returns = method_return
        common_return = get_common_pair(method_returns)

    total_combinations = len(list(combinations(list(method_params.keys()), 2))) * 2
    # total_combinations = len(list(combinations(list(method_params.keys()), 2))) + len(list(combinations(list(method_returns.keys()), 2))) # C(n,2) = n(n-1)/2

    sidc1 = (len(common_param) + len(common_return)) / total_combinations if total_combinations > 0 else 0
    if sidc1 > 1:
        sidc1 = 1

    return sidc1, len(common_param), len(common_return), total_combinations

def calculate_sidc(method_param) -> Tuple[float, int, int]:

    param_types = set()

    # Menentukan parameter yang muncul lebih dari sekali
    param_occurrences = defaultdict(int)
    for key, params in method_param.items():
        for param in params:
            param_types.add(param)
            if param in param_occurrences:
                param_occurrences[param] += 1
            else:
                param_occurrences[param] = 1
    total_param_types = len(param_types)

    common_params = {ptype for ptype, count in param_occurrences.items() if count > 1}

    # Hitung SIDC
    sidc = len(common_params) / total_param_types if total_param_types > 0 else 0
    return sidc, len(common_params), total_param_types # Pembulatan 4 desimal

def clean_empty_keys(dict1, dict2):
    """
    Menghapus key yang memiliki list kosong di kedua dictionary.
    """
    keys_to_remove = [key for key in dict1 if not dict1[key] or key in dict2 and not dict2[key]]

    for key in keys_to_remove:
        dict1.pop(key, None)
        dict2.pop(key, None)

    return dict1, dict2

def get_common_pair(list_pair):
    # print(list_pair)
    return [
        (func1, func2) for func1, func2 in combinations(list_pair.keys(), 2)
        if (set(list_pair[func1]) & set(list_pair[func2])) or (list_pair[func1] == [] and list_pair[func2] == [])
    ]

def calculate_siuc(functions, service_operations):
    clients = get_all_client_call(functions, service_operations)
    function = get_all_function_call(functions, service_operations)

    # Step 3: Hitung jumlah total pemanggilan metode dalam service
    total_invoked = sum(len(called_methods) for called_methods in function.values())

    # Step 4: Hitung jumlah total klien dan operasi service
    total_clients = len(clients)
    total_operations = len(service_operations)

    # Step 5: Hitung SIUC menggunakan rumus
    siuc = total_invoked / (total_clients * total_operations) if total_clients > 0 and total_operations > 0 else 0
    return siuc, total_invoked, total_clients, total_operations

def get_all_client_call(functions, service_operations):
    clients = defaultdict(set)
    for client, details in functions.items():
        # print(client, details)
        for call in details["called_methods"]:
            if call["method"] in service_operations:
                clients[client].add(call["method"])

    return clients

def get_all_function_call(functions, service_operations):
    clients = defaultdict(set)
    for client, details in functions.items():
        # print(client, details)
        for call in details["called_methods"]:
            # if call["method"] in service_operations:
            clients[client].add(call["method"])

    return clients

def calculate_sisc(functions, service_operations):
    seq_call = get_all_function_seq_call(functions, service_operations)
    seq_client_call = get_all_client_seq_call(functions, service_operations)

    # Step 3: Hitung jumlah total pasangan metode yang dipanggil secara sekuensial
    # seq_connected = sum(len(called_set) for called_set in seq_call.values())
    seq_connected = len(seq_call)

    # Step 4: Hitung jumlah total kombinasi pasangan metode dalam service
    # total_combinations = len(list(combinations(service_operations, 2)))
    total_combinations = len(service_operations) * len(seq_client_call)

    # Step 5: Hitung SISC menggunakan rumus
    sisc = seq_connected / total_combinations if total_combinations > 0 else 0

    return sisc, seq_connected, total_combinations


def get_all_client_seq_call(functions, service_operations):
    # Step 2: Identifikasi pemanggilan metode secara berurutan
    sequential_calls = defaultdict(set)  # Dictionary untuk menyimpan sequential calls

    for function_name, details in functions.items():
        called_methods = [call["method"] for call in details["called_methods"] if call["method"] in service_operations]

        # Jika ada lebih dari satu metode dipanggil dalam satu function, kita anggap sequential
        for i in range(len(called_methods) - 1):
            sequential_calls[called_methods[i]].add(called_methods[i + 1])

    return sequential_calls

def get_all_function_seq_call(functions, service_operations):
    # Step 2: Identifikasi pemanggilan metode secara berurutan
    sequential_calls = defaultdict(set)  # Dictionary untuk menyimpan sequential calls

    for function_name, details in functions.items():
        called_methods = [call["method"] for call in details["called_methods"]]

        # Jika ada lebih dari satu metode dipanggil dalam satu function, kita anggap sequential
        for i in range(len(called_methods) - 1):
            # print(function_name, called_methods[i], called_methods[i+1])
            sequential_calls[called_methods[i]].add(called_methods[i + 1])

    return sequential_calls

def calculate_siic(functions, service_operations, other_service_operations):
    shared_calls = get_all_function_shared_call(functions, service_operations, other_service_operations)

    IC_s = sum(1 for count in shared_calls.values() if count > 1)
    total_operation = len(service_operations)

    siic = IC_s / total_operation if total_operation > 0  else 0
    # if siic > 1 :
    #     siic = float(1)
    return siic, IC_s, total_operation

def calculate_tics(SIDC, SIUC, SIIC, SISC):
    return (SIDC + SIUC + SIIC + SISC)/4

def get_all_function_shared_call(functions, service_operations, other_service_operations):
    # Step 2: Identifikasi pemanggilan metode secara berurutan
    shared_call = defaultdict(set)  # Dictionary untuk menyimpan sequential calls

    for function_name, details in functions.items():
        if 'called_methods' in details.keys():
            called_methods = [call["method"] for call in details["called_methods"]]
            # called_methods = [call["method"] for call in details["called_methods"] if call['method'] in service_operations]

            # Jika ada lebih dari satu metode dipanggil dalam satu function, kita anggap sequential
            for called_method in called_methods:
                if shared_call[called_method]:
                    shared_call[called_method] += 1
                else:
                    shared_call[called_method] = 1
    # print(shared_call)

    return shared_call

def get_func_body(functions):
    methods = []

    # Ekstrak method signature dan body
    for func_name, func_data in functions.items():
        params = []
        # print(func_data)
        for param_name, param_type in func_data['local_vars'].items():
            if param_name == 'Parameter':
                # print(func_name, param_type)
                for param in param_type:
                    params.append(param['type'])

        method_signature = f"{func_name}({', '.join([param for param in params if param])})"
        method_body = str(func_data.values())
        methods.append((method_signature, method_body))

    return methods

# Latih model Doc2Vec untuk menghasilkan vektor representasi dari methods
def train_doc2vec(methods):
    tagged_data = [TaggedDocument(words=method_body.split(), tags=[method_signature]) for method_signature, method_body in methods]
    model = Doc2Vec(vector_size=100, window=2, min_count=1, workers=4, epochs=100)
    model.build_vocab(tagged_data)
    model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)
    return model

# Fungsi untuk menghitung COSM menggunakan cosine similarity
def compute_cosm_cosine(method1, method2, model):
    vector1 = model.infer_vector(method1.split())
    vector2 = model.infer_vector(method2.split())
    similarity = cosine_similarity([vector1], [vector2])[0][0]
    return similarity

# Fungsi untuk menghitung COSM menggunakan euclidean distance
def compute_cosm_euclidean(method1, method2, model):
    vector1 = model.infer_vector(method1.split())
    vector2 = model.infer_vector(method2.split())
    euclidean_distance = np.linalg.norm(vector1 - vector2)
    similarity = 1 / (1 + euclidean_distance)
    return similarity

def calculate_COSM(model, method_body, similarity_func=compute_cosm_cosine):
    # Pilih dua method yang ingin dibandingkan, misalnya method pertama dan kedua
    method1 = method_body[0][1]  # Method body dari method pertama
    method2 = method_body[1][1]  # Method body dari method kedua

    # Hitung COSM menggunakan cosine similarity
    return similarity_func(method1, method2, model)

def extract_similarity(model, method_body, similarity_func=compute_cosm_cosine):
    n = len(method_body)

    # Hitung matriks similarity (sim_matrix)
    sim_matrix = np.zeros((n, n))
    pair_indices = list(combinations(range(n), 2))
    for i, j in pair_indices:
        sim = similarity_func(method_body[i][1], method_body[j][1], model)
        sim_matrix[i, j] = sim
        sim_matrix[j, i] = sim  # matriks simetri

    return sim_matrix, pair_indices

def calculate_ACOSM(sim_matrix, pair_indices):
    return np.mean([sim_matrix[i, j] for i, j in pair_indices])

def calculate_CCOC(acosm_value):
    # Jika ACOSM > 0, maka COCC = ACOSM, jika tidak, COCC = 0.
    return acosm_value if acosm_value > 0 else 0

def calculate_LCOSM(sim_matrix, pair_indices, ACOSM):
    # Bentuk himpunan M untuk setiap metode: M[i] = { j | j != i dan sim_matrix[i,j] > acosm }
    M = []
    n, _ = sim_matrix.shape
    for i in range(n):
        similar_set = set()
        for j in range(n):
            if i != j and sim_matrix[i, j] > ACOSM:
                similar_set.add(j)
        M.append(similar_set)

    # Bentuk himpunan P dan Q: untuk setiap pasangan (i, j) dengan i < j
    P = []
    Q = []
    for i, j in pair_indices:
        if M[i].intersection(M[j]) == set():
            P.append((i, j))
        else:
            Q.append((i, j))

    total_pairs = len(pair_indices)

    # Hitung LCOSM sesuai definisi
    if len(P) > len(Q):
        LCOSM = (len(P) - len(Q)) / total_pairs
    else:
        LCOSM = 0

    details = {
        'M_sets': M,
        'P_pairs': P,
        'Q_pairs': Q
    }
    return LCOSM, details

def _calculate_lcom(functions):
    all_params = get_all_params(functions)
    unique_params = get_unique_params(functions)
    all_func = get_all_func(functions)
    lcom = calculate_lcom(len(all_params), len(unique_params), len(all_func))

    return lcom

def _calculate_alcom(total_lcom, total_services):
    return total_lcom / total_services if total_services != 0 else 0

def _calculate_lcom4(functions):

    all_func_param = get_all_func_params(functions)
    # print(len(all_func_param))
    G = build_function_graph(all_func_param)
    connected_component = nx.number_connected_components(G)

    # all_class = get_all_class(functions)

    return connected_component

def _calculate_avg_lcom4(total_lcom4, total_services):
    return total_lcom4 / total_services if total_services != 0 else 0

def _calculate_acosm(variable_func):
    method_body = get_func_body(variable_func["functions"])
    model = train_doc2vec(method_body)
    sim_matrix, pair_indices = extract_similarity(model, method_body, compute_cosm_cosine)

    acosm = calculate_ACOSM(sim_matrix, pair_indices)
    return acosm

def _calculate_lcom5(variable_func):
    variables = variable_func["global_vars"]
    # print(variables)
    functions = variable_func["functions"].copy()
    lcom5_class = {}

    all_class = get_all_class(functions)
    for class_name in all_class:

        variable = {k: v for k,v in variables.items() if '.'.join(k.split('.')[:-1]) == class_name}
        function = {k: v for k, v in functions.items() if '.'.join(k.split('.')[:-1]) == class_name}
        lcom5 = calculate_lcom5(variable, function)
        # print(class_name, lcom5)
        if lcom5[0] != float('inf'):
            lcom5_class[class_name] = lcom5[0]
        else:
            lcom5_class[class_name] = 1

    # print(len(lcom5_class))

    average_lcom5 = sum(k for k in lcom5_class.values()) / len(lcom5_class) if len(lcom5_class) != 0 else 0
    return average_lcom5 if average_lcom5 <= 1 else 1


def calculate_lcom5(variable, function):

    # Hitung jumlah akses unik ke atribut (a)
    global_vars_key = [d.split('.')[-1] for d in variable.keys()]
    accessed_attribute = {}
    non_access_method = []

    for method, details in function.items():
        accessed_attribute_per_method = set()
        if "called_methods" in details:
            for call in details["called_methods"]:
                if "arguments" in call:
                    for argument in call["arguments"]:
                        if argument in global_vars_key:
                            accessed_attribute_per_method.add(argument)

                # print(call['qualifier'].split('.')[0] if call['qualifier'] else call['qualifier'])

                if "qualifier" in call and call['qualifier'] and call["qualifier"].split('.')[0] in global_vars_key:
                    # print(call['qualifier'])
                    accessed_attribute_per_method.add(call["qualifier"])

        if 'local_vars' in details:
            for var in details['local_vars'].keys():
                if var in global_vars_key:
                    accessed_attribute_per_method.add(var)

        if accessed_attribute_per_method:
            accessed_attribute[method] = accessed_attribute_per_method
        else:
            non_access_method.append(method)

    # function = {k: v for k, v in function.items() if k not in non_access_method}

    a = sum(len(v) for v in accessed_attribute.values())
    l = len(variable)
    k = len(function)

    if k == 1 or l == 0:
        a = 0
        lcom5 = float('inf')
    else:
        if a == 0:
            lcom5 = 1
        else:
            lcom5 = (a - (k*l)) / (l - (k*l)) if (l - (k*l)) != 0 else float('inf')
            if lcom5 == -0.0:
                lcom5 = 0

    return lcom5, a, k, l

def _calculate_avg_lcom5(total_lcom5, total_services):
    return total_lcom5 / total_services if total_services != 0 else 0


## ------------------------------------------------------------------- ##
'''Run command'''
lang_list = {
    'java': {'lang': 'java', 'extract': java._extract_from_dir, 'parse' : java._parse_tree_content, 'func': java._parse_function_variable},
    'py': {'lang': 'py', 'extract': py._extract_from_dir, 'parse' : py._parse_tree_content, 'func': py._parse_function_variable},
    'js': {'lang': 'js', 'extract': js._extract_from_dir, 'parse' : js._parse_tree_content, 'func': js._parse_function_variable},
    'php': {'lang': 'php', 'extract': php._extract_from_dir, 'parse' : php._parse_tree_content, 'func': php._parse_function_variable},
    'go': {'lang': 'go', 'extract': go._extract_from_dir, 'parse' : go._parse_tree_content, 'func': go._parse_function_variable}
}

# lang = 'java'

# dir_path = "D://DATA//java//intellij//bravo-branch-service"
# dir_path = 'C://Users//ARD//Desktop//DeathStarBench-master//hotelReservation//services'
# dir_path = "C://Users//ARD//Desktop//robot-shop//shipping"
# dir_path = "./example/java/rs"
# dir_path = "C://Users//ARD//Desktop//train-ticket//ts-verification-code-service//src//main"

# tree_contents = lang_list[lang]['extract'](dir_path, lang_list[lang]['parse'], lang)
# print(tree_contents)
# variable_func = lang_list[lang]['func'](tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['global_vars'], indent=2))
# print(json.dumps(variable_func['functions'], indent=2))

# all_params = get_all_params(variable_func["functions"])
# print(all_params)

# unique_params = get_unique_params(variable_func["functions"])
# print(unique_params)

# all_func = get_all_func(variable_func["functions"])
# print(all_func)

# lcom = _calculate_lcom(variable_func["functions"])
# print(lcom)

# lcom4 = _calculate_lcom4(variable_func["functions"])
# print(lcom4)

# lcom5 = calculate_lcom5(variable_func['global_vars'], variable_func['functions'])
# lcom5 = _calculate_lcom5(variable_func)
# print(lcom5)

# all_get_set_func = get_all_get_set_func((variable_func["functions"]))
# print(all_get_set_func)

# all_func_params_type = get_all_func_params_type(variable_func["functions"])
# print(all_func_params_type)

# all_func_params_type_without_get_set = get_all_func_params_type_without_get_set(variable_func["functions"], all_get_set_func)
# print(all_func_params_type_without_get_set)

# all_func_return_type = get_all_func_return_type(variable_func["functions"])
# print(all_func_return_type)

# all_func_return_type_without_get_set = get_all_func_return_type_without_get_set(variable_func["functions"], all_get_set_func)
# print(all_func_return_type_without_get_set)

# sidc = calculate_sidc(all_func_params_type)
# print(sidc)

# sidc1 = calculate_sidc1(all_func_params_type, all_func_return_type)
# print(sidc1)

# service_operations = get_all_function(variable_func["functions"])
# other_service_operations = get_all_other_function(variable_func['functions'])
# print(service_operations)
# siuc = calculate_siuc(variable_func["functions"], service_operations)
# print(siuc)

# sisc = calculate_sisc(variable_func["functions"], service_operations)
# print(sisc)

# siic = calculate_siic(variable_func["functions"], service_operations, other_service_operations)
# print(siic)

# tics = calculate_tics(sidc[0], siuc[0], siic[0], sisc[0])
# print(tics)

# method_body = get_func_body(variable_func["functions"])
# print(method_body)
# model = train_doc2vec(method_body)
# sim_matrix, pair_indices = extract_similarity(model, method_body, compute_cosm_cosine)

# ACOSM = calculate_ACOSM(sim_matrix, pair_indices)
# print(ACOSM)

# CCOC = calculate_CCOC(ACOSM)
# print(CCOC)

# LCOSM, detail = calculate_LCOSM(sim_matrix, pair_indices, ACOSM)
# print(LCOSM)






