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
                package = dirpath.replace('./','').replace('/','.')

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
    parser.set_language(JS_LANGUAGE)

    return parser.parse(file_contents.encode('utf8'))

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
        functions.update(function)
        function_lib = get_lib_methods(tree.root_node, key, 'app')
        functions.update(function_lib)

    variable_func = {
        'global_vars': global_vars,
        'functions': functions
    }

    return variable_func

def get_global_variables(node, scope):
    """Mencari global variables dan nilai awalnya"""
    global_vars = {}

    for child in node.children:
        if child.type == "expression_statement":
            expr = child.children[0]
            if expr.type == "assignment_expression":
                var_name = expr.child_by_field_name("left")
                var_value = expr.child_by_field_name("right")
                full_var_name = f"{scope}.{var_name.text.decode()}"
                if var_name and not is_inside_function(child):
                    # Jika variabel adalah hasil pemanggilan fungsi
                    if var_value and var_value.type == "call_expression":
                        function_name_node = var_value.child_by_field_name("function")
                        arguments_nodes = [arg.text.decode() for arg in var_value.children[1:]]

                        if function_name_node:
                            function_name = function_name_node.text.decode()
                            qualifier = None

                            # Jika ada namespace/objek sebelum function call
                            if "." in function_name:
                                parts = function_name.split(".")
                                qualifier = ".".join(parts[:-1])
                                function_name = parts[-1]

                            global_vars[full_var_name] = {
                                "method": function_name,
                                "arguments": arguments_nodes,
                                "qualifier": qualifier
                            }
                        else:
                            global_vars[full_var_name] = None

                    # Jika variabel bukan hasil pemanggilan fungsi, simpan nilainya langsung
                    else:
                        if var_value.type == "array":
                            values = [v.text.decode() for v in var_value.children]
                            global_vars[full_var_name] = values
                        elif var_value.type == "number":
                            global_vars[full_var_name] = int(var_value.text)
                        elif var_value.type == "string":
                            global_vars[full_var_name] = var_value.text.decode()
                        elif var_value.type == "true" or var_value.type == "false":
                            global_vars[full_var_name] = var_value.type == "true"
                        elif var_value.type == "binary_expression":
                            global_vars[full_var_name] = get_binary_expressions(var_value)
                        else:
                            global_vars[full_var_name] = None

                if var_value and var_value.type == "member_expression":
                    # print(var_value.type == "member_expression")

                    object_node = var_value.child_by_field_name("object")
                    property_node = var_value.child_by_field_name("property")

                    # Pastikan object adalah hasil require()
                    if object_node and object_node.type == "call_expression":
                        function_node = object_node.child_by_field_name("function")
                        arguments_node = object_node.child_by_field_name("arguments")
                        qualifier = None

                        if function_node:
                            function_name = function_node.text.decode()
                            if "." in function_name:
                                parts = function_name.split(".")
                                qualifier = ".".join(parts[:-1])
                                function_name = parts[-1]

                            global_vars[full_var_name] = {
                                "method": function_name,
                                "arguments": arguments_node.text.decode(),
                                "qualifier": qualifier
                            }

        elif child.type == "variable_declaration" or child.type == 'lexical_declaration':
            for declarator in child.children:

                if declarator.type == "variable_declarator":
                    var_name = declarator.child_by_field_name("name")
                    var_value = declarator.child_by_field_name("value")

                    full_var_name = f"{scope}.{var_name.text.decode()}"

                    if var_name and not is_inside_function(child):

                        # Jika variabel adalah hasil pemanggilan fungsi
                        if var_value and var_value.type == "call_expression":
                            function_name_node = var_value.child_by_field_name("function")
                            arguments_nodes = [arg.text.decode() for arg in var_value.children[1:]]

                            qualifier = None
                            if function_name_node:
                                function_name = function_name_node.text.decode()
                                if "." in function_name:
                                    parts = function_name.split(".")
                                    qualifier = ".".join(parts[:-1])
                                    function_name = parts[-1]

                                global_vars[full_var_name] = {
                                    "method": function_name,
                                    "arguments": arguments_nodes,
                                    "qualifier": qualifier
                                }
                        # Jika bukan hasil pemanggilan fungsi, simpan nilai langsung
                        else:
                            # print(var_value)
                            global_vars[full_var_name] = get_node_value_type(var_value) if var_value else None

                    if var_value and var_value.type == "member_expression":
                        # print(var_value.type == "member_expression")

                        object_node = var_value.child_by_field_name("object")
                        property_node = var_value.child_by_field_name("property")

                        # Pastikan object adalah hasil require()
                        if object_node and object_node.type == "call_expression":
                            function_node = object_node.child_by_field_name("function")
                            arguments_node = object_node.child_by_field_name("arguments")
                            qualifier = None

                            if function_node:
                                function_name = function_node.text.decode()
                                if "." in function_name:
                                    parts = function_name.split(".")
                                    qualifier = ".".join(parts[:-1])
                                    function_name = parts[-1]

                                global_vars[full_var_name] = {
                                    "method": function_name,
                                    "arguments": arguments_node.text.decode(),
                                    "qualifier": qualifier
                                }

        global_vars.update(get_global_variables(child, scope))

    return global_vars

