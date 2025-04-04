import os
import json
import ast
import astor
from typing import Tuple, List

class GlobalVariableVisitor(ast.NodeVisitor):
    def __init__(self):
        self.global_vars = {
            'called_methods': []
        }
        self.global_func = {}
        self.current_function = None
        self.current_def = None

    def visit_Expr(self, node):
        """Mendeteksi ekspresi metode yang dipanggil tanpa assignment"""
        if isinstance(node.value, ast.Call):
            method_data = self.extract_method_data(node.value)
            if self.current_def and self.current_function:
                self.global_func[f"{self.current_def}.{self.current_function}"]['called_methods'].append(method_data)
            elif self.current_function:
                self.global_func[f"{self.current_function}"]['called_methods'].append(method_data)
            else:
                self.global_vars['called_methods'].append(method_data)
        elif isinstance(node.value, ast.Await) or isinstance(node.value, ast.AsyncWith) :
            node1 = node.value
            if isinstance(node1.value, ast.Call):
                method_data = self.extract_method_data(node1.value)

                if self.current_def and self.current_function:
                    self.global_func[f"{self.current_def}.{self.current_function}"]['called_methods'].append(method_data)
                elif self.current_function:
                    self.global_func[self.current_function]['called_methods'].append(method_data)

        # elif isinstance(node.va)
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Mendeteksi variabel yang dideklarasikan di tingkat global"""
        for target in node.targets:
            if isinstance(target, ast.Name):  # Hanya ambil variabel (bukan atribut obj.property)
                if self.current_def and self.current_function:
                    self.global_vars[f"{self.current_def}.{target.id}"] = self.get_value(node.value)
                elif self.current_def and not self.current_function:
                    self.global_vars[f"{self.current_def}.{target.id}"] = self.get_value(node.value)
                elif not self.current_function:
                    self.global_vars[target.id] = self.get_value(node.value)
                else:
                    if self.current_def and self.current_function:
                        self.global_func[f"{self.current_def}.{self.current_function}"]['local_vars'].update({target.id : self.get_value(node.value)})
                    elif self.current_function:
                        self.global_func[self.current_function]['local_vars'].update({target.id : self.get_value(node.value)})

                if isinstance(node.value, ast.Await) or isinstance(node.value, ast.AsyncWith) :
                    node1 = node.value
                    if isinstance(node1.value, ast.Call):
                        method_data = self.extract_method_data(node1.value)
                        method_data["assigned_to"] = self.get_value(target)  # Ambil nama variabel yang menerima hasil

                        if self.current_def and self.current_function:
                            self.global_func[f"{self.current_def}.{self.current_function}"]['called_methods'].append(method_data)
                        elif self.current_function:
                            self.global_func[self.current_function]['called_methods'].append(method_data)


            if isinstance(node.value, ast.Call):
                method_data = self.extract_method_data(node.value)
                method_data["assigned_to"] = self.get_value(target)  # Ambil nama variabel yang menerima hasil

                if self.current_def and self.current_function:
                    self.global_func[f"{self.current_def}.{self.current_function}"]['called_methods'].append(method_data)
                elif self.current_function:
                    self.global_func[self.current_function]['called_methods'].append(method_data)


        self.generic_visit(node)

    def extract_method_data(self, node):
        """Mengekstrak informasi dari pemanggilan metode"""
        if isinstance(node.func, ast.Attribute):  # Jika metode dipanggil dalam objek (userService.bar)
            qualifier = self.get_full_qualifier(node.func.value) if self.get_full_qualifier(node.func.value) else node.func.attr
            method_name = node.func.attr  # Ambil nama metode (bar)
        elif isinstance(node.func, ast.Name):  # Jika fungsi dipanggil langsung (printGo)
            qualifier = None
            method_name = node.func.id
        else:
            qualifier = None
            method_name = "Unknown"

        # Ambil argumen dalam bentuk string
        # print(node.keywords[0].value)
        # arguments = [astor.to_source(arg).strip() for arg in node.args]

        arguments = []
        if node.args:
            for arg in node.args:
                if isinstance(arg, ast.Call) and arg.keywords:
                    arguments.append(self.visit_call_keyword(arg))
                else:
                    arguments.append(self.get_value(arg))

        if node.keywords:
            # arguments.extend([astor.to_source(arg.value).strip() for arg in node.keywords])
            for kw in node.keywords:
                value = astor.to_source(kw.value).strip()
                if "self." in value:
                    value = value.replace("self.",'')

                arguments.append(value)

        return {
            "method": method_name,
            "arguments": arguments,
            "qualifier": qualifier
        }

    def get_full_qualifier(self, node):
        """Mengembalikan qualifier (objek pemanggil) dalam pemanggilan metode."""
        if isinstance(node, ast.Name):  # Contoh: logging.method()
            return node.id
        elif isinstance(node, ast.Attribute):  # Contoh: app.logger.method()
            return self.get_full_qualifier(node.value) + "." + node.attr
        return None  # Tidak diketahui

    def visit_FunctionDef(self, node):
        """Mendeteksi fungsi yang didefinisikan di global scope"""
        local_vars = {}
        params = []

        self.current_function = node.name
        for arg in node.args.args:
            param_name = arg.arg  # Nama parameter
            param_type = self.get_annotation(arg.annotation)  # Ambil tipe parameter
            if param_name != 'self':
                params.append({
                    "name": param_name,
                    "type": param_type
                    })

        local_vars['Parameter'] = params

        route_info = self.visit_route(node)
        if route_info and 'methods' in route_info:
            local_vars['Http_method'] = route_info['methods']

        # return_type = self.get_annotation(node.returns)  # Ambil tipe return jika ada
        # return_values = self.get_return_values(node)  # Ambil return values dalam fungsi
        path = f"{self.current_def}.{self.current_function}" if self.current_def else self.current_function
        self.global_func[path] = {
            'local_vars': local_vars,
            'called_methods': []
        }

        self.generic_visit(node)
        return_values, return_type  = self.get_return_values(node)

        if return_type:
            self.global_func[path]['local_vars']['Return'] = return_type

        self.current_function = None

    def visit_route(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr == "route":
                    route_info = {
                        "path": None,
                        "methods": None
                    }

                    # Ambil argumen pertama sebagai path
                    # if decorator.args:
                        # for arg in decorator.args:
                        # route_info["path"] = ast.unparse(decorator.args[0])

                    # Ambil metode jika didefinisikan dalam keyword arguments
                    for kw in decorator.keywords:
                        if kw.arg == "methods":
                            methods = self.get_value(kw.value)
                            if isinstance(methods, list):
                                route_info["methods"] = methods[0].replace("'",'').replace('"','').lower()

                    # Simpan hasil dengan nama fungsi sebagai key
                    return route_info

    def visit_AsyncFunctionDef(self, node):
        """Extract variables from async functions"""
        local_vars = {}
        params = []

        self.current_function = node.name
        for arg in node.args.args:
            param_name = arg.arg  # Nama parameter
            param_type = self.get_annotation(arg.annotation)  # Ambil tipe parameter
            params.append({
                "name": param_name,
                "type": param_type
                })

        local_vars['Parameter'] = params

        # return_type = self.get_annotation(node.returns)  # Ambil tipe return jika ada
        # return_values = self.get_return_values(node)  # Ambil return values dalam fungsi
        path = f"{self.current_def}.{self.current_function}" if self.current_def else self.current_function
        self.global_func[path] = {
            'local_vars': local_vars,
            'called_methods': []
        }

        self.generic_visit(node)
        return_values, return_type  = self.get_return_values(node)

        if return_type:
            self.global_func[path]['local_vars']['Return'] = return_type

        self.current_function = None

    def visit_With(self, node):
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):  # Detects function call
                func = item.context_expr.func
                name = item.optional_vars.id

                # Check if it is urllib.request.urlopen
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute):
                    method = self.extract_method_data(item.context_expr)
                    self.global_vars[name] = method

        self.generic_visit(node)

    def visit_AsyncWith(self, node):
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):  # Detects function call
                func = item.context_expr.func
                name = item.optional_vars.id

                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute):
                    method = self.extract_method_data(item.context_expr)
                    if self.current_function:
                        self.global_func[f"{self.current_function}"]['local_vars'][name] = method
                    else:
                        self.global_vars[f"{name}"] = method
                elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                    method = self.extract_method_data(item.context_expr)
                    if self.current_function:
                        self.global_func[f"{self.current_function}"]['local_vars'][name] = method
                    else:
                        self.global_vars[f"{name}"] = method

                if self.current_function:
                    if isinstance(item.context_expr, ast.Call):
                        method_data = self.extract_method_data(item.context_expr)
                        method_data["assigned_to"] = name

                        if self.current_def and self.current_function:
                            self.global_func[f"{self.current_def}.{self.current_function}"]['called_methods'].append(method_data)
                        elif self.current_function:
                            self.global_func[self.current_function]['called_methods'].append(method_data)

        self.generic_visit(node)

    def get_return_values(self, node):
        """Mengembalikan daftar nilai yang direturn dalam fungsi sebagai list"""
        return_values = []
        return_types= []
        for sub_node in ast.walk(node):  # Menelusuri seluruh node dalam fungsi
            if isinstance(sub_node, ast.Return) and sub_node.value is not None:
                return_values = self.get_value(sub_node.value)
                if return_values:
                    return_values = list(self.get_value(sub_node.value))
                return_type = self.get_type_value(sub_node.value)

                if isinstance(return_type, Tuple):
                    return_types = list(return_type)
                elif isinstance(return_type, List):
                    return_types = return_type
                else:
                    return_types.append(return_type)

        return return_values, return_types

    def get_annotation(self, annotation):
        """Mengembalikan tipe parameter sebagai string"""
        if annotation is None:
            return "Unknown Type"  # Jika tidak ada annotation
        elif isinstance(annotation, ast.Name):
            return annotation.id  # Contoh: int, str, float
        elif isinstance(annotation, ast.Subscript):
            return self.get_annotation(annotation.value) + f"[{self.get_annotation(annotation.slice)}]"
        return "Unknown Type"

    # def visit_Global(self, node):
    #     """Mendeteksi variabel yang dideklarasikan sebagai 'global' dalam fungsi"""
    #     for name in node.names:
    #         self.global_vars[name] = "Declared as global, value set elsewhere"

    def get_value(self, node):
        """Mengubah node AST ke dalam bentuk Python yang bisa dibaca"""
        if isinstance(node, ast.Str):  # Python < 3.8 String
            return f'"{node.s}"'
        elif isinstance(node, ast.Await):
            return self.get_value(node.value)
        elif isinstance(node, ast.Num):  # Python < 3.8 Angka
            return node.n
        elif isinstance(node, ast.NameConstant):  # Python < 3.8 Boolean/None
            return node.value
        elif isinstance(node, ast.List):  # List []
            return [self.get_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Dict):  # Dictionary {}
            return {self.get_value(k): self.get_value(v) for k, v in zip(node.keys, node.values)}
        elif isinstance(node, ast.Tuple):  # Tuple ()
            return tuple(self.get_value(elt) for elt in node.elts)
        elif isinstance(node, ast.Name):  # Variabel lain
            # return {
            #     "type": "reference",
            #     "value": node.id
            # }
            return node.id
        elif isinstance(node, ast.BinOp):  # Operasi seperti 5 + 3
            return f"({self.get_value_BinOp(node.left)} {self.get_operator_BinOp(node.op)} {self.get_value_BinOp(node.right)})"
        elif isinstance(node, ast.Call):  # Panggilan fungsi seperti func()
            # arguments = []
            # if node.args:
            #     for arg in node.args:
            #         arguments.append(self.get_value(arg))

            return self.visit_Call(node)

        elif isinstance(node, ast.Subscript):  # Contoh: my_list[0](arg1)
            return self.get_value(node.value) + "[" + self.get_value(node.slice) + "]"
        return "Unknown Type"

    def visit_call_keyword(self, node):
        if isinstance(node, ast.Call):
            # print(node.func.value.s)
            if isinstance(node.func.value, ast.Str) and node.func.attr == 'format' :
                # Ambil string format awal
                format_str = node.func.value.s
                new_values = {}
                for kw in node.keywords:
                    value = self.get_value(kw.value)
                    if value and isinstance(value, str):
                        value = value.replace("'",'').replace('"','')
                    new_values[kw.arg] = value

                # Gantikan placeholder `{var}` dengan namanya langsung
                new_str = format_str.format(**new_values)
                return f'"{new_str}"'
            else:
                return astor.to_source(node.func.value).strip()

    def visit_Call(self, node):
        # arguments = [self.get_value(arg) for arg in node.args]  # Ambil argumen
        arguments = []
        if node.args:
            for arg in node.args:
                if isinstance(arg, ast.Call) and arg.keywords:
                    arguments.append(self.visit_call_keyword(arg))
                else:
                    arguments.append(self.get_value(arg))

        if isinstance(node.func, ast.Name):  # Contoh: func()
            method_name = node.func.id
            qualifier = None
        elif isinstance(node.func, ast.Attribute):  # Contoh: obj.method()
            method_name = node.func.attr
            qualifier = self.get_full_qualifier(node.func.value)
        elif isinstance(node.func, ast.Subscript):  # Contoh: my_list[0](arg1)
            method_name = self.get_value(node.func.value) + "[" + self.get_value(node.func.slice) + "]"
            qualifier = None
        else:
            method_name = "Unknown"
            qualifier = None

        return {
            "method": method_name,
            "arguments": arguments,
            "qualifier": qualifier
        }

    def get_type_value(self, node):

        if isinstance(node, ast.Str):
            type_of = 'str'
        elif isinstance(node, ast.Num):
            type_of = 'int'
        elif isinstance(node, ast.NameConstant):
            type_of = 'bool' if node else ''
        elif isinstance(node, ast.List):
            type_of = [self.get_type_value(elt) for elt in node.elts]
            return type_of
        elif isinstance(node, ast.Dict):
            type_of = {self.get_value(k): self.get_type_value(v) for k, v in zip(node.keys, node.values)}
            return type_of
        elif isinstance(node, ast.Tuple):
            type_of = tuple(self.get_type_value(elt) for elt in node.elts)
            return type_of
        elif isinstance(node, ast.Name):
            type_return = type(self.global_func[self.current_function]['local_vars'][node.id]) if self.current_function in self.global_func and node.id in self.global_func[self.current_function]['local_vars'].keys() else type('str')
            type_of = type_return.__name__
        elif isinstance(node, ast.BinOp):
            type_of = f"({self.get_type_value(self.get_value_BinOp(node.left))} {self.get_type_value(self.get_operator_BinOp(node.op))} {self.get_type_value(self.get_value_BinOp(node.right))})"
        elif isinstance(node, ast.Call):
            arguments = []
            # if node.args:
            #     for arg in node.args:
            #         arguments.append(self.get_type_value(arg))
            # print(node.func.id, node.args[0].s)
            type_of = 'method'

            if node.args:
                type_of = self.get_type_value(node.args[0])
            return type_of
        else:
            type_of = "Unknown Type"

        return {
            "type": type_of
        }

    def get_value_BinOp(self, node):
        """Mengambil nilai dari operand kiri atau kanan"""
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.NameConstant):
            return node.value
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            return f"({self.get_value_BinOp(node.left)} {self.get_operator_BinOp(node.op)} {self.get_value_BinOp(node.right)})"
        return "Unknown"

    def get_operator_BinOp(self, node):
        """Mengonversi operator menjadi string"""
        operators = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.Mod: "%",
            ast.Pow: "**",
            ast.FloorDiv: "//"
        }
        return operators.get(type(node), "?")

    def visit_ClassDef(self, node):
        """
        Mengunjungi setiap definisi class dan mencari variabel di dalamnya.
        """
        self.current_def = node.name

        self.generic_visit(node)
        self.current_def = None

    def parse_value(self, node):
        """
        Konversi nilai AST ke format yang diinginkan.
        """
        # print(node)
        if isinstance(node, ast.Call):
            arguments = [astor.to_source(kw.value) for kw in node.keywords]
            return {
                "method": node.func.attr,
                "arguments": arguments,
                "qualifier": self.get_full_qualifier(node.func.value)
            }
            # return self.visit_Call(node)

        elif isinstance(node, ast.Attribute):
            arguments = [astor.to_source(arg).strip() for arg in node.args]
            return {
                "method": node.func.attr,
                "arguments": arguments,
                "qualifier": node.func.value
            }

        else:
            return self.get_value(node)  # Gunakan ast.unparse untuk menangani kasus lain

    def get_class_name(self, node):
        """
        Mencari nama class dari function yang sedang dianalisis.
        """
        while node:
            if isinstance(node, ast.ClassDef):
                return node.name
            elif isinstance(node, ast.FunctionDef):
                return node.name
            node = getattr(node, "parent", None)
        return None

    def set_parents(self, node, parent=None):
        """
        Menetapkan hubungan parent-child di AST agar bisa mendapatkan class name.
        """
        for child in ast.iter_child_nodes(node):
            setattr(child, "parent", node)
            self.set_parents(child, node)

class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.global_vars = {
            'called_methods': []
        }
        self.global_func = {}
        self.functions = {}
        self.current_function = None
        self.current_def = None

    def visit_Expr(self, node):
        """Mendeteksi ekspresi metode yang dipanggil tanpa assignment"""
        if self.current_def:
            if isinstance(node.value, ast.Call):
                method_data = self.extract_method_data(node.value)
                if self.current_def and self.current_function:
                    if f"{self.current_def}.{self.current_function}" in self.global_func:
                        self.global_func[f"{self.current_def}.{self.current_function}"]['called_methods'].append(method_data)
                    else:
                        self.global_func[f"{self.current_def}.{self.current_function}"] = {'called_methods': [method_data]}
                elif self.current_function:
                    self.global_func[f"{self.current_function}"]['called_methods'].append(method_data)
                else:
                    self.global_vars['called_methods'].append(method_data)
            elif isinstance(node.value, ast.Await) or isinstance(node.value, ast.AsyncWith) :
                node1 = node.value
                if isinstance(node1.value, ast.Call):
                    method_data = self.extract_method_data(node1.value)

                    if self.current_def and self.current_function:
                        self.global_func[f"{self.current_def}.{self.current_function}"]['called_methods'].append(method_data)
                    elif self.current_function:
                        self.global_func[self.current_function]['called_methods'].append(method_data)

        # elif isinstance(node.va)
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Mendeteksi variabel yang dideklarasikan di tingkat global"""
        for target in node.targets:
            if isinstance(target, ast.Name):  # Hanya ambil variabel (bukan atribut obj.property)
                # print(target, self.current_def, self.current_function)
                if self.current_def and self.current_function:
                    # self.global_vars[f"{self.current_def}.{target.id}"] = self.get_value(node.value)
                    self.functions[f"{self.current_def}.{self.current_function}"]['local_vars'].update({target.id: self.get_value(node.value)})
                elif self.current_def and not self.current_function:
                    self.global_vars[f"{self.current_def}.{target.id}"] = self.get_value(node.value)
                elif not self.current_function:
                    self.global_vars[target.id] = self.get_value(node.value)
                else:
                    if self.current_def:
                        if self.current_def and self.current_function:
                            self.functions[f"{self.current_def}.{self.current_function}"]['local_vars'].update({target.id : self.get_value(node.value)})
                        elif self.current_function:
                            if self.global_func[self.current_function]['local_vars']:
                                self.global_func[self.current_function]['local_vars'].update({target.id : self.get_value(node.value)})
                            else:
                                self.global_func[self.current_function]['local_vars'] = {target.id : self.get_value(node.value)}

                if isinstance(node.value, ast.Await) or isinstance(node.value, ast.AsyncWith) :
                    node1 = node.value
                    if isinstance(node1.value, ast.Call):
                        method_data = self.extract_method_data(node1.value)
                        method_data["assigned_to"] = self.get_value(target)  # Ambil nama variabel yang menerima hasil

                        if self.current_def and self.current_function:
                            self.global_func[f"{self.current_def}.{self.current_function}"]['called_methods'].append(method_data)
                        elif self.current_function:
                            self.global_func[self.current_function]['called_methods'].append(method_data)


            if isinstance(node.value, ast.Call):
                method_data = self.extract_method_data(node.value)
                method_data["assigned_to"] = self.get_value(target)  # Ambil nama variabel yang menerima hasil
                if self.current_def:
                    if self.current_def and self.current_function:
                        if 'called_methods' in self.functions[f"{self.current_def}.{self.current_function}"]:
                            self.functions[f"{self.current_def}.{self.current_function}"]['called_methods'].append(method_data)
                        else:
                            self.functions[f"{self.current_def}.{self.current_function}"].update({'called_methods': [method_data]})
                    elif self.current_function:
                        self.global_func[self.current_function]['called_methods'].append(method_data)


        self.generic_visit(node)

    def extract_method_data(self, node):
        """Mengekstrak informasi dari pemanggilan metode"""
        if isinstance(node.func, ast.Attribute):  # Jika metode dipanggil dalam objek (userService.bar)
            qualifier = self.get_full_qualifier(node.func.value) if self.get_full_qualifier(node.func.value) else node.func.attr
            method_name = node.func.attr  # Ambil nama metode (bar)
        elif isinstance(node.func, ast.Name):  # Jika fungsi dipanggil langsung (printGo)
            qualifier = None
            method_name = node.func.id
        else:
            qualifier = None
            method_name = "Unknown"

        # Ambil argumen dalam bentuk string
        # print(node.keywords[0].value)
        # arguments = [astor.to_source(arg).strip() for arg in node.args]

        arguments = []
        if node.args:
            for arg in node.args:
                if isinstance(arg, ast.Call) and arg.keywords:
                    arguments.append(self.visit_call_keyword(arg))
                else:
                    arguments.append(self.get_value(arg))

        if node.keywords:
            # arguments.extend([astor.to_source(arg.value).strip() for arg in node.keywords])
            for kw in node.keywords:
                value = astor.to_source(kw.value).strip()
                if "self." in value:
                    value = value.replace("self.",'')

                arguments.append(value)

        return {
            "method": method_name,
            "arguments": arguments,
            "qualifier": qualifier
        }

    def get_full_qualifier(self, node):
        """Mengembalikan qualifier (objek pemanggil) dalam pemanggilan metode."""
        if isinstance(node, ast.Name):  # Contoh: logging.method()
            return node.id
        elif isinstance(node, ast.Attribute):  # Contoh: app.logger.method()
            return self.get_full_qualifier(node.value) + "." + node.attr
        return None  # Tidak diketahui

    def get_annotation(self, annotation):
        """Mengembalikan tipe parameter sebagai string"""
        if annotation is None:
            return "Unknown Type"  # Jika tidak ada annotation
        elif isinstance(annotation, ast.Name):
            return annotation.id  # Contoh: int, str, float
        elif isinstance(annotation, ast.Subscript):
            return self.get_annotation(annotation.value) + f"[{self.get_annotation(annotation.slice)}]"
        return "Unknown Type"

    # def visit_Global(self, node):
    #     """Mendeteksi variabel yang dideklarasikan sebagai 'global' dalam fungsi"""
    #     for name in node.names:
    #         self.global_vars[name] = "Declared as global, value set elsewhere"

    def get_value(self, node):
        """Mengubah node AST ke dalam bentuk Python yang bisa dibaca"""
        # print(node)
        if isinstance(node, ast.Str):  # Python < 3.8 String
            return f'"{node.s}"'
        elif isinstance(node, ast.Await):
            return self.get_value(node.value)
        elif isinstance(node, ast.Num):  # Python < 3.8 Angka
            return node.n
        elif isinstance(node, ast.NameConstant):  # Python < 3.8 Boolean/None
            return node.value
        elif isinstance(node, ast.List):  # List []
            return [self.get_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Dict):  # Dictionary {}
            return {self.get_value(k): self.get_value(v) for k, v in zip(node.keys, node.values)}
        elif isinstance(node, ast.Tuple):  # Tuple ()
            return tuple(self.get_value(elt) for elt in node.elts)
        elif isinstance(node, ast.Name):  # Variabel lain
            # return {
            #     "type": "reference",
            #     "value": node.id
            # }
            return node.id
        elif isinstance(node, ast.BinOp):  # Operasi seperti 5 + 3
            return f"({self.get_value_BinOp(node.left)} {self.get_operator_BinOp(node.op)} {self.get_value_BinOp(node.right)})"
        elif isinstance(node, ast.Call):  # Panggilan fungsi seperti func()
            arguments = []
            if node.args:
                for arg in node.args:
                    arguments.append(self.get_value(arg))

            return self.visit_Call(node)

        elif isinstance(node, ast.Subscript):  # Contoh: my_list[0](arg1)
            return self.get_value(node.value) + "[" + self.get_value(node.slice) + "]"
        return "Unknown Type"

    def visit_call_keyword(self, node):
        if isinstance(node, ast.Call):
            # print(node.func.value.s)
            if isinstance(node.func.value, ast.Str):
                # Ambil string format awal
                format_str = node.func.value.s
                new_values = {}
                for kw in node.keywords:
                    value = self.get_value(kw.value)
                    if value and isinstance(value, str):
                        value = value.replace("'",'').replace('"','')
                    new_values[kw.arg] = value

                # Gantikan placeholder `{var}` dengan namanya langsung
                new_str = format_str.format(**new_values)
                return f'"{new_str}"'

            else:
                return astor.to_source(node.func.value).strip()

    def visit_Call(self, node):
        # arguments = [self.get_value(arg) for arg in node.args]  # Ambil argumen
        arguments = []
        if node.args:
            for arg in node.args:
                if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == 'format' and arg.keywords:
                        arguments.append(self.visit_call_keyword(arg))
                else:
                    arguments.append(self.get_value(arg))

        if isinstance(node.func, ast.Name):  # Contoh: func()
            method_name = node.func.id
            qualifier = None
        elif isinstance(node.func, ast.Attribute):  # Contoh: obj.method()
            method_name = node.func.attr
            qualifier = self.get_full_qualifier(node.func.value)
        elif isinstance(node.func, ast.Subscript):  # Contoh: my_list[0](arg1)
            method_name = self.get_value(node.func.value) + "[" + self.get_value(node.func.slice) + "]"
            qualifier = None
        else:
            method_name = "Unknown"
            qualifier = None

        return {
            "method": method_name,
            "arguments": arguments,
            "qualifier": qualifier
        }

    def get_type_value(self, node):

        if isinstance(node, ast.Str):  # Python < 3.8 String
            type_of = 'str'
        elif isinstance(node, ast.Num):  # Python < 3.8 Angka
            type_of = 'int'
        elif isinstance(node, ast.NameConstant):  # Python < 3.8 Boolean/None
            type_of = 'bool' if node else ''
        elif isinstance(node, ast.List):  # List []
            type_of = [self.get_type_value(elt) for elt in node.elts]
            return type_of
        elif isinstance(node, ast.Dict):  # Dictionary {}
            type_of = {self.get_value(k): type(self.get_type_value(v)) for k, v in zip(node.keys, node.values)}
            return type_of
        elif isinstance(node, ast.Tuple):  # Tuple ())
            type_of = tuple(self.get_type_value(elt) for elt in node.elts)
            return type_of
        elif isinstance(node, ast.Name):  # Variabel lain
            # print(type(self.global_func[self.current_function]['local_vars'][node.id]))
            type_return = type(self.global_func[self.current_function]['local_vars'][node.id]) if node.id in self.global_func[self.current_function]['local_vars'].keys() else type('str')
            type_of = type_return.__name__
        elif isinstance(node, ast.BinOp):  # Operasi seperti 5 + 3
            type_of = f"({self.get_type_value(self.get_value_BinOp(node.left))} {self.get_type_value(self.get_operator_BinOp(node.op))} {self.get_type_value(self.get_value_BinOp(node.right))})"
        elif isinstance(node, ast.Call):  # Panggilan fungsi seperti func()
            arguments = []
            # if node.args:
            #     for arg in node.args:
            #         arguments.append(self.get_type_value(arg))
            # print(node.func.id, node.args[0].s)
            type_of = self.get_type_value(node.args[0])
            return type_of
        else:
            type_of = "Unknown Type"

        return {
            "type": type_of
        }

    def get_value_BinOp(self, node):
        """Mengambil nilai dari operand kiri atau kanan"""
        if isinstance(node, ast.Str):  # Python < 3.8 String
            return node.s
        elif isinstance(node, ast.Num):  # Python < 3.8 Angka
            return node.n
        elif isinstance(node, ast.NameConstant):  # Python < 3.8 Boolean/None
            return node.value
        elif isinstance(node, ast.Name):  # Variabel seperti 'a'
            return node.id
        elif isinstance(node, ast.BinOp):  # Operasi dalam operasi (nested)
            return f"({self.get_value_BinOp(node.left)} {self.get_operator_BinOp(node.op)} {self.get_value_BinOp(node.right)})"
        return "Unknown"

    def get_operator_BinOp(self, node):
        """Mengonversi operator menjadi string"""
        operators = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.Mod: "%",
            ast.Pow: "**",
            ast.FloorDiv: "//"
        }
        return operators.get(type(node), "?")

    def parse_value(self, node):
        """
        Konversi nilai AST ke format yang diinginkan.
        """
        # print(node)
        if isinstance(node, ast.Call):
            arguments = [astor.to_source(kw.value) for kw in node.keywords]
            return {
                "method": node.func.attr,
                "arguments": arguments,
                "qualifier": self.get_full_qualifier(node.func.value)
            }
            # return self.visit_Call(node)

        elif isinstance(node, ast.Attribute):
            arguments = [astor.to_source(arg).strip() for arg in node.args]
            return {
                "method": node.func.attr,
                "arguments": arguments,
                "qualifier": node.func.value
            }

        else:
            return self.get_value(node)  # Gunakan ast.unparse untuk menangani kasus lain

    def visit_FunctionDef(self, node):
        """
        Mengunjungi setiap function dalam class untuk mendapatkan:
        - Parameter function
        - Local variables
        - Called methods
        """
        class_name = self.get_class_name(node)
        self.current_function = node.name
        if class_name and self.current_def:
            func_path = f"{self.current_def}.{class_name}"

            # Ekstrak parameter function
            parameters = []
            for arg in node.args.args:
                param_name = arg.arg
                param_type = "Unknown Type"  # Python AST tidak menyimpan tipe
                parameters.append({"name": param_name, "type": param_type})

            route_info = self.visit_route(node)
            http_method = ''
            if route_info and 'methods' in route_info:
                http_method = route_info['methods']

            # Ekstrak variabel lokal
            local_vars = {}
            called_methods = []

            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    # Jika ada variabel yang di-assign dalam function
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                            var_name = f"self.{target.attr}"
                            # print(var_name)
                            var_value = self.parse_value(stmt.value)
                            local_vars[var_name] = var_value
                elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    # Jika ada pemanggilan method dalam function
                    method_call = self.extract_method_data(stmt.value)
                    if method_call:
                        called_methods.append(method_call)

            # Simpan hasil analisis function
            self.functions[func_path] = {
                "local_vars": {"Parameter": parameters, "Http_method": http_method, **local_vars},
                "called_methods": called_methods
            }

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """
        Mengunjungi setiap definisi class dan mencari variabel di dalamnya.
        """
        self.current_def = node.name

        self.generic_visit(node)
        self.current_def = None

    def visit_route(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr == "route":
                    route_info = {
                        "path": None,
                        "methods": None
                    }

                    # Ambil argumen pertama sebagai path
                    # if decorator.args:
                        # for arg in decorator.args:
                        # route_info["path"] = ast.unparse(decorator.args[0])

                    # Ambil metode jika didefinisikan dalam keyword arguments
                    for kw in decorator.keywords:
                        if kw.arg == "methods":
                            methods = self.get_value(kw.value)
                            if isinstance(methods, list):
                                route_info["methods"] = methods[0].replace("'",'').replace('"','').lower()

                    # Simpan hasil dengan nama fungsi sebagai key
                    return route_info

    def visit_AsyncFunctionDef(self, node):
        """Extract variables from async functions"""
        local_vars = {}
        params = []

        class_name = self.get_class_name(node)
        if class_name and self.current_def:
            func_path = f"{self.current_def}.{class_name}"

        self.current_function = func_path
        for arg in node.args.args:
            param_name = arg.arg  # Nama parameter
            param_type = self.get_annotation(arg.annotation)  # Ambil tipe parameter
            params.append({
                "name": param_name,
                "type": param_type
                })

        local_vars['Parameter'] = params

        # return_type = self.get_annotation(node.returns)  # Ambil tipe return jika ada
        # return_values = self.get_return_values(node)  # Ambil return values dalam fungsi
        path = f"{self.current_def}.{self.current_function}" if self.current_def else self.current_function
        self.functions[path] = {
            'local_vars': local_vars,
            'called_methods': []
        }

        self.generic_visit(node)
        return_values, return_type  = self.get_return_values(node)

        if return_type:
            self.global_func[path]['local_vars']['Return'] = return_type

        self.current_function = None

    def visit_With(self, node):
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):  # Detects function call
                func = item.context_expr.func
                name = item.optional_vars.id

                # Check if it is urllib.request.urlopen
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute):
                    method = self.extract_method_data(item.context_expr)
                    self.global_vars[name] = method

        self.generic_visit(node)

    def visit_AsyncWith(self, node):
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):  # Detects function call
                func = item.context_expr.func
                name = item.optional_vars.id

                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute):
                    method = self.extract_method_data(item.context_expr)
                    if self.current_function:
                        self.global_func[f"{self.current_function}"]['local_vars'][name] = method
                    else:
                        self.global_vars[f"{name}"] = method
                elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                    method = self.extract_method_data(item.context_expr)
                    if self.current_function:
                        self.global_func[f"{self.current_function}"]['local_vars'][name] = method
                    else:
                        self.global_vars[f"{name}"] = method

                if self.current_function:
                    if isinstance(item.context_expr, ast.Call):
                        method_data = self.extract_method_data(item.context_expr)
                        method_data["assigned_to"] = name

                        if self.current_def and self.current_function:
                            self.global_func[f"{self.current_def}.{self.current_function}"]['called_methods'].append(method_data)
                        elif self.current_function:
                            self.global_func[self.current_function]['called_methods'].append(method_data)

        self.generic_visit(node)

    def get_class_name(self, node):
        """
        Mencari nama class dari function yang sedang dianalisis.
        """
        while node:
            if isinstance(node, ast.ClassDef):
                return node.name
            elif isinstance(node, ast.FunctionDef):
                return node.name
            node = getattr(node, "parent", None)
        return None

    def set_parents(self, node, parent=None):
        """
        Menetapkan hubungan parent-child di AST agar bisa mendapatkan class name.
        """
        for child in ast.iter_child_nodes(node):
            setattr(child, "parent", node)
            self.set_parents(child, node)

