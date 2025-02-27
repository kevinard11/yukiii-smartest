import os
import java, py, js, php, go
import cohesion
import json

class Microservice:
    def __init__(self, name, lang, dir_path):
        self.name = name
        self.lang = lang
        self.dir_path = dir_path
        self.cohesion = {}
        self.get_parse_lang()
        self.get_variable_func()
        self.get_cohesion_metric()

    def set_dir_path(self, dir_path):
        if dir_path:
            self.dir_path.append(dir_path)

    def get_cohesion_metric(self):
        self.cohesion['LCOM'] = cohesion._calculate_lcom(self.variable_func['functions'])
        self.cohesion['LCOM4'] = cohesion._calculate_lcom4(self.variable_func['functions'])

    def get_variable_func(self):
        self.tree_contents = self.extract_from_dir(self.dir_path, self.parser_tree, self.lang)
        self.variable_func = self.parse_function_variable(self.tree_contents)

    def extract_from_dir(self, dir_paths, parser, lang) -> dict:
        contents = {}
        for dir_path in dir_paths:
            for dirpath, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    if filename.endswith(f".{lang}"):
                        file_path = os.path.join(dirpath, filename)
                        file_content = parser(file_path)
                        package = dirpath.replace('./','').replace('/','.').replace('\\', '.')

                        if package:
                            key = package + "." + filename.replace(f".{lang}", "")
                        else:
                            key = file_path

                        contents[key] = file_content
            return contents

    def get_parse_lang(self):
        if self.lang == 'java':
            self.parser_tree = java._parse_tree_content
            self.parse_function_variable = java._parse_function_variable
        elif self.lang == 'py':
            self.parser_tree = py._parse_tree_content
            self.parse_function_variable = py._parse_function_variable
        elif self.lang == 'js':
            self.parser_tree = js._parse_tree_content
            self.parse_function_variable = js._parse_function_variable
        elif self.lang == 'php':
            self.parser_tree = php._parse_tree_content
            self.parse_function_variable = php._parse_function_variable
        elif self.lang == 'go':
            self.parser_tree = go._parse_tree_content
            self.parse_function_variable = go._parse_function_variable

    def print(self):
        print(f"Service Name : {self.name}")
        print(f"Languages : {self.lang}")
        self.print_cohesion()
        # print(self.tree_contents)
        # print(json.dumps(self.variable_func, indent=2))

    def print_cohesion(self):
        for key, item in self.cohesion.items():
            print(f"Metric {key} : {item}")

class Microservices():
    def __init__(self, name, dir_path):
        self.name = name
        self.dir_path = dir_path
        self.microservices = []

    def set_microservices(self, microservice):
        self.microservices.append(microservice)

    def calculate_alcom(self):
        self.alcom = sum([ms.cohesion['LCOM'] for ms in self.microservices]) / len(self.microservices)

    def calculate_alcom4(self):
        self.alcom4 = sum([ms.cohesion['LCOM4'] for ms in self.microservices]) / len(self.microservices)

    def print(self):
        print(f"Service Name: {self.name}")
        print(f"ALCOM: {self.alcom}")
        print(f"ALCOM4: {self.alcom4}")

    def create_microservice(self, name, lang, dir_path=[]):
        if len(dir_path) == 0:
            dir_path = [self.dir_path]

        ms = Microservice(name, lang, dir_path)
        self.set_microservices(ms)

    def print_microservice(self):
        for microservice in self.microservices:
            microservice.print()

def main():
    mss = Microservices('robot-shop', "C://Users//ARD//Desktop//robot-shop")
    mss.create_microservice('payment', 'go', ["C://Users//ARD//Desktop//DeathStarBench-master//hotelReservation//services"])
    mss.create_microservice('dispatch','py')
    mss.create_microservice('cart', 'java')
    mss.create_microservice('shipment', 'php', ["C://Users//ARD//Desktop//robot-shop"])
    mss.create_microservice('user', 'js', ["C://Users//ARD//Desktop//robot-shop"])
    mss.print_microservice()
    mss.calculate_alcom()
    mss.calculate_alcom4()
    mss.print()

if __name__ == "__main__":
    main()