def get_binary_expressions(node):
    """Membangun string dari binary_expression secara rekursif"""
    if node.type == "binary_expression":
        left = get_binary_expressions(node.child_by_field_name("left"))
        operator = node.children[1].text.decode()  # Operator adalah child kedua
        right = get_binary_expressions(node.child_by_field_name("right"))
        return f"({left} {operator} {right})"

    # Jika node adalah identifier (variabel) atau angka, langsung kembalikan teksnya
    if node.type in ["identifier", "number", "string"]:
        return node.text.decode()

    return ""

def get_global_called_methods(node, scope):
    """Mencari semua pemanggilan fungsi yang hanya terjadi di global scope"""
    global_called_methods = []

    for child in node.children:
        if child.type == "expression_statement":
            expr = child.children[0]
            if expr.type == "call_expression" and not is_inside_function(child):
                function_name_node = expr.child_by_field_name("function")
                arguments_nodes = [arg.text.decode() for arg in expr.children[1:]]

                if function_name_node:
                    function_name = function_name_node.text.decode()
                    qualifier = None

                    if "." in function_name:
                        parts = function_name.split(".")
                        qualifier = ".".join(parts[:-1])
                        function_name = parts[-1]

                    global_called_methods.append({
                        "method": function_name,
                        "arguments": arguments_nodes,
                        "qualifier": qualifier
                    })

        global_called_methods.extend(get_global_called_methods(child, scope))

    return global_called_methods


def is_inside_function(node):
    """Cek apakah node berada dalam function/class"""
    while node.parent:
        if node.parent.type in ["function_declaration", "method_definition"]:
            return True
        node = node.parent
    return False

def get_function_parameters(node):
    """Ambil parameter dari sebuah fungsi"""
    parameters = []
    params_node = node.child_by_field_name("parameters")

    if params_node:
        for param in params_node.children:
            if param.type == "identifier":
                parameters.append({"name": param.text.decode(), "type": "Unknown"})

    return parameters

def get_called_methods(node):
    """Menemukan variabel lokal dan fungsi yang dipanggil dalam suatu fungsi"""
    called_methods = []

    for child in node.children:

        # Mendeteksi pemanggilan fungsi langsung di dalam fungsi
        if child.type == "expression_statement":
            expr = child.children[0] if len(child.children) > 0 else None
            if expr and expr.type == "call_expression":
                function_name_node = expr.child_by_field_name("function")
                arguments_nodes = [arg.text.decode() for arg in expr.children[1:]]
                qualifier = None

                if function_name_node:
                    function_name = function_name_node.text.decode()
                    if "." in function_name:
                        parts = function_name.split(".")
                        qualifier = ".".join(parts[:-1])
                        function_name = parts[-1]

                    called_methods.append({
                        "method": function_name,
                        "arguments": arguments_nodes,
                        "qualifier": qualifier
                    })

        # Rekursif untuk mencari variabel dan pemanggilan fungsi lebih dalam
        deeper_methods = get_called_methods(child)
        called_methods.extend(deeper_methods)

    return called_methods

