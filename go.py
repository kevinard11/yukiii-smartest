import re
import os
import json

from typing import Dict, Tuple, List
from tree_sitter import Language, Parser

def _extract_from_dir(dir_path, parser, lang) -> dict:
    contents = {}
    for dirpath, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename.endswith(f".{lang}"):
                file_path = os.path.join(dirpath, filename)
                file_content = parser(file_path)
                # package = _parse_tree_package(file_content)
                package = dirpath.replace('./','').replace('/','.').replace('\\', '.').replace('..','.').replace(':','')

                if package:
                    key = package + "." + filename.replace(f".{lang}", "")
                else:
                    key = file_path

                contents[key] = file_content
    return contents

def _parse_content(file_path) -> any:
    with open(file_path, "r") as f:
        file_contents = f.read()

    return file_contents

def _parse_tree_content(file_path) -> any:
    file_contents = _parse_content(file_path)

    parser = Parser()
    parser.set_language(GO_LANGUAGE)

    return parser.parse(file_contents.encode('utf8'))

def get_value(node):
    # print(node.type)
    if node.type == 'int_literal':
        return int(node.text.decode())
    elif node.type == 'literal_element':
        return get_value(node.children[0])
    elif node.type in ['true', 'false', 'interpreted_string_literal', 'rune_literal', 'identifier', 'selector_expression', 'type_identifier', 'index_expression']:
        return node.text.decode()
    elif node.type == 'float_literal':
        return float(node.text.decode())
    elif node.type == 'composite_literal':
        if node.child_by_field_name("type").type == 'slice_type':
            array_value = []
            for child in node.children[1].children:
                if child.type == 'literal_element':
                    array_value.append(child.text.decode())
            return array_value
        elif node.child_by_field_name("type").type == 'map_type':
            map_values = {}
            elements_node = node.child_by_field_name("body")
            if elements_node:
                for child in elements_node.children:
                    if child.type == "keyed_element":  # Key-value pair
                        key = get_value(child.children[0])
                        value = get_value(child.children[2])
                        map_values[key] = value
            return map_values
    elif node.type == 'call_expression':
        qualifier = ''
        function_name = ''
        arguments_nodes = []

        for child in node.children:
            if child.type == 'selector_expression':
                selector = child.text.decode().split('.')
                function_name = selector[-1]
                qualifier = '.'.join(selector[:-1])
            elif child.type == 'identifier':
                function_name = get_value(child)
            elif child.type == 'argument_list':
                for child2 in child.children[1:-1]:
                    if child2.text.decode() != ',':
                        arguments_nodes.append(get_value(child2))

        # print(function_name, qualifier, arguments_nodes)

        return {
            "method": function_name,
            "arguments": arguments_nodes,
            "qualifier": qualifier
        }
     # Unary expressions (contoh: -5, +10, !flag)
    elif node.type == 'unary_expression':
        operator = node.child(0).text.decode()
        operand = get_value(node.child(1))
        return f"{operator}{operand}"

    # Binary expressions (contoh: a + b, x * y)
    elif node.type == 'binary_expression':
        left = get_value(node.child(0))
        operator = node.child(1).text.decode()
        right = get_value(node.child(2))
        return f"({left} {operator} {right})"

    elif node.type == 'type_assertion_expression':
        qualifier = ''
        function_name = ''
        arguments_nodes = []

        for child in node.children:
            if child.type == 'identifier':
                function_name = get_value(child)
            elif child.type == 'index_expression':
                function_name = get_value(child)
            else:
                # argument = get_value(child)
                arguments_nodes.append(child.text.decode())
        return {
            "method": function_name,
            "arguments": "".join(arguments_nodes[2:-1]),
            "qualifier": qualifier
        }
    return None

def _parse_function_variable(tree_contents) -> Tuple[dict, dict]:

    global_vars = {}
    functions = {}

    for key, tree in tree_contents.items():
        global_var = get_global_variables(tree.root_node, key)
        global_vars.update(global_var)

        # called_method = get_global_called_methods(tree.root_node, key)
        # global_vars[f"{key}.called_methods"] = (called_method)

        function = get_functions(tree.root_node, key)
        # print(function)

        functions.update(function)

    variable_func = {
        'global_vars': global_vars,
        'functions': functions
    }

    return variable_func

def get_var_spec_name_value(node):
    var_name = ''
    var_value = None
    if node.type == 'var_spec':
        for child1 in node.children:
            # print(child1.type, child1.text.decode())
            if child1.type == 'identifier':
                var_name = child1.text.decode()  # Nama variable
            elif child1.type == 'expression_list':
                var_value = get_value(child1.children[0])

    return var_name, var_value

