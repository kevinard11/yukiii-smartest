import re
import os
import javalang, yaml
import json
from typing import Dict, Tuple

def _extract_from_dir(dir_path, parser, lang) -> dict:
    contents = {}
    loc = 0
    for dirpath, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename.endswith(f".{lang}"):
                file_path = os.path.join(dirpath, filename)
                file_content = parser(file_path)
                if file_content:
                    package = _parse_tree_package(file_content)
                    if package:
                        key = package + "." + filename.replace(f".{lang}", "")
                    else:
                        key = file_path

                    contents[key] = file_content

                total_loc, effective_loc = count_lines_of_code(file_path)
                loc = loc + effective_loc

            elif 'application' in filename and filename.endswith(".yaml"):
                file_path = os.path.join(dirpath, filename)
                file_content = _parse_content_yaml(file_path)

                contents[file_path.replace('./','').replace('/','.').replace('\\', '.')] = file_content

    contents['loc'] = loc

    return contents

def count_lines_of_code(file_path):
    """Menghitung jumlah baris kode dalam file berdasarkan jenis bahasa"""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # Aturan komentar berdasarkan bahasa
    comment_markers = {
        ".java": ("//", "/*", "*/"),
        ".py": ("#", "'''", "'''"),
        ".php": ("//", "/*", "*/", "#"),
        ".js": ("//", "/*", "*/"),
        ".go": ("//", "/*", "*/")
    }

    single_comment, block_start, block_end = comment_markers.get(ext, (None, None, None))

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    total_loc = len(lines)
    effective_loc = 0
    in_block_comment = False

    for line in lines:
        stripped = line.strip()

        # Abaikan baris kosong
        if not stripped:
            continue

        # Cek awal atau akhir blok komentar
        if block_start and stripped.startswith(block_start):
            in_block_comment = True
        if block_end and stripped.endswith(block_end):
            in_block_comment = False
            continue  # Lewati baris ini

        # Lewati jika sedang dalam blok komentar
        if in_block_comment:
            continue

        # Abaikan komentar satu baris
        if single_comment and stripped.startswith(single_comment):
            continue

        # Tambahkan hanya jika baris ini adalah baris kode
        effective_loc += 1

    return total_loc, effective_loc

def _parse_content(file_path) -> any:
    with open(file_path, "r") as f:
        file_contents = f.read()

    return file_contents

def _parse_tree_content(file_path) -> any:
    try:
        file_contents = _parse_content(file_path)

        return javalang.parse.parse(file_contents)
    except Exception:
        return None


def _parse_tree_package(tree_contents) -> str:
    return tree_contents.package.name

def _parse_content_yaml(file_path) -> any:
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)

    return config

def flatten_dict(d, parent_key='', sep='.'):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

def convert_java_format_to_python(java_format, *args):
    """Convert Java's String.format syntax to Python .format() syntax"""
    python_format = re.sub(r'%s', '{}', java_format)
    return python_format.format(*args)

