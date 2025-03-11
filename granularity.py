import java, py, js, php, go

def calculate_noo(function):
    return len(function.keys())

def calculate_no_nanoentities(variable_func):
    global_vars = variable_func['global_vars']
    functions = variable_func['functions']

    total_nanoentities_globals = len([k for k in global_vars.keys() if not k.endswith('.called_methods')])

    total_nanoentities_functions = calculate_noo(functions)

    # nanoentities_function_local_vars = [k for k,v in {v for k,v in functions.items()}['local_vars']  if k != 'Parameter'and k != 'Return']
    total_nanoentities_function_local_vars = 0
    for k,v in functions.items():
        if 'local_vars' in v.keys():
            for a,b in v['local_vars'].items():
                if a != 'Parameter' and a != 'Return':
                    total_nanoentities_function_local_vars = total_nanoentities_function_local_vars + 1

    return total_nanoentities_globals + total_nanoentities_functions + total_nanoentities_function_local_vars

def calculate_loc(tree_contents):
    if 'loc' in tree_contents.keys():
        return tree_contents['loc']

'''Run command'''
lang_list = {
    'java': {'lang': 'java', 'extract': java._extract_from_dir, 'parse' : java._parse_tree_content, 'func': java._parse_function_variable},
    'py': {'lang': 'py', 'extract': py._extract_from_dir, 'parse' : py._parse_tree_content, 'func': py._parse_function_variable},
    'js': {'lang': 'js', 'extract': js._extract_from_dir, 'parse' : js._parse_tree_content, 'func': js._parse_function_variable},
    'php': {'lang': 'php', 'extract': php._extract_from_dir, 'parse' : php._parse_tree_content, 'func': php._parse_function_variable},
    'go': {'lang': 'go', 'extract': go._extract_from_dir, 'parse' : go._parse_tree_content, 'func': go._parse_function_variable}
}

lang = 'java'
# dir_path = "D://DATA//java//intellij//bravo-branch-service//src//main"
# dir_path = 'C://Users//ARD//Desktop//DeathStarBench-master//hotelReservation//services'
# dir_path = "C://Users//ARD//Desktop//robot-shop"
dir_path = "./java/rs"
tree_contents = lang_list[lang]['extract'](dir_path, lang_list[lang]['parse'], lang)
# print(tree_contents)
variable_func = lang_list[lang]['func'](tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['global_vars'], indent=2))
# print(json.dumps(variable_func['functions'], indent=2))

noo = calculate_noo(variable_func['functions'])
print(noo)

no_nanoentities = calculate_no_nanoentities(variable_func)
print(no_nanoentities)

loc = calculate_loc(tree_contents)
print(loc)