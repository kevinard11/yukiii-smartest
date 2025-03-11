import os
import java, py, js, php, go
import cohesion, coupling
import json
import yaml
from itertools import chain

class Microservice:
    def __init__(self, name, lang, dir_path):
        self.name = name
        self.lang = lang
        self.dir_path = dir_path
        self.cohesion = {}
        self.coupling = {}
        self.set_parse_lang()
        self.set_variable_func()
        self.set_cohesion_metric()

    def set_dir_path(self, dir_path):
        if dir_path:
            self.dir_path.append(dir_path)

    def set_ads(self):
        self.coupling['ADS'] = coupling.calculate_ads(self.name, self.called_service)

    def set_ais(self, ais):
        self.coupling['AIS'] = ais

    def set_cohesion_metric(self):
        self.cohesion['LCOM'] = cohesion._calculate_lcom(self.variable_func['functions'])
        self.cohesion['LCOM4'] = cohesion._calculate_lcom4(self.variable_func['functions'])
        # self.cohesion['LCOM5'] = cohesion._calculate_lcom5(self.variable_func)
        # self.cohesion['ACOSM'] = cohesion._calculate_acosm(self.variable_func)

    def set_coupling_metric(self):
        self.coupling['ACS'] = coupling._calculate_acs(self.coupling['ADS'], self.coupling['AIS'])
        # print(self.name, self.coupling['ADS'], self.coupling['AIS'])

    def set_variable_func(self):
        self.tree_contents = self.extract_from_dir(self.dir_path, self.parser_tree, self.lang)
        self.variable_func = self.parse_function_variable(self.tree_contents)

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
        print(f"Service Name : {self.name}")
        # print(f"Languages : {self.lang}")
        self.print_cohesion()
        # print(self.tree_contents)
        # print(json.dumps(self.variable_func, indent=2))
        print()

    def print_cohesion(self):
        for key, item in chain(self.cohesion.items(), self.coupling.items()):
            print(f"Metric {key} : {item}")

    def get_called_service(self, service_base_url, service_queue_topic_routing):
        self.called_service = coupling.get_called_service(self.variable_func, service_base_url, service_queue_topic_routing)
        # print(self.name, self.called_service)


class Microservices():
    def __init__(self, name, dir_path):
        self.name = name
        self.dir_path = dir_path
        self.microservices = []
        self.service_base_url = {}
        self.service_queue_key = {}
        self.metric = {
            'Cohesion':{}, 'Coupling':{}, 'Complexity':{}, 'Granularity':{}
        }

    def set_microservices(self, microservice):
        self.microservices.append(microservice)

    def set_service_base_url(self, service_name, base_url):
        self.service_base_url[service_name] = base_url

    def set_service_queue_key(self, service_name, queue_key):
        self.service_queue_key[service_name] = queue_key

    def calculate_metric(self):
        self.calculate_alcom() #ALCOM
        self.calculate_alcom4() #Average LCOM4
        self.calculate_adcs() #ADCS
        self.calculate_scf() #SCF
        self.calculate_aacs() #Average ACS

    def calculate_alcom(self):
        self.metric['Cohesion']['ALCOM']= sum([ms.cohesion['LCOM'] for ms in self.microservices]) / len(self.microservices)

    def calculate_alcom4(self):
        self.metric['Cohesion']['Average LCOM4'] = sum([ms.cohesion['LCOM4'] for ms in self.microservices]) / len(self.microservices)

    def calculate_adcs(self):
        self.metric['Coupling']['ADCS'] = coupling.calculate_adcs(sum([ms.coupling['ADS'] for ms in self.microservices]), len(self.microservices))

    def calculate_scf(self):
        self.metric['Coupling']['SCF'] = coupling.calculate_scf(sum([ms.coupling['ADS'] for ms in self.microservices]), len(self.microservices))

    def calculate_aacs(self):
        self.metric['Coupling']['Average ACS'] = coupling.calculate_aacs(sum([ms.coupling['ACS'] for ms in self.microservices]), len(self.microservices))

    def print_metric(self):
        # print(self.metric)
        for key, aspect in self.metric.items():
            for metric, value in aspect.items():
                print(f"Metrik {key}, {metric}: {value}")

    def print(self):
        print(f"Service Name: {self.name}")
        self.print_metric()
        # print(self.service_base_url)
        # print(self.service_queue_key)
        print()

    def create_microservice(self, name, lang, dir_path=[]):
        if len(dir_path) == 0:
            dir_path = [self.dir_path]

        ms = Microservice(name, lang, dir_path)
        self.set_microservices(ms)

    def print_microservice(self):
        for microservice in self.microservices:
            microservice.print()

    def get_called_services(self):
        for ms in self.microservices:
            ms.get_called_service(self.service_base_url, self.service_queue_key)
            ms.set_ads()

        for ms in self.microservices:
            ais = 0
            for ms1 in self.microservices:
                if ms.name != ms1.name and ms.name in ms1.called_service.keys():
                    ais = ais + 1
            ms.set_ais(ais)
            ms.set_coupling_metric()


def import_config(filepath):
    # read yaml configuration
    config = {}
    with open(filepath, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)

    return config


def main():
    config = import_config("C://Users//ARD//Desktop//robot-shop//yukiii-maqa.yaml")
    mss_name = config['name']
    mss_root_dir = config['root-dir']
    mss = Microservices(mss_name, mss_root_dir)

    for service_key in config['services']:

        service = config['services'][service_key]
        if 'dir' in service:
            dir = mss_root_dir+service['dir']

        if 'lang' in service:
            lang = service['lang']

        mss.create_microservice(service_key, lang, [dir])

        if 'base-url' in service:
            base_url = service['base-url']
            mss.set_service_base_url(service_key, base_url)

        if 'queue-key' in service:
            queue_key = service['queue-key']
            mss.set_service_queue_key(service_key, queue_key)

    mss.get_called_services()
    mss.calculate_metric()
    mss.print()

    for ms in mss.microservices:
        ms.print()

if __name__ == "__main__":
    main()