def get_local_variables(node):
    """Mendeteksi semua variabel yang dideklarasikan dalam fungsi dan apakah merupakan hasil pemanggilan fungsi"""
    local_vars = {}

    for child in node.children:
        # print(child.type)
        # Mendeteksi deklarasi variabel dengan let, var, atau const
        if child.type == "variable_declaration" or child.type == "lexical_declaration":
            for declarator in child.children:
                if declarator.type == "variable_declarator":
                    var_name = declarator.child_by_field_name("name")
                    var_value = declarator.child_by_field_name("value")

                    if var_name:
                        var_name_text = var_name.text.decode()

                        # Jika variabel adalah hasil pemanggilan fungsi
                        if var_value and var_value.type == "call_expression":
                            function_name_node = var_value.child_by_field_name("function")
                            arguments_nodes = [arg.text.decode() for arg in var_value.children[1:]]

                            qualifier = None
                            if function_name_node:
                                function_name = function_name_node.text.decode()

                                # Jika ada namespace/objek sebelum function call
                                if "." in function_name:
                                    parts = function_name.split(".")
                                    qualifier = ".".join(parts[:-1])
                                    function_name = parts[-1]

                                local_vars[var_name_text] = {
                                    "method": function_name,
                                    "arguments": arguments_nodes,
                                    "qualifier": qualifier
                                }
                        else:
                            # Simpan nilai langsung jika bukan hasil pemanggilan fungsi
                            local_vars[var_name_text] = var_value.text.decode() if var_value else None

        # Mendeteksi variabel yang langsung di-assign tanpa let, var, const
        if child.type == "expression_statement":
            expr = child.children[0] if len(child.children) > 0 else None
            if expr and expr.type == "assignment_expression":
                var_name = expr.child_by_field_name("left")
                var_value = expr.child_by_field_name("right")

                if var_name and is_inside_function(child):  # Pastikan dalam function
                    var_name_text = var_name.text.decode()

                    # Jika variabel adalah hasil pemanggilan fungsi
                    if var_value and var_value.type == "call_expression":
                        function_name_node = var_value.child_by_field_name("function")
                        arguments_nodes = [arg.text.decode() for arg in var_value.children[1:]]

                        qualifier = None
                        if function_name_node:
                            function_name = function_name_node.text.decode()
                            if "." in function_name:
                                parts = function_name.split(".")
                                qualifier = ".".join(parts[:-1])
                                function_name = parts[-1]

                            local_vars[var_name_text] = {
                                "method": function_name,
                                "arguments": arguments_nodes,
                                "qualifier": qualifier
                            }
                    else:
                        # Simpan nilai langsung jika bukan hasil pemanggilan fungsi
                        local_vars[var_name_text] = var_value.text.decode() if var_value else None

        # Rekursif untuk mencari lebih dalam
        local_vars.update(get_local_variables(child))

    return local_vars

def get_functions(node, global_vars, scope):
    """Menemukan semua fungsi dalam kode JavaScript"""
    functions = {}

    for child in node.children:

        local_vars = {}
        parameters = []
        return_type = []
        called_methods = []

        if child.type == "function_declaration":
            function_name = child.child_by_field_name("name")
            function_body = child.child_by_field_name("body")

            if function_name and function_body:
                function_name_text = function_name.text.decode()
                full_function_name = f"{scope}.{function_name_text}"

                # Ambil parameter fungsi
                parameters = get_function_parameters(child)
                if parameters:
                    local_vars["Parameter"] = parameters

                local_vars = get_local_variables(function_body)
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

def get_node_value_type(value_node):

    """Menentukan tipe dari value langsung"""
    if value_node.type == "string":
        return "String"
    elif value_node.type == "number":
        return "Number"
    elif value_node.type in ["true", "false"]:
        return "Boolean"
    elif value_node.type == "array":
        return "Array"
    elif value_node.type == "object":
        return "Object"
    elif value_node.type == 'binary_expression':
        return get_binary_expressions(value_node)
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


def get_return_type(node, local_vars, global_vars):
    """Menganalisis return type dalam fungsi"""
    return_types = []
    global_vars_last_keys = {key.split(".")[-1]: key for key in global_vars.keys()}

    for child in node.children:
        if child.type == "return_statement"and len(child.children) > 1:
            return_value = child.children[1]

            if return_value:
                # Jika return value adalah langsung (literal)
                if return_value.type in ["string", "number", "true", "false", "array", "object"]:
                    return_types.append({"type": get_value_type(return_value.text.decode())})

                # Jika return adalah pemanggilan fungsi
                elif return_value.type == "call_expression":
                    function_name_node = return_value.child_by_field_name("function")
                    arguments_nodes = [arg.text.decode() for arg in return_value.children[1:]]

                    qualifier = None
                    if function_name_node:
                        function_name = function_name_node.text.decode()
                        if "." in function_name:
                            parts = function_name.split(".")
                            qualifier = ".".join(parts[:-1])
                            function_name = parts[-1]

                        return_types.append({
                            "method": function_name,
                            "arguments": arguments_nodes,
                            "qualifier": qualifier
                        })

                # Jika return adalah variabel, cari di local atau global
                elif return_value.type == "identifier":
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