def _parse_function_variable(tree_contents) -> Tuple[dict, dict]:

    # Menyimpan hasil analisis
    functions = {}
    global_vars = {}

    # Mendapatkan variabel global (field)
    for key, tree in tree_contents.items():

        if key == 'loc':
            continue

        if 'application' in key and isinstance(tree, dict):
            items = flatten_dict(tree)
            for name, item in items.items():
                global_vars[key +"."+ name] = item
            continue

        elif isinstance(tree, javalang.tree.CompilationUnit):
            for path, node in tree.filter(javalang.tree.InterfaceDeclaration):
                for annotation in node.annotations:
                    if annotation.name == 'FeignClient':
                        key = key + ".@" + annotation.name
                        for element in annotation.element:
                            if element.name == 'url':
                                for name, element_value in element.value.filter(javalang.tree.Literal):
                                    global_vars[key + ".base" + element.name] = element_value.value

            for path, node in tree.filter(javalang.tree.FieldDeclaration):
                for declarator in node.declarators:
                    var_name = key+"."+declarator.name

                    if isinstance(declarator.initializer, javalang.tree.This):
                        declarator.initializer = declarator.initializer.selectors[0]

                    # Jika initializer adalah pemanggilan metode
                    if isinstance(declarator.initializer, javalang.tree.MethodInvocation):
                        method_name = declarator.initializer.member

                        qualifier = declarator.initializer.qualifier if hasattr(declarator.initializer, 'qualifier') else None

                        method_args = []

                        if method_name == 'format':
                            args = declarator.initializer.arguments
                            if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                format_str = args[0].value

                            if format_str:
                                keywords = []
                                for arg in args[1:]:
                                    if isinstance(arg, javalang.tree.Literal):
                                        keywords.append(arg.value.replace("'",'').replace('"',''))
                                    elif isinstance(arg, javalang.tree.MemberReference):
                                        keywords.append(arg.member.replace("'",'').replace('"',''))
                                    elif isinstance(arg, javalang.tree.MethodInvocation):
                                        arg1 = arg.arguments
                                        for arg2 in arg1:
                                            if isinstance(arg2, javalang.tree.Literal):
                                                keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                break

                                if keywords:
                                    format_str = convert_java_format_to_python(format_str, *keywords)
                                method_args.append(format_str)
                        else:
                            for arg in declarator.initializer.arguments:

                                if isinstance(arg, javalang.tree.This):
                                    arg = arg.selectors[0]

                                if isinstance(arg, javalang.tree.ClassReference):
                                    method_args.append(arg.type.name+".class")
                                elif isinstance(arg, javalang.tree.MemberReference):
                                    method_args.append(arg.member)
                                elif isinstance(arg, javalang.tree.Literal):
                                    method_args.append(arg.value)
                                # elif isinstance(arg, javalang.tree.BinaryOperation):
                                #     method_args(get_BinOp(initializer))
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
                    elif isinstance(declarator.initializer, javalang.tree.LambdaExpression):
                        global_vars[var_name] = "lambda_expression"
                    elif isinstance(declarator.initializer, javalang.tree.ClassCreator):
                        global_vars[var_name] = f"{declarator.initializer.type.name}.class" if declarator.initializer else None
                    elif isinstance(declarator.initializer, javalang.tree.MemberReference):
                        global_vars[var_name] = f"{declarator.initializer.member}" if declarator.initializer else None
                        # print(declarator.initializer)
                    elif isinstance(declarator.initializer, javalang.tree.BinaryOperation):
                       global_vars[var_name] = get_BinOp(declarator.initializer)
                    else:
                        global_vars[var_name] = declarator.initializer.value if declarator.initializer else None

                    for annotations in node.annotations:
                        var_name = key+"."+declarator.name
                        if var_name in global_vars and global_vars[var_name] == None and annotations.element and isinstance(annotations.element, javalang.tree.Literal):
                            # print(annotations)
                            global_vars[var_name] = annotations.element.value if annotations.element else None


            # Mendapatkan daftar fungsi beserta variabel lokal
            for path, node in tree.filter(javalang.tree.MethodDeclaration):
                func_name = key+"."+node.name
                # print(func_name, node)
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

                if node.annotations:
                    for annotation in node.annotations:
                        if (annotation.name == 'RequestMapping'):
                            if annotation.element:
                                for element in annotation.element:
                                    if isinstance(element, javalang.tree.ElementValuePair) and element.name == 'method':
                                        if (isinstance(element.value, javalang.tree.MemberReference)) and element.value.qualifier == 'RequestMethod':
                                            local_vars['Http_method'] = element.value.member.lower()
                        elif (annotation.name == 'GetMapping'):
                            local_vars['Http_method'] = 'get'
                        elif (annotation.name == 'PostMapping'):
                            local_vars['Http_method'] = 'post'
                        elif (annotation.name == 'PutMapping'):
                            local_vars['Http_method'] = 'put'
                        elif (annotation.name == 'DeleteMapping'):
                            local_vars['Http_method'] = 'delete'


                # Cari variabel lokal dalam body fungsi
                if node.body:
                    for statement in node.body:
                        # print(statement)

                        # Cari variabel lokal
                        if isinstance(statement, javalang.tree.StatementExpression):
                            expression = statement.expression
                            if isinstance(expression, javalang.tree.This):
                                expression = expression.selectors[0]

                            # Jika expression adalah pemanggilan metode
                            if isinstance(expression, javalang.tree.MethodInvocation):
                                method_name = expression.member
                                qualifier = expression.qualifier if hasattr(expression, 'qualifier') else None
                                # method_args = [str(arg.value if hasattr(arg, 'value') else arg) for arg in expression.arguments]
                                method_args = []
                                if method_name == 'format':
                                    args = expression.arguments
                                    if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                        format_str = args[0].value

                                    if format_str:
                                        keywords = []
                                        for arg in args[1:]:
                                            if isinstance(arg, javalang.tree.Literal):
                                                keywords.append(arg.value.replace("'",'').replace('"',''))
                                            elif isinstance(arg, javalang.tree.MemberReference):
                                                keywords.append(arg.member.replace("'",'').replace('"',''))
                                            elif isinstance(arg, javalang.tree.MethodInvocation):
                                                arg1 = arg.arguments
                                                for arg2 in arg1:
                                                    if isinstance(arg2, javalang.tree.Literal):
                                                        keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                        break

                                        if keywords:
                                            format_str = convert_java_format_to_python(format_str, *keywords)
                                        method_args.append(format_str)
                                else:
                                    for arg in expression.arguments:
                                        if isinstance(arg, javalang.tree.This):
                                            arg = arg.selectors[0] if arg.selectors else arg
                                        if isinstance(arg, javalang.tree.ClassReference):
                                            method_args.append(arg.type.name+".class")
                                        elif isinstance(arg, javalang.tree.MemberReference):
                                            method_args.append(arg.member)
                                        elif isinstance(arg, javalang.tree.Literal):
                                            method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                        elif isinstance(arg, javalang.tree.ClassReference):
                                            method_args.append(f"{arg.type.name}.class")

                                called_methods.append({
                                    "method": method_name,
                                    "arguments": method_args,
                                    "qualifier": qualifier
                                })
                                called_set.add((method_name, len(method_args), qualifier))
                            elif isinstance(statement.expression, javalang.tree.Assignment):
                                declarator = statement.expression

                                if isinstance(declarator.expressionl, javalang.tree.MemberReference):
                                    var_name = declarator.expressionl.member

                                initializer = declarator.value

                                if isinstance(initializer, javalang.tree.This):
                                    initializer = initializer.selectors[0]

                                # Jika initializer adalah pemanggilan metode
                                if isinstance(initializer, javalang.tree.MethodInvocation):
                                    method_name = initializer.member
                                    qualifier = initializer.qualifier if hasattr(initializer, 'qualifier') else None
                                    # method_args = [str(arg.value if hasattr(arg, 'value') else arg) for arg in initializer.arguments]
                                    method_args = []
                                    if method_name == 'format':
                                        args = initializer.arguments
                                        if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                            format_str = args[0].value

                                        if format_str:
                                            keywords = []
                                            for arg in args[1:]:
                                                if isinstance(arg, javalang.tree.Literal):
                                                    keywords.append(arg.value.replace("'",'').replace('"',''))
                                                elif isinstance(arg, javalang.tree.MemberReference):
                                                    keywords.append(arg.member.replace("'",'').replace('"',''))
                                                elif isinstance(arg, javalang.tree.MethodInvocation):
                                                    arg1 = arg.arguments
                                                    for arg2 in arg1:
                                                        if isinstance(arg2, javalang.tree.Literal):
                                                            keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                            break

                                            if keywords:
                                                format_str = convert_java_format_to_python(format_str, *keywords)
                                            method_args.append(format_str)
                                    else:
                                        for arg in initializer.arguments:
                                            if isinstance(arg, javalang.tree.This):
                                                arg = arg.selectors[0]
                                            if isinstance(arg, javalang.tree.ClassReference):
                                                method_args.append(arg.type.name+".class")
                                            elif isinstance(arg, javalang.tree.MemberReference):
                                                method_args.append(arg.member)
                                            elif isinstance(arg, javalang.tree.Literal):
                                                method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                            elif isinstance(arg, javalang.tree.ClassReference):
                                                method_args.append(f"{arg.type.name}.class")
                                            # else:
                                            #     method_args.append(str(arg))
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

                                # elif isinstance(initializer, javalang.tree.BinaryOperation):
                                #     local_vars[var_name] = get_BinOp(initializer)
                                else:
                                    # Jika initializer adalah literal
                                    local_vars[var_name] = getattr(initializer, 'value', 'None')
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
                                    if method_name == 'format':
                                        args = initializer.arguments
                                        if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                            format_str = args[0].value

                                        if format_str:
                                            keywords = []
                                            for arg in args[1:]:
                                                if isinstance(arg, javalang.tree.Literal):
                                                    keywords.append(arg.value.replace("'",'').replace('"',''))
                                                elif isinstance(arg, javalang.tree.MemberReference):
                                                    keywords.append(arg.member.replace("'",'').replace('"',''))
                                                elif isinstance(arg, javalang.tree.MethodInvocation):
                                                    arg1 = arg.arguments
                                                    for arg2 in arg1:
                                                        if isinstance(arg2, javalang.tree.Literal):
                                                            keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                            break

                                            if keywords:
                                                format_str = convert_java_format_to_python(format_str, *keywords)
                                            method_args.append(format_str)
                                    else:
                                        for arg in initializer.arguments:
                                            if isinstance(arg, javalang.tree.This):
                                                arg = arg.selectors[0]
                                            if isinstance(arg, javalang.tree.MemberReference):
                                                method_args.append(arg.member)
                                            # elif isinstance(arg, javalang.tree.BinaryOperation):
                                            #     method_args(get_BinOp(arg))
                                            elif isinstance(arg, javalang.tree.Literal):
                                                method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                            elif isinstance(arg, javalang.tree.ClassReference):
                                                method_args.append(f"{arg.type.name}.class")
                                            # else:
                                            #     method_args.append(str(arg))

                                    local_vars[var_name] = {
                                        "method": method_name,
                                        "arguments": method_args
                                    }
                                    # --------------------eaeaea

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
                                # elif isinstance(initializer, javalang.tree.BinaryOperation):
                                #     local_vars[var_name] = get_BinOp(initializer)

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
                                            if method_name == 'format':
                                                args = initializer.arguments
                                                if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                                    format_str = args[0].value

                                                if format_str:
                                                    keywords = []
                                                    for arg in args[1:]:
                                                        if isinstance(arg, javalang.tree.Literal):
                                                            keywords.append(arg.value.replace("'",'').replace('"',''))
                                                        elif isinstance(arg, javalang.tree.MemberReference):
                                                            keywords.append(arg.member.replace("'",'').replace('"',''))
                                                        elif isinstance(arg, javalang.tree.MethodInvocation):
                                                            arg1 = arg.arguments
                                                            for arg2 in arg1:
                                                                if isinstance(arg2, javalang.tree.Literal):
                                                                    keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                                    break

                                                    if keywords:
                                                        format_str = convert_java_format_to_python(format_str, *keywords)
                                                    method_args.append(format_str)
                                            else:
                                                for arg in initializer.arguments:
                                                    if isinstance(arg, javalang.tree.This):
                                                        arg = arg.selectors[0]
                                                    if isinstance(arg, javalang.tree.ClassReference):
                                                        method_args.append(arg.type.name+".class")
                                                    elif isinstance(arg, javalang.tree.MemberReference):
                                                        method_args.append(arg.member)
                                                    # elif isinstance(arg, javalang.tree.BinaryOperation):
                                                    #     method_args(get_BinOp(initializer))
                                                    elif isinstance(arg, javalang.tree.Literal):
                                                        method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                                    elif isinstance(arg, javalang.tree.ClassReference):
                                                        method_args.append(f"{arg.type.name}.class")
                                                    # else:
                                                    #     method_args.append(str(arg))
                                            local_vars[var_name] = {
                                                "method": method_name,
                                                "arguments": method_args
                                            }

                                            # called_methods.append({
                                            #     "method": method_name,
                                            #     "arguments": method_args,
                                            #     "qualifier": qualifier,
                                            #     "assigned_to": var_name
                                            # })
                                            called_set.add((method_name, len(method_args), qualifier))

                                        elif isinstance(initializer, javalang.tree.ArrayInitializer):
                                            array_list = []
                                            for initializer2 in initializer.initializers:
                                                if isinstance(initializer2, javalang.tree.Literal):
                                                    array_list.append(initializer2.value)
                                            local_vars[var_name] = array_list
                                        # elif isinstance(initializer, javalang.tree.BinaryOperation):
                                        #     local_vars[var_name] = get_BinOp(initializer)

                                        else:
                                            # Jika initializer adalah literal
                                            local_vars[var_name] = getattr(initializer, 'value', 'None')

                        elif isinstance(statement, javalang.tree.IfStatement) or  isinstance(statement, javalang.tree.WhileStatement) or isinstance(statement, javalang.tree.ForStatement):
                            # print(statement)
                            get_for_if_while_switch(statement, local_vars, called_methods, called_set)


                        # Cari pemanggilan metode secara umum di dalam statement
                        for inner_path, inner_node in statement.filter(javalang.tree.MethodInvocation):
                            # print(inner_node)
                            method_name = inner_node.member
                            qualifier = inner_node.qualifier if hasattr(inner_node, 'qualifier') else None

                            # method_args = [arg.value for arg in inner_node.arguments if hasattr(arg, 'value')]
                            method_args = []
                            if method_name == 'format':
                                args = inner_node.arguments
                                if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                    format_str = args[0].value

                                if format_str:
                                    keywords = []
                                    for arg in args[1:]:
                                        if isinstance(arg, javalang.tree.Literal):
                                            keywords.append(arg.value.replace("'",'').replace('"',''))
                                        elif isinstance(arg, javalang.tree.MemberReference):
                                            keywords.append(arg.member.replace("'",'').replace('"',''))
                                        elif isinstance(arg, javalang.tree.MethodInvocation):
                                            arg1 = arg.arguments
                                            for arg2 in arg1:
                                                if isinstance(arg2, javalang.tree.Literal):
                                                    keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                    break

                                    if keywords:
                                        format_str = convert_java_format_to_python(format_str, *keywords)
                                    method_args.append(format_str)
                            else:
                                for arg in inner_node.arguments:
                                    if isinstance(arg, javalang.tree.ClassReference):
                                        method_args.append(arg.type.name+".class")
                                    elif isinstance(arg, javalang.tree.MemberReference):
                                        method_args.append(arg.member)
                                    elif isinstance(arg, javalang.tree.Literal):
                                        method_args.append(arg.value)
                                    elif isinstance(arg, javalang.tree.ClassReference):
                                        method_args.append(f"{arg.type.name}.class")
                                    # else:
                                    #     method_args.append(str(arg))
                                    # elif isinstance(arg, javalang.tree.BinaryOperation):
                                    #     method_args(get_BinOp(initializer))

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

        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                operands, operators, nodes, edges, statement_count = get_complexity_element(node)
                functions[key+"."+node.name].update({
                    "operands": operands,
                    "operators": operators,
                    "nodes": nodes,
                    "edges": edges,
                    "exec_state": statement_count,
                })

        # get_operand_and_operator(node, functions, func_name)
    variable_func = {
        'global_vars': global_vars,
        'functions': functions
    }
    return variable_func

