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
                package = dirpath.replace('./','').replace('/','.').replace('\\', '.')

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
    parser.set_language(PHP_LANGUAGE)

    return parser.parse(file_contents.encode('utf8'))

def get_node_value_type(value_node):
    """Menentukan tipe dari nilai dalam PHP"""
    if value_node is None:
        return "Unknown Type"
    if value_node.type == "string":
        return "str"
    elif value_node.type == "integer":
        return "int"
    elif value_node.type in ["true", "false", "boolean"]:
        return "boolean"
    elif value_node.type == "array_creation_expression":
        return "List"
    elif value_node.type == "object_creation_expression":
        return "Object"
    elif value_node.type == "identifier":
        return value_node.text.decode()
    else:
        return "Unknown Type"

def get_value_type(value_node):
    """Menentukan tipe dari value langsung"""
    if isinstance(value_node, str):  # Cek jika string
        return "String"
    elif isinstance(value_node, (int, float)):  # Cek jika angka (int atau float)
        return "Number"
    elif isinstance(value_node, bool):  # Cek jika boolean
        return "Boolean"
    elif isinstance(value_node, list):  # Cek jika array/list
        return "List"
    elif isinstance(value_node, dict):  # Cek jika object/dictionary
        return "Dict"
    elif isinstance(value_node, tuple):  # Cek jika tuple
        return "Tuple"
    else:
        return "Unknown Type"

def _parse_function_variable(tree_contents) -> Tuple[dict, dict]:

    global_vars = {}
    functions = {}

    for key, tree in tree_contents.items():
        global_var = get_global_variables(tree.root_node, key)
        global_vars.update(global_var)

        called_method = get_global_called_methods(tree.root_node, key)
        global_vars[f"{key}.called_methods"] = (called_method)

    for key, tree in tree_contents.items():
        function = get_functions(tree.root_node, global_vars, key)
        # print(function)
        function1 = get_class_functions(tree.root_node, global_vars, key)
        # print(function1)

        functions.update(function)
        functions.update(function1)

    variable_func = {
        'global_vars': global_vars,
        'functions': functions
    }

    return variable_func

def get_global_variables(node, scope):
    """Mencari variabel global dalam PHP"""
    global_vars = {}

    for child in node.children:
        if child.type == "expression_statement":
            expr = child.children[0] if len(child.children) > 0 else None
            if expr.type == "assignment_expression":
                var_name = expr.child_by_field_name("left")
                var_value = expr.child_by_field_name("right")
                if var_name and not is_inside_function(child):
                    full_var_name = f"{scope}.{var_name.text.decode()}"
                    # Jika variabel adalah hasil pemanggilan fungsi
                    if var_value and var_value.type == "function_call_expression":
                        global_vars[full_var_name] = get_calls(var_value)
                    elif var_value and var_value.type == "member_call_expression":
                        global_vars[full_var_name] = get_member_calls(var_value)
                    # Jika variabel bukan hasil pemanggilan fungsi, simpan nilainya langsung
                    elif var_value and var_value.type == "variable_name":
                        global_vars[full_var_name] = var_value.text.decode()
                    else:
                        global_vars[full_var_name] = get_value(var_value)
        elif child.type == "class_declaration":
            scope_temp = scope
            for child1 in child.children:
                if child1.type == 'name':
                    scope = f'{scope_temp}.{child1.text.decode()}'
                elif child1.type == "declaration_list":
                    for child2 in child1.children:
                        if child2.type == 'property_declaration':
                            is_global = False
                            for child3 in child2.children:
                                if child3.type == 'visibility_modifier':
                                    if(child3.text.decode() == 'public'):
                                        is_global = True
                                elif child3.type == 'property_element':
                                    if is_global:
                                        # full_var_name = ''
                                        for child4 in child3.children:
                                            if child4.type == 'variable_name':
                                                full_var_name = f"{scope}.{child4.text.decode()}"
                                                global_vars[full_var_name] = None
                                            else:
                                                if child4.type == "function_call_expression":
                                                    global_vars[full_var_name] = get_calls(child4)
                                                elif child4.type == "member_call_expression":
                                                    global_vars[full_var_name] = get_member_calls(child4)
                                                else:
                                                    global_vars[full_var_name] = get_value(child4)
                                                pass

    return global_vars

