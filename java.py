import re
import os
import javalang
import json
from typing import Dict, Tuple

def _extract_from_dir(dir_path, parser, lang) -> dict:
    contents = {}
    for dirpath, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename.endswith(f".{lang}"):
                file_path = os.path.join(dirpath, filename)
                file_content = parser(file_path)
                package = _parse_tree_package(file_content)

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

    return javalang.parse.parse(file_contents)

def _parse_tree_package(tree_contents) -> str:
    return tree_contents.package.name

def _parse_function_variable(tree_contents) -> Tuple[dict, dict]:

    # Menyimpan hasil analisis
    functions = {}
    global_vars = {}

    # Mendapatkan variabel global (field)
    for key, tree in tree_contents.items():

        for path, node in tree.filter(javalang.tree.FieldDeclaration):
            for declarator in node.declarators:
                var_name = key+"."+declarator.name

                if isinstance(declarator.initializer, javalang.tree.This):
                    declarator.initializer = declarator.initializer.selectors[0]

                # Jika initializer adalah pemanggilan metode
                if isinstance(declarator.initializer, javalang.tree.MethodInvocation):
                    method_name = declarator.initializer.member
                    # print(declarator.initializer)
                    qualifier = declarator.initializer.qualifier if hasattr(declarator.initializer, 'qualifier') else None

                    method_args = []
                    for arg in declarator.initializer.arguments:

                        if isinstance(arg, javalang.tree.This):
                            arg = arg.selectors[0]

                        if isinstance(arg, javalang.tree.ClassReference):
                            method_args.append(arg.type.name+".class")
                        elif isinstance(arg, javalang.tree.MemberReference):
                            method_args.append(arg.member)
                        elif isinstance(arg, javalang.tree.Literal):
                            method_args.append(arg.value)
                        elif isinstance(arg, javalang.tree.MethodInvocation):
                            method_name2 = arg.member
                            qualifier2 = arg.qualifier if hasattr(arg, 'qualifier') else None

                            method_args2 = []
                            for arg2 in arg.arguments:
                                if isinstance(arg2, javalang.tree.ClassReference):
                                    method_args2.append(arg2.type.name)
                                elif isinstance(arg2, javalang.tree.MemberReference):
                                    method_args2.append(arg2.member)
                                elif isinstance(arg2, javalang.tree.Literal):
                                    method_args2.append(arg2.value)
                            method_args.append({
                                "method": method_name2,
                                "arguments": method_args2,
                                "qualifier": qualifier2,
                            })

                    global_vars[var_name] = {
                        "method": method_name,
                        "arguments": method_args,
                        "qualifier": qualifier,
                    }
                elif isinstance(declarator.initializer, javalang.tree.ArrayInitializer):
                    array_list = []
                    for initializer2 in declarator.initializer.initializers:
                        if isinstance(initializer2, javalang.tree.Literal):
                            array_list.append(initializer2.value)
                    method_args.append(array_list)
                else:
                    global_vars[var_name] = declarator.initializer.value if declarator.initializer else None


        # Mendapatkan daftar fungsi beserta variabel lokal
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            func_name = key+"."+node.name
            local_vars = {}
            called_methods = []
            called_set = set()
            return_vars = {}

            # Cek parameter
            if node.parameters:
                params = []
                for param in node.parameters:
                    params.append({
                        'name': param.name,
                        'type': param.type.name
                    })

                local_vars['Parameter'] = params

            if node.return_type and node.return_type.name:
                local_vars["Return"] = [{
                    "type": node.return_type.name
                }]

            # Cari variabel lokal dalam body fungsi
            if node.body:
                for statement in node.body:
                    # print(statement, "\n")

                    # Cari variabel lokal
                    if isinstance(statement, javalang.tree.LocalVariableDeclaration):
                        for declarator in statement.declarators:
                            var_name = declarator.name
                            initializer = declarator.initializer

                            if isinstance(initializer, javalang.tree.This):
                                initializer = initializer.selectors[0]

                            # Jika initializer adalah pemanggilan metode
                            if isinstance(initializer, javalang.tree.MethodInvocation):
                                method_name = initializer.member
                                qualifier = initializer.qualifier if hasattr(initializer, 'qualifier') else None
                                # method_args = [str(arg.value if hasattr(arg, 'value') else arg) for arg in initializer.arguments]
                                method_args = []
                                for arg in initializer.arguments:
                                    if isinstance(arg, javalang.tree.This):
                                        arg = arg.selectors[0]
                                    if isinstance(arg, javalang.tree.MemberReference):
                                        method_args.append(arg.member)
                                    elif isinstance(arg, javalang.tree.Literal):
                                        method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                local_vars[var_name] = {
                                    "method": method_name,
                                    "arguments": method_args
                                }

                                called_methods.append({
                                    "method": method_name,
                                    "arguments": method_args,
                                    "qualifier": qualifier,
                                    "assigned_to": var_name
                                })
                                called_set.add((method_name, len(method_args), qualifier))

                            elif isinstance(initializer, javalang.tree.ArrayInitializer):
                                array_list = []
                                for initializer2 in initializer.initializers:
                                    if isinstance(initializer2, javalang.tree.Literal):
                                        array_list.append(initializer2.value)
                                local_vars[var_name] = array_list

                            else:
                                # Jika initializer adalah literal
                                local_vars[var_name] = getattr(initializer, 'value', 'None')

                    elif isinstance(statement, javalang.tree.TryStatement):
                        for try_statement in statement.block:
                            if isinstance(try_statement, javalang.tree.LocalVariableDeclaration):
                                for declarator in try_statement.declarators:
                                    var_name = declarator.name
                                    initializer = declarator.initializer

                                    if isinstance(initializer, javalang.tree.This):
                                        initializer = initializer.selectors[0]

                                    # Jika initializer adalah pemanggilan metode
                                    if isinstance(initializer, javalang.tree.MethodInvocation):
                                        method_name = initializer.member
                                        qualifier = initializer.qualifier if hasattr(initializer, 'qualifier') else None
                                        # method_args = [str(arg.value if hasattr(arg, 'value') else arg) for arg in initializer.arguments]
                                        method_args = []
                                        for arg in initializer.arguments:
                                            if isinstance(arg, javalang.tree.This):
                                                arg = arg.selectors[0]
                                            if isinstance(arg, javalang.tree.ClassReference):
                                                method_args.append(arg.type.name+".class")
                                            elif isinstance(arg, javalang.tree.MemberReference):
                                                method_args.append(arg.member)
                                            elif isinstance(arg, javalang.tree.Literal):
                                                method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                        local_vars[var_name] = {
                                            "method": method_name,
                                            "arguments": method_args
                                        }

                                        called_methods.append({
                                            "method": method_name,
                                            "arguments": method_args,
                                            "qualifier": qualifier,
                                            "assigned_to": var_name
                                        })
                                        called_set.add((method_name, len(method_args), qualifier))

                                    elif isinstance(initializer, javalang.tree.ArrayInitializer):
                                        array_list = []
                                        for initializer2 in initializer.initializers:
                                            if isinstance(initializer2, javalang.tree.Literal):
                                                array_list.append(initializer2.value)
                                        local_vars[var_name] = array_list

                                    else:
                                        # Jika initializer adalah literal
                                        local_vars[var_name] = getattr(initializer, 'value', 'None')


                    # Cari pemanggilan metode secara umum di dalam statement
                    for inner_path, inner_node in statement.filter(javalang.tree.MethodInvocation):
                        # print(inner_node)
                        method_name = inner_node.member
                        qualifier = inner_node.qualifier if hasattr(inner_node, 'qualifier') else None

                        # method_args = [arg.value for arg in inner_node.arguments if hasattr(arg, 'value')]
                        method_args = []
                        for arg in inner_node.arguments:
                            if isinstance(arg, javalang.tree.ClassReference):
                                method_args.append(arg.type.name+".class")
                            elif isinstance(arg, javalang.tree.MemberReference):
                                method_args.append(arg.member)
                            elif isinstance(arg, javalang.tree.Literal):
                                method_args.append(arg.value)

                        if not (method_name, len(method_args), qualifier) in called_set:
                            called_methods.append({
                                "method": method_name,
                                "arguments": method_args,
                                "qualifier": qualifier
                            })
                            called_set.add((method_name, len(method_args), qualifier))

            functions[func_name] = {
                'local_vars': local_vars,
                'called_methods': called_methods
            }
    variable_func = {
        'global_vars': global_vars,
        'functions': functions
    }
    return variable_func


# tree_contents = _extract_from_dir("./java/test", _parse_tree_content, "java")
# print(tree_contents)
# variable_func = _parse_function_variable(tree_contents)
# print(json.dumps(variable_func['functions'], indent=2))