def get_global_variables(head_node, scope):
    """
    Menganalisis kode Go untuk menemukan global variables dan method calls.
    - Jika di luar struct, path = filename.
    - Jika dalam struct, path = filename + "." + struct_name.
    """
    global_vars = {}
    called_methods = []

    for node in head_node.children:
        value = None
        var_name = ''
        var_value = None
        if node.type == "var_declaration":  # Global variable

            for child in node.children:
                # print(child)
                if child.type == 'var_spec':
                    var_name, var_value = get_var_spec_name_value(child)
                    global_vars[f"{scope}.{var_name}"] = var_value

                elif child.type == 'var_spec_list':
                    for child1 in child.children:
                        if child1.type == 'var_spec':
                            var_name, var_value = get_var_spec_name_value(child1)
                            global_vars[f"{scope}.{var_name}"] = var_value
                            # print(var_name, var_value)
        elif node.type =='expression_statement':
            for child in node.children:
                if child.type == 'call_expression':
                    called_method = get_value(child)
                    called_methods.append(called_method)

        elif node.type == "assignment_statement":  # Assignment (logger = LoggerFactory.getLogger(...))
            var_name = node.children[0].text.decode()
            value_node = node.children[-1]
            value = extract_method_call(value_node) if value_node else value_node.text.decode("utf8") if value_node else None

            global_vars[f"{scope}.{var_name}"] = value or None

        elif node.type == "type_declaration":  # Structs (untuk field struct)
            for child in node.children:
                # print(child.type)
                if child.type == 'type_spec':
                    for child1 in child.children:
                        # print(child1.type)
                        if child1.type == 'type_identifier':
                            struct_name = f'{scope}.{child1.text.decode()}'
                        elif child1.type == 'struct_type':
                            # print(child1.children)
                            for child2 in child1.children:
                                if child2.type == 'field_declaration_list':
                                    for child3 in child2.children:
                                        if child3.type == 'field_declaration':
                                            # print(child3.children)
                                            for child4 in child3.children:
                                                if child4.type == 'field_identifier':
                                                    var_name = child4.text.decode()
                                                elif child4.type == 'raw_string_literal':
                                                    # print(child4.children)
                                                    for child5 in child4.children:
                                                        if child5.type == 'raw_string_literal_content':
                                                            var_value = child5.text.decode().replace('default:', '')
                                                global_vars[f"{struct_name}.{var_name}"] = var_value


    global_vars[f"{scope}.called_methods"] = called_methods
    return global_vars


def extract_method_call(node):
    if node.type == "call_expression":
        method_node = node.child_by_field_name("function")
        args_node = node.child_by_field_name("arguments")

        if method_node and "." in method_node.text.decode("utf8"):
            qualifier, method = method_node.text.decode("utf8").rsplit(".", 1)

            arguments = []
            if args_node:
                for arg in args_node.children:
                    if arg.type != ",":
                        arguments.append(arg.text.decode("utf8"))

            return {
                "qualifier": qualifier,
                "method": method,
                "arguments": arguments
            }
    return None

def get_type_value(node):
    if node.type in ['type_identifier', 'pointer_type', 'qualified_type']:
        return node.text.decode()
    elif node.type == 'slice_type':
        return'array'
    elif node.type == 'map_type':
        return 'map'

