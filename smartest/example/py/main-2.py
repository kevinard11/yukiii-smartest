import re
import javalang
import networkx as nx

def java_extract_params(file_path):
    with open(file_path, "r") as f:
        file_contents = f.read()

    func_pattern = re.compile(
        r"(?:"
        # public method
        r"public\s+(\w+)\s*\((.*?)\)|"
        # public static method
        r"public\s*static\s*(?:(?!\bclass\b)\b\w+\b)\s*(\w*)\((.*?)\)|"
        # public type method
        r"public\s*(?:(?!\bclass\b)\b\w+\b)\s*(\w*)\((.*?)\)|"
        # private method
        r"private\s+(\w+)\s*\((.*?)\)|"
        # private static method
        r"private\s*static\s*(?:(?!\bclass\b)\b\w+\b)\s*(\w*)\((.*?)\)|"
        # private type method
        r"private\s*(?:(?!\bclass\b)\b\w+\b)\s*(\w*)\((.*?)\)"
        r")",
        re.DOTALL
    )

    matches = func_pattern.findall(file_contents)

    # print(matches)
    func_params = {}
    for match in matches:
        func_name = match[0] or match[2] or match[4] or match[6] or match[8] or match[10]
        params = match[1] or match[3] or match[5] or match[7] or match[9] or match[11]
        param_list = list(
            filter(lambda x: x != '', [
                p.strip().split(" ")[1]
                for p in params.split(",")
                if p.strip()
            ]))

        # Pada Java mengecualikan setter
        if func_name.startswith("set") and len(param_list) == 1:
            expected_param_name = func_name[3:].lower()
            if param_list[0].lower() == expected_param_name:
                continue

        if len(param_list) != 0:
            func_params[func_name] = param_list

    return func_params


def build_method_graph(methods):
    """ Build a graph where nodes are methods, and edges exist if two methods share attributes. """
    G = nx.Graph()
    method_list = list(methods.keys())

    for i in range(len(method_list)):
        for j in range(i + 1, len(method_list)):
            method1, method2 = method_list[i], method_list[j]
            if methods[method1] & methods[method2]:  # Jika ada atribut yang sama
                G.add_edge(method1, method2)

    # Tambahkan semua metode sebagai node, bahkan jika tidak terhubung
    for method in method_list:
        G.add_node(method)

    return G

def calculate_lcom4(java_code):
    """ Calculate LCOM4 metric from Java source code. """
    # for class_name, data in class_data.items():
    #     G = build_method_graph(data["methods"])
    #     lcom4 = nx.number_connected_components(G)
    #     print(f"LCOM4 for class {class_name}: {lcom4}")

def _extract_params_from_dir(dir_path, parser, lang):
    params_dict = {}
    for dirpath, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename.endswith(f".{lang}"):
                file_path = os.path.join(dirpath, filename)
                params_dict.update(parser(file_path))
    return params_dict

def extract_similarity(model, method_body, similarity_func=compute_cosm_cosine):
    similarities = []
    for (name1, text1), (name2, text2) in combinations(method_body, 2):
            sim = similarity_func(text1, text2, model)
            similarities.append(sim)

    return similarities

def _extract_params_from_dir(dir_path, parser, lang):
    tree_content = {}
    for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                if filename.endswith(f".{lang}"):
                    file_path = os.path.join(dirpath, filename)
                    tree_content[file_path] = parser(file_path)
    return tree_content

def java_parse_tree(file_path) -> any:
    with open(file_path, "r") as f:
        file_contents = f.read()

    return javalang.parse.parse(file_contents)

def java_extract_params(tree_contents):

    class_func_param = {}

    for tree in tree_contents.values():
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_name = node.name
            methods = {}

            for method in node.methods:
                method_name = method.name
                params = [param.name for param in method.parameters]  # Ambil nama parameter
                methods[method_name] = params  # Simpan metode dan parameternya

            class_func_param[class_name] = methods

    return class_func_param