class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = {}
        self.operators = {}
        self.operands = {}
        self.nodes = 0
        self.edges = 0
        self.statement_count = 0
        self.current_def = None

    def visit_BinOp(self, node):
        """Menghitung operator biner seperti +, -, *, /"""

        if type(node.op).__name__ in self.operators.keys():
            self.operators[type(node.op).__name__] += 1
        else:
            self.operators[type(node.op).__name__] = 1

        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node):
        """Menghitung operator unary seperti -, +"""

        if type(node.op).__name__ in self.operators.keys():
            self.operators[type(node.op).__name__] += 1
        else:
            self.operators[type(node.op).__name__] = 1

        self.visit(node.operand)

    def visit_Assign(self, node):
        """Menghitung assignment '=' dan operannya"""

        if '=' in self.operators.keys():
            self.operators['='] += 1
        else:
            self.operators['='] = 1

        for target in node.targets:
            self.visit(target)
        self.visit(node.value)

    def visit_Compare(self, node):
        """Menghitung operator perbandingan seperti ==, !=, >, <"""
        for op in node.ops:
            # self.operators.add(type(op).__name__)
            # self.operator_count += 1

            if type(op).__name__ in self.operators.keys():
                self.operators[type(op).__name__] += 1
            else:
                self.operators[type(op).__name__] = 1

        self.visit(node.left)
        for comparator in node.comparators:
            self.visit(comparator)

    def visit_BoolOp(self, node):
        """Menghitung operator boolean seperti 'and', 'or'"""
        # self.operators.add(type(node.op).__name__)
        # self.operator_count += 1

        if type(node.op).__name__ in self.operators.keys():
            self.operators[type(node.op).__name__] += 1
        else:
            self.operators[type(node.op).__name__] = 1

        for value in node.values:
            self.visit(value)

    def visit_Call(self, node):
        """Menghitung pemanggilan fungsi sebagai operan"""
        if isinstance(node.func, ast.Name):
        #     self.operands.add(node.func.id)
        # self.operand_count += 1

            if node.func.id in self.operands.keys():
                self.operands[node.func.id] += 1
            else:
                self.operands[node.func.id] = 1
        for arg in node.args:
            self.visit(arg)

    def visit_Name(self, node):
        """Menghitung variabel sebagai operan"""
        # self.operands.add(node.id)
        # self.operand_count += 1

        if node.id in self.operands.keys():
            self.operands[node.id] += 1
        else:
            self.operands[node.id] = 1

    def visit_Constant(self, node):
        """Menghitung konstanta sebagai operan"""
        # self.operands.add(str(node.value))
        # self.operand_count += 1

        if str(node.value) in self.operands.keys():
            self.operands[str(node.value)] += 1
        else:
            self.operands[str(node.value)] = 1

    def visit_ClassDef(self, node):
        """
        Mengunjungi setiap definisi class dan mencari variabel di dalamnya.
        """
        self.current_def = node.name

        self.generic_visit(node)
        self.current_def = None

    def visit_FunctionDef(self, node):
        """
        Mengunjungi setiap function dalam class untuk mendapatkan:
        - Parameter function
        - Local variables
        - Called methods
        """
        func_path = node.name

        class_name = self.get_class_name(node)
        if class_name and self.current_def:
            func_path = f"{self.current_def}.{class_name}"

        self.current_function = func_path

        function_nodes = 1  # Fungsi utama sebagai node pertama
        function_edges = 1  # Minimal 1 edge untuk eksekusi fungsi
        statement_count = 0

        for subnode in ast.walk(node):
            if isinstance(subnode, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                function_nodes += 1
                function_edges += 2  # Satu percabangan menambah dua edges

            elif isinstance(subnode, ast.Return):
                function_edges += 1  # Return menghubungkan ke akhir fungsi

            if isinstance(subnode, (
                ast.Assign,          # Assignment (x = 1)
                ast.Expr,            # Expression (e.g., function calls)
                ast.If,              # If statement
                ast.For,             # For loop
                ast.While,           # While loop
                ast.Try,             # Try-except
                ast.Return,          # Return statement
                ast.With,            # With statement
                ast.Break,           # Break statement
                ast.Continue,        # Continue statement
                ast.Raise            # Raise statement
            )):
                statement_count += 1

        self.nodes += function_nodes
        self.edges += function_edges
        self.statement_count = statement_count

        self.generic_visit(node)

        # Simpan hasil analisis function
        self.functions[func_path] = {
            "operators": self.operators,
            "operands": self.operands,
            "nodes": self.nodes,
            "edges": self.edges,
            "exec_state": self.statement_count,
        }

        self.operators = {}
        self.operands = {}
        self.nodes = 0
        self.edges = 0
        self.statement_count = 0
        self.current_function = None

    def get_class_name(self, node):
        """
        Mencari nama class dari function yang sedang dianalisis.
        """
        while node:
            if isinstance(node, ast.ClassDef):
                return node.name
            elif isinstance(node, ast.FunctionDef):
                return node.name
            node = getattr(node, "parent", None)
        return None

def _extract_from_dir(dir_path, parser, lang) -> dict:
    contents = {}
    loc = 0
    for dirpath, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename.endswith(f".{lang}"):
                file_path = os.path.join(dirpath, filename)
                file_content = parser(file_path)
                # package = _parse_tree_package(file_content)
                package = dirpath.replace('./','').replace('/','.').replace('\\','.').replace('..','.')

                if package:
                    key = package + "." + filename.replace(f".{lang}", "")
                else:
                    key = file_path

                total_loc, effective_loc = count_lines_of_code(file_path)
                loc = loc + effective_loc

                contents[key] = file_content

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
        ".php": ("//", "/*", "*/"),
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
    # print(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        file_contents = f.read()

    return file_contents

def _parse_tree_content(file_path) -> any:
    file_contents = _parse_content(file_path)
    return ast.parse(file_contents)

# def _parse_tree_package(tree_contents) -> str:
#     return tree_contents.package.name

def _parse_function_variable(tree_contents) -> Tuple[dict, dict]:

    # Menyimpan hasil analisis
    functions = {}
    global_vars = {}
    for key, tree in tree_contents.items():
        # print(key, tree)
        if key == 'loc':
            continue

        global_visitor = GlobalVariableVisitor()
        function_call_visitor = FunctionCallVisitor()
        analyzer = ComplexityAnalyzer()

        global_visitor.visit(tree)
        function_call_visitor.visit(tree)
        analyzer.visit(tree)

        for var, value in global_visitor.global_vars.items():
            var_name = key+"."+var
            global_vars[var_name] = value

        for var, value in global_visitor.global_func.items():
            var_name = key+"."+var
            functions[var_name] = value

        for var, value in function_call_visitor.functions.items():
            var_name = key+"."+var
            functions[var_name] = value

        for var, value in analyzer.functions.items():
            var_name = key+'.'+var
            functions[var_name].update(value)

    # print(global_visitor.called_methods)
    variable_func = {
        'global_vars': global_vars,
        'functions': functions
    }
    return variable_func

# tree_contents = _extract_from_dir("./example/py/test", _parse_tree_content, "py")
# tree_contents = _extract_from_dir("C://Users//ARD//Desktop//train-ticket//ts-avatar-service", _parse_tree_content, "py")
# print(tree_contents)
# variable_func = _parse_function_variable(tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['functions'], indent=2))