def get_for_if_while_switch(statement, local_vars, called_methods, called_set):
    # print(statement)
    if isinstance(statement, javalang.tree.IfStatement):
        if isinstance(statement.condition, javalang.tree.MethodInvocation):
            initializer = statement.condition
            method_name = initializer.member
            qualifier = initializer.qualifier if hasattr(initializer, 'qualifier') else None
            # method_args = [str(arg.value if hasattr(arg, 'value') else arg) for arg in initializer.arguments]
            method_args = []
            if method_name == 'format':
                args = initializer.arguments
                if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                    format_str = args[0].value

                if format_str:
                    keywords = []
                    for arg in args[1:]:
                        if isinstance(arg, javalang.tree.Literal):
                            keywords.append(arg.value.replace("'",'').replace('"',''))
                        elif isinstance(arg, javalang.tree.MemberReference):
                            keywords.append(arg.member.replace("'",'').replace('"',''))
                        elif isinstance(arg, javalang.tree.MethodInvocation):
                            arg1 = arg.arguments
                            for arg2 in arg1:
                                if isinstance(arg2, javalang.tree.Literal):
                                    keywords.append(arg2.value.replace("'",'').replace('"',''))
                                    break

                    if keywords:
                        format_str = convert_java_format_to_python(format_str, *keywords)
                    method_args.append(format_str)
            else:
                for arg in initializer.arguments:
                    if isinstance(arg, javalang.tree.This):
                        arg = arg.selectors[0]
                    if isinstance(arg, javalang.tree.MemberReference):
                        method_args.append(arg.member)
                    elif isinstance(arg, javalang.tree.Literal):
                        method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                    elif isinstance(arg, javalang.tree.ClassReference):
                        method_args.append(f"{arg.type.name}.class")
                    # else:
                    #     method_args.append(str(arg))
                    # elif isinstance(arg, javalang.tree.BinaryOperation):
                    #     method_args(get_BinOp(initializer))

            called_methods.append({
                "method": method_name,
                "arguments": method_args,
                "qualifier": qualifier
            })
            called_set.add((method_name, len(method_args), qualifier))

        if isinstance(statement.then_statement, javalang.tree.BlockStatement):
            then_statements = statement.then_statement
            for then_statement in then_statements.statements:
                if isinstance(then_statement, javalang.tree.LocalVariableDeclaration):
                    for declarator in then_statement.declarators:
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

                            if method_name == 'format':
                                args = initializer.arguments
                                if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                    format_str = args[0].value

                                if format_str:
                                    keywords = []
                                    for arg in args[1:]:
                                        if isinstance(arg, javalang.tree.Literal):
                                            keywords.append(arg.value.replace("'",'').replace('"',''))
                                        elif isinstance(arg, javalang.tree.MemberReference):
                                            keywords.append(arg.member.replace("'",'').replace('"',''))
                                        elif isinstance(arg, javalang.tree.MethodInvocation):
                                            arg1 = arg.arguments
                                            for arg2 in arg1:
                                                if isinstance(arg2, javalang.tree.Literal):
                                                    keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                    break

                                    if keywords:
                                        format_str = convert_java_format_to_python(format_str, *keywords)
                                    method_args.append(format_str)
                            else:
                                for arg in initializer.arguments:
                                    if isinstance(arg, javalang.tree.This):
                                        arg = arg.selectors[0]
                                    if isinstance(arg, javalang.tree.ClassReference):
                                        method_args.append(arg.type.name+".class")
                                    elif isinstance(arg, javalang.tree.MemberReference):
                                        method_args.append(arg.member)
                                    elif isinstance(arg, javalang.tree.Literal):
                                        method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                    # else:
                                    #     method_args.append(str(arg))
                                    # elif isinstance(arg, javalang.tree.BinaryOperation):
                                    #     method_args(get_BinOp(initializer))
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
                        # elif isinstance(initializer, javalang.tree.BinaryOperation):
                        #     local_vars[var_name] = get_BinOp(initializer)

                        else:
                            # Jika initializer adalah literal
                            local_vars[var_name] = getattr(initializer, 'value', 'None')

                elif isinstance(then_statement, javalang.tree.StatementExpression):
                    expression = then_statement.expression
                    if isinstance(expression, javalang.tree.This):
                        expression = expression.selectors[0]

                    # Jika expression adalah pemanggilan metode
                    if isinstance(expression, javalang.tree.MethodInvocation):
                        method_name = expression.member
                        qualifier = expression.qualifier if hasattr(expression, 'qualifier') else None
                        # method_args = [str(arg.value if hasattr(arg, 'value') else arg) for arg in expression.arguments]
                        method_args = []

                        if method_name == 'format':
                            args = expression.arguments
                            if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                format_str = args[0].value

                            if format_str:
                                keywords = []
                                for arg in args[1:]:
                                    if isinstance(arg, javalang.tree.Literal):
                                        keywords.append(arg.value.replace("'",'').replace('"',''))
                                    elif isinstance(arg, javalang.tree.MemberReference):
                                        keywords.append(arg.member.replace("'",'').replace('"',''))
                                    elif isinstance(arg, javalang.tree.MethodInvocation):
                                        arg1 = arg.arguments
                                        for arg2 in arg1:
                                            if isinstance(arg2, javalang.tree.Literal):
                                                keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                break

                                if keywords:
                                    format_str = convert_java_format_to_python(format_str, *keywords)
                                method_args.append(format_str)
                        else:
                            for arg in expression.arguments:
                                if isinstance(arg, javalang.tree.This):
                                    arg = arg.selectors[0]
                                if isinstance(arg, javalang.tree.ClassReference):
                                    method_args.append(arg.type.name+".class")
                                elif isinstance(arg, javalang.tree.MemberReference):
                                    method_args.append(arg.member)
                                elif isinstance(arg, javalang.tree.BinaryOperation):
                                    method_args(get_BinOp(initializer))
                                elif isinstance(arg, javalang.tree.Literal):
                                    method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                # else:
                                #     method_args.append(str(arg))

                        called_methods.append({
                            "method": method_name,
                            "arguments": method_args,
                            "qualifier": qualifier
                        })
                        called_set.add((method_name, len(method_args), qualifier))
                    elif isinstance(expression, javalang.tree.Assignment):
                        declarator = expression

                        if isinstance(declarator.expressionl, javalang.tree.MemberReference):
                            var_name = declarator.expressionl.member

                        initializer = declarator.value

                        if isinstance(initializer, javalang.tree.This):
                            initializer = initializer.selectors[0]

                        # Jika initializer adalah pemanggilan metode
                        if isinstance(initializer, javalang.tree.MethodInvocation):
                            method_name = initializer.member
                            qualifier = initializer.qualifier if hasattr(initializer, 'qualifier') else None
                            # method_args = [str(arg.value if hasattr(arg, 'value') else arg) for arg in initializer.arguments]
                            method_args = []

                            if method_name == 'format':
                                args = initializer.arguments
                                if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                    format_str = args[0].value

                                if format_str:
                                    keywords = []
                                    for arg in args[1:]:
                                        if isinstance(arg, javalang.tree.Literal):
                                            keywords.append(arg.value.replace("'",'').replace('"',''))
                                        elif isinstance(arg, javalang.tree.MemberReference):
                                            keywords.append(arg.member.replace("'",'').replace('"',''))
                                        elif isinstance(arg, javalang.tree.MethodInvocation):
                                            arg1 = arg.arguments
                                            for arg2 in arg1:
                                                if isinstance(arg2, javalang.tree.Literal):
                                                    keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                    break

                                    if keywords:
                                        format_str = convert_java_format_to_python(format_str, *keywords)
                                    method_args.append(format_str)
                            else:
                                for arg in initializer.arguments:
                                    if isinstance(arg, javalang.tree.This):
                                        arg = arg.selectors[0]
                                    if isinstance(arg, javalang.tree.ClassReference):
                                        method_args.append(arg.type.name+".class")
                                    elif isinstance(arg, javalang.tree.MemberReference):
                                        method_args.append(arg.member)
                                    elif isinstance(arg, javalang.tree.Literal):
                                        method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                    # else:
                                    #     method_args.append(str(arg))
                            # local_vars[var_name] = {
                            #     "method": method_name,
                            #     "arguments": method_args
                            # }

                            called_methods.append({
                                "method": method_name,
                                "arguments": method_args,
                                "qualifier": qualifier,
                                # "assigned_to": var_name
                            })
                            called_set.add((method_name, len(method_args), qualifier))

                        # elif isinstance(initializer, javalang.tree.ArrayInitializer):
                        #     array_list = []
                        #     for initializer2 in initializer.initializers:
                        #         if isinstance(initializer2, javalang.tree.Literal):
                        #             array_list.append(initializer2.value)
                        #     local_vars[var_name] = array_list

                        # elif isinstance(initializer, javalang.tree.BinaryOperation):
                        #     local_vars[var_name] = get_BinOp(initializer)
                        # else:
                        #     # Jika initializer adalah literal
                        #     local_vars[var_name] = getattr(initializer, 'value', 'None')


        elif isinstance(statement.then_statement, javalang.tree.StatementExpression):

            if isinstance(statement.then_statement.expression, javalang.tree.Assignment):
                declarator = statement.then_statement.expression

                if isinstance(declarator.expressionl, javalang.tree.MemberReference):
                    var_name = declarator.expressionl.member

                initializer = declarator.value

                if isinstance(initializer, javalang.tree.This):
                    initializer = initializer.selectors[0]

                # Jika initializer adalah pemanggilan metode
                if isinstance(initializer, javalang.tree.MethodInvocation):
                    method_name = initializer.member
                    qualifier = initializer.qualifier if hasattr(initializer, 'qualifier') else None
                    # method_args = [str(arg.value if hasattr(arg, 'value') else arg) for arg in initializer.arguments]
                    method_args = []
                    if method_name == 'format':
                        args = initializer.arguments
                        if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                            format_str = args[0].value

                        if format_str:
                            keywords = []
                            for arg in args[1:]:
                                if isinstance(arg, javalang.tree.Literal):
                                    keywords.append(arg.value.replace("'",'').replace('"',''))
                                elif isinstance(arg, javalang.tree.MemberReference):
                                    keywords.append(arg.member.replace("'",'').replace('"',''))
                                elif isinstance(arg, javalang.tree.MethodInvocation):
                                    arg1 = arg.arguments
                                    for arg2 in arg1:
                                        if isinstance(arg2, javalang.tree.Literal):
                                            keywords.append(arg2.value.replace("'",'').replace('"',''))
                                            break

                            if keywords:
                                format_str = convert_java_format_to_python(format_str, *keywords)
                            method_args.append(format_str)
                    else:
                        for arg in initializer.arguments:
                            if isinstance(arg, javalang.tree.This):
                                arg = arg.selectors[0]
                            if isinstance(arg, javalang.tree.ClassReference):
                                method_args.append(arg.type.name+".class")
                            elif isinstance(arg, javalang.tree.MemberReference):
                                method_args.append(arg.member)
                            elif isinstance(arg, javalang.tree.Literal):
                                method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                            # else:
                            #     method_args.append(str(arg))
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

                # elif isinstance(initializer, javalang.tree.BinaryOperation):
                #     local_vars[var_name] = get_BinOp(initializer)
                else:
                    # Jika initializer adalah literal
                    local_vars[var_name] = getattr(initializer, 'value', 'None')

    elif isinstance(statement, javalang.tree.WhileStatement) or isinstance(statement, javalang.tree.ForStatement):
        inside = 'while' if isinstance(statement, javalang.tree.WhileStatement) else 'for'
        if isinstance(statement.body, javalang.tree.BlockStatement):
            for stmt in statement.body.statements:
                if isinstance(stmt, javalang.tree.LocalVariableDeclaration):
                    for declarator in stmt.declarators:
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
                            if method_name == 'format':
                                args = initializer.arguments
                                if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                    format_str = args[0].value

                                if format_str:
                                    keywords = []
                                    for arg in args[1:]:
                                        if isinstance(arg, javalang.tree.Literal):
                                            keywords.append(arg.value.replace("'",'').replace('"',''))
                                        elif isinstance(arg, javalang.tree.MemberReference):
                                            keywords.append(arg.member.replace("'",'').replace('"',''))
                                        elif isinstance(arg, javalang.tree.MethodInvocation):
                                            arg1 = arg.arguments
                                            for arg2 in arg1:
                                                if isinstance(arg2, javalang.tree.Literal):
                                                    keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                    break

                                    if keywords:
                                        format_str = convert_java_format_to_python(format_str, *keywords)
                                    method_args.append(format_str)
                            else:
                                for arg in initializer.arguments:
                                    if isinstance(arg, javalang.tree.This):
                                        arg = arg.selectors[0]
                                    if isinstance(arg, javalang.tree.ClassReference):
                                        method_args.append(arg.type.name+".class")
                                    elif isinstance(arg, javalang.tree.MemberReference):
                                        method_args.append(arg.member)
                                    elif isinstance(arg, javalang.tree.Literal):
                                        method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                    # else:
                                    #     method_args.append(str(arg))
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

                        # elif isinstance(initializer, javalang.tree.BinaryOperation):
                        #     local_vars[var_name] = get_BinOp(initializer)

                        else:
                            # Jika initializer adalah literal
                            local_vars[var_name] = getattr(initializer, 'value', 'None')

                elif isinstance(stmt, javalang.tree.StatementExpression):
                    # print(stmt)
                    expression = stmt.expression
                    if isinstance(expression, javalang.tree.This):
                        expression = expression.selectors[0]

                    # Jika expression adalah pemanggilan metode
                    if isinstance(expression, javalang.tree.MethodInvocation):
                        method_name = expression.member
                        qualifier = expression.qualifier if hasattr(expression, 'qualifier') else None
                        # method_args = [str(arg.value if hasattr(arg, 'value') else arg) for arg in expression.arguments]
                        method_args = []
                        if method_name == 'format':
                            args = expression.arguments
                            if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                format_str = args[0].value

                            if format_str:
                                keywords = []
                                for arg in args[1:]:
                                    if isinstance(arg, javalang.tree.Literal):
                                        keywords.append(arg.value.replace("'",'').replace('"',''))
                                    elif isinstance(arg, javalang.tree.MemberReference):
                                        keywords.append(arg.member.replace("'",'').replace('"',''))
                                    elif isinstance(arg, javalang.tree.MethodInvocation):
                                        arg1 = arg.arguments
                                        for arg2 in arg1:
                                            if isinstance(arg2, javalang.tree.Literal):
                                                keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                break

                                if keywords:
                                    format_str = convert_java_format_to_python(format_str, *keywords)
                                method_args.append(format_str)
                        else:
                            for arg in expression.arguments:
                                if isinstance(arg, javalang.tree.This):
                                    arg = arg.selectors[0]
                                if isinstance(arg, javalang.tree.ClassReference):
                                    method_args.append(arg.type.name+".class")
                                elif isinstance(arg, javalang.tree.MemberReference):
                                    method_args.append(arg.member)
                                elif isinstance(arg, javalang.tree.Literal):
                                    method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                else:
                                    method_args.append(str(arg))

                        called_methods.append({
                            "method": method_name,
                            "arguments": method_args,
                            "qualifier": qualifier
                        })
                        called_set.add((method_name, len(method_args), qualifier))

                    elif isinstance(stmt.expression, javalang.tree.Assignment):
                        declarator = stmt.expression

                        if isinstance(declarator.expressionl, javalang.tree.MemberReference):
                            var_name = declarator.expressionl.member

                        initializer = declarator.value

                        if isinstance(initializer, javalang.tree.This):
                            initializer = initializer.selectors[0]

                        # Jika initializer adalah pemanggilan metode
                        if isinstance(initializer, javalang.tree.MethodInvocation):
                            method_name = initializer.member
                            qualifier = initializer.qualifier if hasattr(initializer, 'qualifier') else None
                            # method_args = [str(arg.value if hasattr(arg, 'value') else arg) for arg in initializer.arguments]
                            method_args = []
                            if method_name == 'format':
                                args = initializer.arguments
                                if isinstance(args[0], javalang.tree.Literal) and '%' in args[0].value:
                                    format_str = args[0].value

                                if format_str:
                                    keywords = []
                                    for arg in args[1:]:
                                        if isinstance(arg, javalang.tree.Literal):
                                            keywords.append(arg.value.replace("'",'').replace('"',''))
                                        elif isinstance(arg, javalang.tree.MemberReference):
                                            keywords.append(arg.member.replace("'",'').replace('"',''))
                                        elif isinstance(arg, javalang.tree.MethodInvocation):
                                            arg1 = arg.arguments
                                            for arg2 in arg1:
                                                if isinstance(arg2, javalang.tree.Literal):
                                                    keywords.append(arg2.value.replace("'",'').replace('"',''))
                                                    break

                                    if keywords:
                                        format_str = convert_java_format_to_python(format_str, *keywords)
                                    method_args.append(format_str)
                            else:
                                for arg in initializer.arguments:
                                    if isinstance(arg, javalang.tree.This):
                                        arg = arg.selectors[0]
                                    if isinstance(arg, javalang.tree.ClassReference):
                                        method_args.append(arg.type.name+".class")
                                    elif isinstance(arg, javalang.tree.MemberReference):
                                        method_args.append(arg.member)
                                    elif isinstance(arg, javalang.tree.Literal):
                                        method_args.append(str(arg.value if hasattr(arg, 'value') else arg))
                                    else:
                                        method_args.append(str(arg))
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

                        elif isinstance(initializer, javalang.tree.BinaryOperation):
                            local_vars[var_name] = get_BinOp(initializer)
                        else:
                            # Jika initializer adalah literal
                            local_vars[var_name] = getattr(initializer, 'value', 'None')