def get_all_params(class_func_param) -> list:
        elements = []
        for clas in class_func_param:
            for function in class_func_param[clas]:
                for param in class_func_param[clas][function]:
                    elements.append(param)
        return elements

def total_all_params(class_func_param) -> int:
    return len(get_all_params(class_func_param))

def get_unique_params(class_func_param) -> set:
    elements = set()
    for clas in class_func_param:
        for function in class_func_param[clas]:
            for param in class_func_param[clas][function]:
                elements.add(param)
    return elements

def total_unique_params(class_func_param) -> int:
    return len(get_unique_params(class_func_param))

def get_all_func(class_func_param) -> list:
    return [method for key in class_func_param for method in class_func_param[key].keys()]

def total_all_func(class_func_param) -> list:
    return len(get_all_func(class_func_param))

def extract_attribute_methods(tree_contents):
    class_data = {}

    for tree in tree_contents.values():
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_name = node.name
            attributes = set()
            methods = {}

            # Extract attributes
            for field in node.fields:
                for declarator in field.declarators:
                    attributes.add(declarator.name)

            # Extract methods and their accessed attributes
            for method in node.methods:
                method_name = method.name
                accessed_attributes = set()
                for _, field_access in method.filter(javalang.tree.MemberReference):
                    if field_access.member in attributes:
                        accessed_attributes.add(field_access.member)
                methods[method_name] = accessed_attributes

            class_data[class_name] = {"attributes": attributes, "methods": methods}

    return class_data

def build_method_graph(methods):
    """ Build a graph where nodes are methods, and edges exist if two methods share attributes. """
    G = nx.Graph()

    method_list = list(methods.keys())

    for i in range(len(method_list)):
        for j in range(i + 1, len(method_list)):
            method1, method2 = method_list[i], method_list[j]
            if methods[method1] & methods[method2]:  # Jika ada atribut yang sama
                G.add_edge(method1, method2)

    # Tambahkan semua metode sebagai node, bahkan jika tidak terhubung
    for method in method_list:
        G.add_node(method)

    return G

def calculate_lcom4(attr_method):
    class_lcom4 = {}
    for class_name, data in attr_method.items():
        G = build_method_graph(data['methods'])
        class_lcom4[class_name] = nx.number_connected_components(G)

    print(class_lcom4)
    return sum(lcom4 for lcom4 in class_lcom4.values())/len(class_lcom4)

def LCOM(class_func_param):
    print(total_all_params(class_func_param), total_unique_params(class_func_param), total_all_func(class_func_param))
    return 1 - (total_all_params(class_func_param) / (total_unique_params(class_func_param) * total_all_func(class_func_param)))

def java_extract_params_return(tree_contents):

    methods = {}
    for tree in tree_contents.values():
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            method_name = node.name
            return_type = node.return_type.name if node.return_type else "void"
            param_types = [param.type.name for param in node.parameters]
            methods[method_name] = {"params": param_types, "return": return_type}

    return methods

def calculate_SIDC(methods):
    # Hitung jumlah pasangan operasi
    method_pairs = list(combinations(methods.keys(), 2))
    total_pairs = len(method_pairs)

    # Hitung Common(Param) dan Common(ReturnType)
    common_params = sum(
        1 for (m1, m2) in method_pairs
        if set(methods[m1]["params"]) & set(methods[m2]["params"])
    )

    common_return = sum(
        1 for (m1, m2) in method_pairs
        if methods[m1]["return"] == methods[m2]["return"]
    )

    return (common_params + common_return) / (total_pairs * 2) if total_pairs > 0 else 0

def java_extract_method_in_class(tree_contents):
    class_methods = set()

    for tree in tree_contents.values():
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            class_methods.add(node.name)

    return class_methods

def java_extract_client_method_calls(tree_contents):

    client_method_calls = defaultdict(set)  # Menyimpan method yang dipanggil per method

    for tree in tree_contents.values():
        for path, node in tree.filter(javalang.tree.MethodInvocation):
            client_method_calls[path[1][0].name].add(node.member)

    return client_method_calls