def get_global_called_methods(node, scope):
    """Mencari semua pemanggilan fungsi yang hanya terjadi di global scope"""
    global_called_methods = []

    for child in node.children:
        if child.type == "expression_statement":
            expr = child.children[0]
            if expr.type == "function_call_expression" and not is_inside_function(child):
                res = get_calls(expr)
                global_called_methods.append(res)
            elif expr.type == "member_call_expression" and not is_inside_function(child):
                res = get_member_calls(expr)
                global_called_methods.append(res)

        global_called_methods.extend(get_global_called_methods(child, scope))

    return global_called_methods

def is_inside_function(node):
    """Cek apakah node berada dalam function/class"""
    while node.parent:
        if node.parent.type in ["function_definition", "method_definition"]:
            return True
        node = node.parent
    return False

def get_value(node):
    if node.type == "array" or node.type == 'array_creation_expression':
        # print(node.children)
        values = [v.text.decode() for v in node.children[2:-1]]
        return values
    elif node.type == "integer":
        return int(node.text)
    elif node.type == "string":
        return node.text.decode()
    elif node.type == "true" or node.type == "false":
        return node.type == "true"
    elif node.type == "binary_expression":
        return get_binary_expressions(node)
    else:
        return None

def get_binary_expressions(node):
    """Membangun string dari binary_expression secara rekursif"""
    if node.type == "binary_expression":
        left = get_binary_expressions(node.child_by_field_name("left"))
        operator = node.children[1].text.decode()  # Operator adalah child kedua
        right = get_binary_expressions(node.child_by_field_name("right"))
        return f"({left} {operator} {right})"

    # Jika node adalah identifier (variabel) atau angka, langsung kembalikan teksnya
    if node.type in ["variable_name", "integer", "string"]:
        return node.text.decode()

    return ""

def get_calls(node):
    if node and node.type == "function_call_expression":
        function_name_node = node.child_by_field_name("function")
        args = node.children[1:][0]
        arguments_nodes = [arg.text.decode() for arg in args.children[1:-1] if arg.text.decode() != ',']

        if function_name_node:
            function_name = function_name_node.text.decode()
            qualifier = None

            # Jika ada namespace/objek sebelum function call
            if "." in function_name:
                parts = function_name.split(".")
                qualifier = None
                function_name = parts[-1]

            return {
                "method": function_name,
                "arguments": arguments_nodes,
                "qualifier": qualifier
            }
        else:
            return None

def get_member_calls(node, calls=None):
    if calls is None:
        calls = []

    if node.type == 'member_call_expression':
        for child in node.children:
            if child.type == 'member_access_expression' or child.type == 'variable_name':
                qualifier = child.text.decode().replace('->','.')
                calls.append(qualifier)
            elif child.type == 'name':
                calls.append(child.text.decode())
            elif child.type == 'arguments':
                arguments = [arg.text.decode() for arg in child.children[1:-1] if arg.text.decode() != ',']
    if calls:
        return {
            'method': calls[-1],
            'arguments': arguments,
            'qualifier': calls[:-1]
        }

    return None