def get_functions(head_node, scope):

    functions = {}

    for node in head_node.children:
        full_func_name = ''
        local_vars = {}
        called_methods = []

        if node.type == 'function_declaration':
            params = []
            return_type = []
            # print(node.children) # identifier parameter_list pointer_type/qualified_type block
            for child in node.children:
                if child.type == 'identifier':
                    full_func_name = f"{scope}.{child.text.decode()}"
                    # print(full_func_name)
                elif child.type == 'parameter_list':
                    # print(child.children)
                    if len(params) == 0:
                        for child1 in child.children:
                            if child1.type == 'parameter_declaration':
                                type = None
                                name = None
                                # print(child.text.decode(), child1.children)
                                for child2 in child1.children:
                                    if child2.type == 'identifier':
                                        name = child2.text.decode()
                                    else:
                                        type = get_type_value(child2)
                                res = {
                                    'type': type,
                                    'name': name
                                }
                                # print(res)
                                params.append(res)

                        local_vars['Parameter'] = params
                    else :
                        for child1 in child.children:
                            if child1.type == 'parameter_declaration':
                                type = None
                                # print(child.text.decode(), child1.children)
                                for child2 in child1.children:
                                    # print(child1.text.decode(), child2)
                                    type = get_type_value(child1)
                                res = res = {
                                    'type': type
                                }
                                # print(res)
                                return_type.append(res)
                elif child.type  in ['qualified_type', 'pointer_type', 'type_identifier']:
                    return_type.append({
                                    'type': child.text.decode()
                                })
                    # print(child.children)
                elif child.type == 'block':
                    get_blocks(child, local_vars, called_methods,full_func_name)

                local_vars['Return'] = return_type

        elif node.type == 'method_declaration':
            # print(node.children) # parameter_list field_identifier pointer_type/qualified_type block params = []
            return_type = []
            params = []

            for child in node.children:

                if child.type == 'parameter_list':
                    if full_func_name == '':
                        for child1 in child.children:
                            if child1.type == 'parameter_declaration':
                                for child2 in child1.children:
                                    if child2.type == 'type_identifier':
                                        full_func_name = f"{scope}.{child2.text.decode()}"
                    elif len(params) == 0 and len(full_func_name) > 0:
                        for child1 in child.children:
                            if child1.type == 'parameter_declaration':
                                type = None
                                name = None
                                # print(child.text.decode(), child1.children)
                                for child2 in child1.children:
                                    # print(child1.text.decode(), child2)
                                    if child2.type == 'identifier':
                                        name = child2.text.decode()
                                    elif child2.type == 'type_identifier':
                                        type = child2.text.decode()
                                    elif child2.type == 'pointer_type':
                                        type = child2.text.decode()
                                res = {
                                    'type': type,
                                    'name': name
                                }
                                # print(res)
                                params.append(res)

                        local_vars['Parameter'] = params
                    elif len(params) > 0 and len(full_func_name) > 0:
                        for child1 in child.children:
                            if child1.type == 'parameter_declaration':
                                type = None
                                name = None
                                # print(child.text.decode(), child1.children)
                                for child2 in child1.children:
                                    # print(child1.text.decode(), child2)
                                    if child2.type in ['type_identifier', 'pointer_type']:
                                        type = child2.text.decode()
                                res = res = {
                                    'type': type
                                }
                                # print(res)
                                return_type.append(res)

                elif child.type == 'field_identifier' and len(full_func_name) > 0:
                    full_func_name = f"{full_func_name}.{child.text.decode()}"
                    # print(full_func_name)

                elif child.type  in ['qualified_type', 'pointer_type', 'type_identifier']:
                    return_type.append({
                                    'type': child.text.decode()
                                })
                    # print(child.children)

                local_vars['Return'] = return_type


        # print(full_func_name, local_vars)

        if full_func_name:
            functions[full_func_name] = {
                key: value for key, value in {
                    "local_vars": local_vars,
                    "called_methods": called_methods
                }.items() if value is not None
            }

    return functions

def get_blocks(node, local_vars, called_methods, full_func_name):
    if node.type == 'block':
        for child1 in node.children:
            # print(child1)
            if child1.type in ['assignment_statement', 'short_var_declaration']:
                for child2 in child1.children:
                    # print(child2)
                    if child2.type == 'expression_list':
                        var_value = None
                        # print(child2.text.decode())
                        for child3 in child2.children:
                            # print(child3)
                            if child3.type == 'identifier':
                                full_func_name = child3.text.decode()
                            else:
                                var_value = get_value(child3)

                            if child3.type == 'call_expression':
                                res = get_value(child3)
                                res['assigned_to'] = full_func_name
                                called_methods.append(res)
                        # print(full_func_name, var_value)
                        local_vars[full_func_name] = var_value

            elif child1.type in ['expression_statement', 'defer_statement']:
                for child2 in child1.children:
                    if child2.type == 'call_expression':
                        res = get_value(child2)
                        called_methods.append(get_value(child2))
            elif child1.type == 'for_statement':
                for child2 in child1.children:
                    if child2.type == 'block':
                        get_blocks(child2, local_vars, called_methods, full_func_name)
                    if child2.type == 'if_statement':
                        get_ifelse_while_for(child2, local_vars, called_methods, full_func_name)
            elif child1.type == 'if_statement':
                get_ifelse_while_for(child1, local_vars, called_methods, full_func_name)

def get_ifelse_while_for(node, local_vars, called_methods, full_func_name):
    if node.type == 'if_statement':
        # print(node.children)
        for child in node.children:
            if child.type == 'call_expression':
                called_methods.append(get_value(child))
            if child.type == 'block':
                get_blocks(child, local_vars, called_methods, full_func_name)
            elif child.type == 'if_statement':
                get_ifelse_while_for(child, local_vars, called_methods, full_func_name)

GO_LANGUAGE = Language('build/my-languages.so', 'go')

# tree_contents = _extract_from_dir("./go/test", _parse_tree_content, "go")
# print(tree_contents)
# variable_func = _parse_function_variable(tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['global_vars'], indent=2))
# print(json.dumps(variable_func['functions'], indent=2))