def calculate_SIUC(client_method_calls, service_methods):
    total_clients = len(client_method_calls)  # Jumlah total metode client yang menggunakan service
    total_service_methods = len(service_methods)  # Jumlah total metode dalam service

    if total_clients > 0 and total_service_methods > 0:
        invoked_operations = sum(len(calls & service_methods) for calls in client_method_calls.values())

        # print(invoked_operations, total_clients, total_service_methods)
        return invoked_operations / (total_clients * total_service_methods)
    else:
        return 0

def java_extract_sequential_calls(tree_contents, service_methods):

    # Simpan pasangan metode yang dipanggil secara berurutan dalam client
    sequential_calls = set()

    for tree in tree_contents.values():
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            method_calls = []

            # Ambil semua pemanggilan metode dalam satu method client
            for _, invocation in node.filter(javalang.tree.MethodInvocation):
                if invocation.member in service_methods:
                    method_calls.append(invocation.member)

            # Buat pasangan urutan panggilan (A → B) termasuk fetchData()
            sequential_calls.update(zip(method_calls, method_calls[1:]))

    return sequential_calls

def calculate_SISC(service_methods, sequential_calls):
    # Hitung Total(SOp(sis)) -> semua pasangan kombinasi unik dalam service
    total_possible_pairs = len(set(combinations(service_methods, 2)))

    # Hitung SISC
    return len(sequential_calls) / total_possible_pairs if total_possible_pairs > 0 else 0

def java_extract_method_depedencies(tree_contents):

    # Parse kode
    method_dependencies = defaultdict(set)

    for tree in tree_contents.values():
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            method_name = node.name  # Nama metode
            for _, invocation in node.filter(javalang.tree.MethodInvocation):
                method_dependencies[method_name].add(invocation.member)  # Tambahkan dependency

    return method_dependencies

def java_extract_shared_elements(method_dependencies):
    shared_elements = defaultdict(int)

    for method1, method2 in combinations(method_dependencies.keys(), 2):
        common_deps = method_dependencies[method1] & method_dependencies[method2]
        for dep in common_deps:
            shared_elements[dep] += 1

    return shared_elements

def java_extract_all_implementation_elements(method_dependencies):
    all_implementation_elements = set()
    for deps in method_dependencies.values():
        all_implementation_elements.update(deps)

    return all_implementation_elements

def calculate_SIIC(shared_elements, all_implementation_elements, service_methods):
    IC_s = len(shared_elements)
    total_possible = len(all_implementation_elements) * len(service_methods)

    return IC_s / total_possible if total_possible > 0 else 0

def calculate_TICS(SIDC, SIUC, SIIC, SISC):
    return (SIDC + SIUC + SIIC + SISC)/4

def extract_methods_body(tree_contents):
    methods = []

    # Ekstrak method signature dan body
    for tree in tree_contents.values():
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            method_signature = f"{node.name}({', '.join([param.type.name for param in node.parameters])})"
            method_body = str(node)
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

def calculate_CCOC(acosm_value):
    # Jika ACOSM > 0, maka COCC = ACOSM, jika tidak, COCC = 0.
    return acosm_value if acosm_value > 0 else 0