def get_class_functions(node, global_vars, scope):
    functions = {}

    for child in node.children:

        parameters = []
        return_type = []

        if child.type == 'class_declaration':
            for child1 in child.children:
                if child1.type == 'name':
                    full_function_name = f'{scope}.{child1.text.decode()}'
                elif child1.type == "declaration_list":
                    for child2 in child1.children:
                        if child2.type == 'method_declaration':
                            local_vars = {}
                            called_methods = []
                            full_function_name = scope
                            not_get_return = True
                            for child3 in child2.children:
                                # print(child3)
                                if child3.type == 'name':
                                    full_function_name = f'{full_function_name}.{child3.text.decode()}'

                                    if ':' in [arg.type for arg in child2.children]:
                                        not_get_return = False
                                        for child4 in child2.children:
                                            if child4.type == 'primitive_type':
                                                return_type = child4.children[0].type
                                                if return_type != 'void':
                                                    local_vars["Return"] = [{'type':return_type}]

                                    for child4 in child2.children:
                                        if child4.type == 'formal_parameters':
                                            parameters = get_function_parameters(child4)
                                            # print(full_function_name, parameters)
                                            if parameters:
                                                local_vars["Parameter"] = parameters
                                            # print(full_function_name, local_vars)
                                        elif child4.type == 'compound_statement':
                                            for child5 in child4.children:
                                                if child5.type == 'expression_statement':
                                                    loc = get_local_variables(child5)
                                                    called_methods.extend(get_called_methods(child5))
                                                    local_vars.update(loc)
                                                elif child5.type == 'return_statement':
                                                    # print(child4.children)
                                                    if not_get_return:
                                                        return_type = get_return_type(child4, local_vars, global_vars, 'class')
                                                        local_vars["Return"] = return_type
                                                elif child5.type == 'try_statement':
                                                    for child6 in child5.children:
                                                        # print(child6)
                                                        if child6.type == 'compound_statement':
                                                            for child7 in child6.children:
                                                                # print(child7)
                                                                if child7.type == 'expression_statement':
                                                                    loc = get_local_variables(child7)
                                                                    called_methods.extend(get_called_methods(child7))
                                                                    local_vars.update(loc)
                                                                elif child7.type == 'return_statement':
                                                                    # print(child4.children)
                                                                    if not_get_return:
                                                                        return_type = get_return_type(child6, local_vars, global_vars, 'class')
                                                                        local_vars["Return"] = return_type
                                                elif child5.type == 'if_statement':
                                                    get_if_functions(child5, called_methods, global_vars, local_vars, not_get_return)
                                                elif child5.type == 'while_statement':
                                                    get_while_functions(child5, called_methods, global_vars, local_vars, not_get_return)
                                                elif child5.type == 'for_statement':
                                                    get_for_functions(child5, called_methods, global_vars, local_vars, not_get_return)

                                        functions[full_function_name] = {
                                            "local_vars": local_vars,
                                            "called_methods": called_methods
                                        }

    return functions

def get_if_functions(child, called_methods, global_vars, local_vars, not_get_return):
    if child.type == 'if_statement':
        get_if_while_for_function(child, called_methods, global_vars, local_vars, not_get_return)

def get_while_functions(child, called_methods, global_vars, local_vars, not_get_return):
    if child.type == 'while_statement':
        get_if_while_for_function(child, called_methods, global_vars, local_vars, not_get_return)

def get_for_functions(child, called_methods, global_vars, local_vars, not_get_return):
    if child.type == 'for_statement':
        get_if_while_for_function(child, called_methods, global_vars, local_vars, not_get_return)

