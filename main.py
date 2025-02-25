import os
import java, py, js, php, go
import cohesion
import json

class Microservice:
    def __init__(self, name, lang):
        self.name = name
        self.lang = lang
        self.cohesion = {}
        self.get_parse_lang()
        self.get_variable_func()
        self.get_cohesion_metric()

    def get_cohesion_metric(self):
        self.cohesion['LCOM'] = cohesion._calculate_lcom(self.variable_func['functions'])

    def get_variable_func(self):
        self.tree_contents = self.extract_from_dir(f'./{self.lang}/rs', self.parser_tree, self.lang)
        self.variable_func = self.parse_function_variable(self.tree_contents)

    def extract_from_dir(self, dir_path, parser, lang) -> dict:
        contents = {}
        for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                # print(filename)
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
        print(f"LCOM : {self.cohesion['LCOM']}")
        # print(self.tree_contents)
        # print(self.variable_func['functions']['rabbitReady'])
        # print(json.dumps(self.variable_func, indent=2))

def main():
    ms = Microservice('dispatch','py')
    ms.print()

if __name__ == "__main__":
    main()