def java_extract_service_calls(contents, base_url_dict) -> dict:
    service_calls = {}

    # Regex patterns untuk berbagai pemanggilan service
    patterns = {
        "http_calls": [
            r'\.(?:getForObject|getForEntity|postForObject|postForEntity|exchange)\(\s*["\'](http[s]?://[\w\-\.]+/[\w/\-\.]*)["\']',
            r'WebClient\.create\(\)\.(?:get|post|put|delete)\(\)\.uri\(\s*["\'](http[s]?://[\w\-\.]+/[\w/\-\.]*)["\']',
            r'@FeignClient\s*\(\s*["\']([\w\-\.]+)["\']\s*\).*?\n\s*@(?:GetMapping|PostMapping|PutMapping|DeleteMapping)\(["\'](/[\w/\-\.]*)["\']\)',
        ],
        "rabbitMQ": [
            r'\.(?:convertAndSend|channel\.basicPublish)\(\s*["\']([\w\-\.]+)["\']'
        ]
    }

    for file_path in contents:
        # Menangani HTTP-based service calls
        for pattern in patterns["http_calls"]:
            matches = re.findall(pattern, contents[file_path])
            for match in matches:
                full_url = match if isinstance(match, str) else match[0]

                # Cek apakah full_url cocok dengan salah satu base URL dalam dictionary
                matched_service = next((key for key, base_url in base_url_dict.items() if isinstance(base_url, str) and full_url.startswith(base_url)), None)

                if matched_service:  # Hanya tambahkan jika service ditemukan dalam dictionary
                    if matched_service not in service_calls:
                        service_calls[matched_service] = []
                    service_calls[matched_service].append(full_url)

        # Menangani RabbitMQ Calls
        for pattern in patterns["rabbitMQ"]:
            matches = re.findall(pattern, contents[file_path])
            for match in matches:
                exchange = match  # Nama exchange yang dipublikasikan

                # Cek apakah exchange ada dalam daftar RabbitMQ service
                if "rabbitMQ" in base_url_dict and exchange in base_url_dict["rabbitMQ"]:
                    if "rabbitMQ" not in service_calls:
                        service_calls["rabbitMQ"] = []
                    service_calls["rabbitMQ"].append(exchange)

    return service_calls

def _extract_params_from_dir(dir_path, parser, lang) -> dict:
    contents = {}
    for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                if filename.endswith(f".{lang}"):
                    file_path = os.path.join(dirpath, filename)
                    contents[file_path] = parser(file_path)
    return contents

def java_parse_content(file_path) -> any:
    with open(file_path, "r") as f:
        file_contents = f.read()

    return file_contents
## -------------------------------------------------------------- ##

# tree_contents = _extract_params_from_dir("./java/rs", java_parse_tree, "java")

# class_func_param =  java_extract_params(tree_contents)
# print(class_func_param)
# print(get_all_params(class_func_param))
# print(total_all_params(class_func_param))
# print(get_unique_params(class_func_param))
# print(total_unique_params(class_func_param))
# print(get_all_func(class_func_param))

# print(LCOM(class_func_param))

# attr_method = extract_attribute_methods(tree_contents)
# print(attr_method)
# LCOM4 = calculate_lcom4(attr_method)
# print(LCOM4)

# func_param_return = java_extract_params_return(tree_contents)
# print(func_param_return)

# SIDC = calculate_SIDC(func_param_return)
# print(SIDC)

# method_in_class = java_extract_method_in_class(tree_contents)
# print(method_in_class)

# client_method_calls = java_extract_client_method_calls(tree_contents)
# print(client_method_calls)

# SIUC = calculate_SIUC(client_method_calls, method_in_class)
# print(SIUC)

# sequential_calls =  java_extract_sequential_calls(tree_contents, method_in_class)
# print(sequential_calls)

# SISC = calculate_SISC(method_in_class, sequential_calls)
# print(SISC)

# method_depedencies = java_extract_method_depedencies(tree_contents)
# print(method_depedencies)

# shared_elements = java_extract_shared_elements(method_depedencies)
# print(shared_elements)

# all_implementation_elements = java_extract_all_implementation_elements(method_depedencies)
# print(all_implementation_elements)

# SIIC = calculate_SIIC(shared_elements, all_implementation_elements, method_in_class)
# print(SIIC)

# print(calculate_TICS(SIDC, SIUC, SIIC, SISC))

# method_body = extract_methods_body(tree_contents)
# print(method_body)
# model = train_doc2vec(method_body)
# sim_matrix, pair_indices = extract_similarity(model, method_body, compute_cosm_cosine)
# ACOSM = calculate_ACOSM(sim_matrix, pair_indices)
# print(ACOSM)
# CCOC = calculate_CCOC(ACOSM)
# print(CCOC)
# LCOSM, detail = calculate_LCOSM(sim_matrix, pair_indices, ACOSM)
# print(LCOSM)