def get_if_while_for_function(child, called_methods, global_vars, local_vars, not_get_return):
    for child6 in child.children:
        # print(child6)
        if child6.type == 'parenthesized_expression':
            for child7 in child6.children:
                if child7.type == 'expression_statement':
                    loc = get_local_variables(child7)
                    called_methods.extend(get_called_methods(child7))
                    local_vars.update(loc)
        elif child6.type == 'compound_statement':
            for child7 in child6.children:
                # print(child7)
                if child7.type == 'expression_statement':
                    loc = get_local_variables(child7)
                    called_methods.extend(get_called_methods(child7))
                    local_vars.update(loc)
                elif child7.type == 'return_statement':
                    # print(child4.children)
                    if not_get_return:
                        return_type = get_return_type(child6, local_vars, global_vars, 'class')
                        local_vars["Return"] = return_type
        elif child6.type == 'else_clause':
            # print(child6.children)
            for child7 in child6.children:
                if child7.type == 'if_statement':
                    get_if_functions(child7, called_methods, global_vars, local_vars, not_get_return)
                elif child7.type == 'compound_statement':
                    for child8 in child7.children:
                        print(child8)
                        if child8.type == 'expression_statement':
                            loc = get_local_variables(child8)
                            called_methods.extend(get_called_methods(child8))
                            local_vars.update(loc)
                        elif child8.type == 'return_statement':
                            # print(child4.children)
                            if not_get_return:
                                return_type = get_return_type(child6, local_vars, global_vars, 'class')
                                local_vars["Return"] = return_type

def get_functions(node, global_vars, scope):
    """Menemukan semua fungsi dalam kode JavaScript"""
    functions = {}
    local_vars = {}

    for child in node.children:

        # local_vars = {}
        parameters = []
        return_type = []
        called_methods = []

        if child.type == "function_definition":
            function_name = child.child_by_field_name("name")
            function_body = child.child_by_field_name("body")

            if function_name and function_body:
                function_name_text = function_name.text.decode()
                full_function_name = f"{scope}.{function_name_text}"

                # Ambil parameter fungsi
                parameters = get_function_parameters(child.child_by_field_name("parameters"))
                if parameters:
                    local_vars["Parameter"] = parameters

                local_vars.update(get_local_variables(function_body))
                called_methods = get_called_methods(function_body)
                return_type = get_return_type(function_body, local_vars, global_vars)
                if return_type:
                    local_vars["Return"] = return_type

                functions[full_function_name] = {
                    "local_vars": local_vars,
                    "called_methods": called_methods
                }

        # Rekursif mencari fungsi dalam node lainnya
        functions.update(get_functions(child, global_vars, scope))

    return functions

def get_function_parameters(node):
    """Ambil parameter dari sebuah fungsi"""
    parameters = []
    # params_node = node.child_by_field_name("parameters")

    if node:
        for param in node.children:
            if param.type == "simple_parameter":
                parameters.append({"name": param.children[1].text.decode() if len(param.children) > 1 else 'Unknown Type', "type": param.children[0].text.decode()})

    return parameters

def get_local_variables(node):
    """Mencari variabel global dalam PHP"""
    local_vars = {}

    for child in node.children:
        # print(child)
        if child.type == "expression_statement":
            expr = child.children[0] if len(child.children) > 0 else None
            if expr.type == "assignment_expression":
                var_name = expr.child_by_field_name("left")
                var_value = expr.child_by_field_name("right")
                # print(var_name, var_value)
                if var_name:
                    full_var_name = f"{var_name.text.decode()}"
                    # Jika variabel adalah hasil pemanggilan fungsi
                    if var_value and var_value.type == "function_call_expression":
                        local_vars[full_var_name] = get_calls(var_value)
                    elif var_value and var_value.type == "member_call_expression":
                        local_vars[full_var_name] = get_member_calls(var_value)
                    # Jika variabel bukan hasil pemanggilan fungsi, simpan nilainya langsung
                    elif var_value and var_value.type == "variable_name":
                        local_vars[full_var_name] = var_value.text.decode()
                    else:
                        local_vars[full_var_name] = get_value(var_value)

        elif child.type == "assignment_expression":
                var_name = child.child_by_field_name("left")
                var_value = child.child_by_field_name("right")
                # print(var_name, var_value)
                if var_name:
                    full_var_name = f"{var_name.text.decode()}"
                    # Jika variabel adalah hasil pemanggilan fungsi
                    if var_value and var_value.type == "function_call_expression":
                        local_vars[full_var_name] = get_calls(var_value)
                    elif var_value and var_value.type == "member_call_expression":
                        local_vars[full_var_name] = get_member_calls(var_value)
                    # Jika variabel bukan hasil pemanggilan fungsi, simpan nilainya langsung
                    elif var_value and var_value.type == "variable_name":
                        local_vars[full_var_name] = var_value.text.decode()
                    else:
                        local_vars[full_var_name] = get_value(var_value)

    return local_vars