def get_BinOp(expression):
        """ Rekursif menangani operasi biner dalam ekspresi """
        if isinstance(expression, javalang.tree.BinaryOperation):
            left_operand = get_BinOp(expression.operandl)
            right_operand = get_BinOp(expression.operandr)
            operator = expression.operator
            return f"({left_operand} {operator} {right_operand})"
        elif isinstance(expression, javalang.tree.MemberReference):
            return expression.member
        elif isinstance(expression, javalang.tree.Literal):
            return str(expression.value)
        return "UNKNOWN"

def get_complexity_element(tree):
    operators = {}
    operands = {}

    nodes = 1  # Setiap metode dianggap sebagai satu node
    edges = 1  # Minimal 1 edge untuk memulai eksekusi

    statement_count = 0

    for path, node in tree:
        if isinstance(node, javalang.tree.BinaryOperation):
            # Tambahkan operator biner
            if node.operator in operators.keys():
                operators[node.operator] += 1
            else:
                operators[node.operator] = 1  # Hitung total operator

        elif isinstance(node, javalang.tree.Assignment):
            # Tambahkan operator assignment
            if node.type in operators.keys():
                operators[node.type] += 1
            else:
                operators[node.type] = 1  # Hitung total operator

        elif isinstance(node, javalang.tree.MethodInvocation):
            # Tambahkan nama method sebagai operan
            if node.member in operands.keys():
                operands[node.member] += 1
            else:
                operands[node.member] = 1  # Hitung total operator

        elif isinstance(node, javalang.tree.Literal):
            # Tambahkan literal sebagai operan
            if node.value in operands.keys():
                operands[node.value] += 1
            else:
                operands[node.value] = 1  # Hitung total operator

        elif isinstance(node, javalang.tree.MemberReference):
            # Tambahkan variabel sebagai operan
            if node.member in operands.keys():
                operands[node.member] += 1
            else:
                operands[node.member] = 1  # Hitung total operator

        elif isinstance(node, javalang.tree.VariableDeclarator):
            # Tambahkan deklarasi variabel sebagai operan
            if node.name in operands.keys():
                operands[node.name] += 1
            else:
                operands[node.name] = 1  # Hitung total operator

        if isinstance(node, (javalang.tree.IfStatement,
                                 javalang.tree.ForStatement,
                                 javalang.tree.WhileStatement,
                                 javalang.tree.DoStatement,
                                 javalang.tree.SwitchStatement,
                                 javalang.tree.TryStatement)):
                nodes += 1
                edges += 2  # Percabangan (benar/salah)

        elif isinstance(node, javalang.tree.CatchClause):
            nodes += 1
            edges += 1  # Exception handling menambah satu edge

        elif isinstance(node, javalang.tree.ReturnStatement):
            edges += 1  # Return menghubungkan ke akhir fungsi

        if isinstance(node, (
                javalang.tree.Statement,        # Semua pernyataan
                javalang.tree.IfStatement,      # if
                javalang.tree.ForStatement,     # for
                javalang.tree.WhileStatement,   # while
                javalang.tree.DoStatement,      # do-while
                javalang.tree.SwitchStatement,  # switch
                javalang.tree.ReturnStatement,  # return
                javalang.tree.TryStatement,     # try-catch-finally
                javalang.tree.ThrowStatement,   # throw
                javalang.tree.BreakStatement,   # break
                javalang.tree.ContinueStatement # continue
            )):
                statement_count += 1

    return operands, operators, nodes, edges, statement_count


# tree_contents = _extract_from_dir("./example/java/test", _parse_tree_content, "java")
# print(tree_contents)
# variable_func = _parse_function_variable(tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['functions'], indent=2))