def get_lib_methods(node, scope, lib):
    """Mencari semua pemanggilan fungsi di objek app (app.get, app.post, dll.)"""
    routes = {}
    count = 1

    for child in node.children:
        if child.type == "expression_statement":
            expr = child.children[0] if len(child.children) > 0 else None
            if expr and expr.type == "call_expression":
                function_name_node = expr.child_by_field_name("function")

                # Pastikan ini adalah pemanggilan metode pada `app`
                if function_name_node and function_name_node.type == "member_expression":
                    object_node = function_name_node.child_by_field_name("object")
                    property_node = function_name_node.child_by_field_name("property")

                    if object_node and object_node.text.decode() == lib and property_node:
                        method_name = property_node.text.decode()  # Contoh: "get", "post", "put"
                        arguments = expr.child_by_field_name("arguments")

                        # print(arguments, len(arguments.children))
                        if arguments and len(arguments.children) >= 2:
                            route_path = arguments.children[0].text.decode().strip("\"'")
                            callback_function = arguments.children[1]  # Callback function (Arrow Function)

                            if route_path == '(':
                                if arguments and len(arguments.children) >= 4:
                                    route_path = arguments.children[1].text.decode().strip("\"'")  # Ambil path '/health'
                                    callback_function = arguments.children[3]  # Callback function (Arrow Function)

                                # Ambil parameter dari callback
                                params = []
                                param_node = callback_function.child_by_field_name("parameters")
                                if param_node:
                                    for param in param_node.children:
                                        if param.type == "identifier":
                                            params.append({"name": param.text.decode(), "type": "Object"})
                                else:
                                    params = [get_argument_details(arg) for arg in arguments.children]
                                    params = [param for param in params if param is not None]  # Hapus None values

                                # Ambil variabel lokal dalam callback
                                local_vars = {"Parameter": params}
                                function_body = callback_function.child_by_field_name("body")

                                if function_body:
                                    for statement in function_body.children:
                                        if statement.type == "variable_declaration":
                                            for declarator in statement.children:
                                                if declarator.type == "variable_declarator":
                                                    var_name = declarator.child_by_field_name("name")
                                                    var_value = declarator.child_by_field_name("value")

                                                    if var_name:
                                                        local_vars[var_name.text.decode()] = get_node_value_type(var_value)

                                # Simpan hasil dalam routes
                                function_key = f"{scope}.{lib}.{method_name}"
                                if route_path == '(':
                                    function_key = f"{function_key}.{route_path}"

                                if function_key in routes:
                                    function_key = f"{function_key}.{count}"
                                    count = count + 1
                                routes[function_key] = {
                                    "local_vars": local_vars
                                }

        # Rekursif untuk mencari lebih dalam
        routes.update(get_lib_methods(child, scope, lib))

    return routes

def get_argument_details(arg_node):
    """Menganalisis argumen yang diberikan ke app.use()"""
    if arg_node is None:
        return None

    # Jika argumen adalah pemanggilan fungsi seperti `bodyParser.urlencoded({ extended: true })`
    if arg_node.type == "call_expression":
        function_name_node = arg_node.child_by_field_name("function")
        arguments_nodes = [arg.text.decode() for arg in arg_node.child_by_field_name("arguments").children] if arg_node.child_by_field_name("arguments") else []

        function_name = function_name_node.text.decode() if function_name_node else "Unknown Function"

        return {
            "name": function_name,
            "type": arg_node.type
        }

    # Jika argumen adalah identifier langsung (seperti `expLogger`)
    elif arg_node.type == "identifier":
        return {
            "name": arg_node.text.decode(),
            "type": arg_node.type
        }

    return None


JS_LANGUAGE = Language('build/my-languages.so', 'javascript')

# tree_contents = _extract_from_dir("C://Users//ARD//Desktop//robot-shop", _parse_tree_content, "js")
# print(tree_contents)
# variable_func = _parse_function_variable(tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['functions'], indent=2))