def get_called_methods(node):
    """Mencari semua pemanggilan fungsi yang hanya terjadi di global scope"""
    local_called_methods = []

    for child in node.children:
        if child.type == "expression_statement":
            expr = child.children[0]
            if expr.type == "function_call_expression":
                res = get_calls(expr)
                local_called_methods.append(res)
            elif expr.type == "member_call_expression":
                res = get_member_calls(expr)
                local_called_methods.append(res)
        elif child.type == "function_call_expression":
            res = get_calls(child)
            local_called_methods.append(res)
        elif child.type == "member_call_expression":
            res = get_member_calls(child)
            local_called_methods.append(res)

        local_called_methods.extend(get_called_methods(child))

    return local_called_methods

def get_return_type(node, local_vars, global_vars, type=''):
    """Menganalisis return type dalam fungsi"""
    return_types = []
    global_vars_last_keys = {key.split(".")[-1]: key for key in global_vars.keys()}

    for child in node.children:

        if child.type == "return_statement" and len(child.children) > 1:
            return_value = child.children[1]
            # print(return_value)

            if return_value:
                # Jika return value adalah langsung (literal)
                if return_value.type in ["string", "integer", "true", "false", 'boolean', "array_creation_expression", "object_creation_expression", "identifier"]:
                    if type == 'class':
                        return_types.append({"type": get_node_value_type(return_value)})
                    else:
                        return_types.append({"type": get_value_type(return_value)})

                # Jika return adalah pemanggilan fungsi
                elif return_value.type == "call_expression":
                    return_types.append({"type": 'func'})
                    # function_name_node = return_value.child_by_field_name("function")
                    # arguments_nodes = [arg.text.decode() for arg in return_value.children[1:]]

                    # qualifier = None
                    # if function_name_node:
                    #     function_name = function_name_node.text.decode()
                    #     if "." in function_name:
                    #         parts = function_name.split(".")
                    #         qualifier = ".".join(parts[:-1])
                    #         function_name = parts[-1]

                        # return_types.append({
                        #     "method": function_name,
                        #     "arguments": arguments_nodes,
                        #     "qualifier": qualifier
                        # })
                if return_value.type == "function_call_expression" and not is_inside_function(child):
                    return_types.append({"type": 'func'})
                    # return get_calls(return_value)

                elif return_value.type == "member_call_expression" and not is_inside_function(child):
                    return_types.append({"type": 'func'})
                    # return get_member_calls(return_value)

                # Jika return adalah variabel, cari di local atau global
                elif return_value.type == "variable_name":
                    var_name = return_value.text.decode()

                    # Cari di variabel lokal
                    if var_name in local_vars:
                        var_value = local_vars[var_name]
                        return_types.append({"type": get_value_type(var_value)})

                    # Cari di variabel global
                    elif var_name in global_vars_last_keys:
                        var_value = global_vars[global_vars_last_keys[var_name]]
                        return_types.append({"type": get_value_type(var_value)})

                    # Jika tidak ditemukan
                    else:
                        return_types.append({"type": "Unknown Type"})

        return_types.extend(get_return_type(child, local_vars, global_vars))

    return return_types

PHP_LANGUAGE = Language('build/my-languages.so', 'php')

# tree_contents = _extract_from_dir("./php/test", _parse_tree_content, "php")
# print(tree_contents)
# variable_func = _parse_function_variable(tree_contents)
# print(json.dumps(variable_func['global_vars'], indent=2))
# print(json.dumps(variable_func['functions'], indent=2))