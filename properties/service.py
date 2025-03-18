from extract_param import java, py, js, php, go
from properties import cohesion, coupling, granularity, complexity
from itertools import chain

class Service:
    def __init__(self, name, lang, dir_path):
        self.name = name
        self.lang = lang
        self.dir_path = dir_path
        self.cohesion = {}
        self.coupling = {}
        self.granularity = {}
        self.complexity = {}
        self.set_parse_lang()
        self.set_variable_func()
        self.set_cohesion_metric()
        self.set_granularity_metric()
        self.indirect_coupling = []

    def set_dir_path(self, dir_path):
        if dir_path:
            self.dir_path.append(dir_path)

    def set_ads(self):
        self.coupling['ADS'] = coupling.calculate_ads(self.name, self.called_service)

    def set_ais(self, ais):
        self.coupling['AIS'] = ais

    def set_complexity_factor(self, comf):
        self.complexity['ComF'] = comf

    def set_cohesion_metric(self):
        self.cohesion['LCOM'] = cohesion._calculate_lcom(self.variable_func['functions'])
        self.cohesion['LCOM4'] = cohesion._calculate_lcom4(self.variable_func['functions'])
        self.cohesion['LCOM5'] = cohesion._calculate_lcom5(self.variable_func)
        # self.cohesion['ACOSM'] = cohesion._calculate_acosm(self.variable_func)

    def set_coupling_metric(self):
        self.coupling['ACS'] = coupling._calculate_acs(self.coupling['ADS'], self.coupling['AIS'])

    def set_granularity_metric(self):
        self.granularity['NOO'] = granularity._calculate_noo(self.variable_func['functions'])
        self.granularity['NO nanoentities'] = granularity._calculate_no_nanoentities(self.variable_func)
        self.granularity['LOC'] = granularity._calculate_loc(self.tree_contents)
        self.granularity['SGM'] = granularity._calculate_sgm(self.variable_func['functions'])

    def set_complexity_metric(self):
        self.exposed_function = {key: value for key, value in self.variable_func['functions'].items() if "Http_method" in value.get("local_vars", {})}
        self.complexity['TCM'] = complexity._calculate_tcm(len(self.indirect_coupling), self.coupling['ADS'], 1, len(self.exposed_function))
        self.set_complexity_factor(complexity._calculate_comf(len(self.indirect_coupling), self.coupling['ADS'], 1, len(self.exposed_function)))
        self.complexity['HM'] = complexity._calculate_aggregation_hm(self.variable_func['functions'])
        self.complexity['CC'] = complexity._calculate_avg_ccs(self.variable_func['functions'])
        self.complexity['ICC'] = complexity._calculate_icc(self.variable_func['functions'], self.granularity['LOC'])

    def set_variable_func(self):
        self.tree_contents = self.extract_from_dirs(self.dir_path, self.parser_tree, self.lang)
        self.variable_func = self.parse_function_variable(self.tree_contents)

    def extract_from_dirs(self, dir_paths, parser, lang) -> dict:
        contents = {}
        for dir_path in dir_paths:
            contents.update(self.extract_from_dir(dir_path, parser, lang))

        return contents

    def set_parse_lang(self):
        if self.lang == 'java':
            self.extract_from_dir = java._extract_from_dir
            self.parser_tree = java._parse_tree_content
            self.parse_function_variable = java._parse_function_variable
        elif self.lang == 'py':
            self.extract_from_dir = py._extract_from_dir
            self.parser_tree = py._parse_tree_content
            self.parse_function_variable = py._parse_function_variable
        elif self.lang == 'js':
            self.extract_from_dir = js._extract_from_dir
            self.parser_tree = js._parse_tree_content
            self.parse_function_variable = js._parse_function_variable
        elif self.lang == 'php':
            self.extract_from_dir = php._extract_from_dir
            self.parser_tree = php._parse_tree_content
            self.parse_function_variable = php._parse_function_variable
        elif self.lang == 'go':
            self.extract_from_dir = go._extract_from_dir
            self.parser_tree = go._parse_tree_content
            self.parse_function_variable = go._parse_function_variable

    def print(self):
        print(f"Service Name : {self.name}, Language : {self.lang}")
        self.print_metric()
        print()

    def print_metric(self):
        for key, item in chain(self.cohesion.items(), self.coupling.items(), self.granularity.items(), self.complexity.items()):
            print(f"Metric {key} : {item}")

    def get_called_service(self, service_base_url, service_queue_topic_routing):
        self.called_service = coupling.get_called_service(self.variable_func, service_base_url, service_queue_topic_routing)

    def set_indirect_coupling(self, indirect_coupling):
        self.indirect_coupling = indirect_coupling
