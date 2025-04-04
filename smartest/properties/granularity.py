
import sys, os
sys.path.append(os.path.abspath("C:/Users/ARD/Desktop/yukiii-smartest"))
from extract_param import java, py, js, php, go

import json

def _calculate_noo(function):
    return len(function.keys())

def _calculate_average_noo(total_noo, total_services):
    return total_noo / total_services

def _calculate_no_nanoentities(variable_func):
    global_vars = variable_func['global_vars']
    functions = variable_func['functions']

    total_nanoentities_globals = len([k for k in global_vars.keys() if not k.endswith('.called_methods')])

    total_nanoentities_functions = _calculate_noo(functions)

    # nanoentities_function_local_vars = [k for k,v in {v for k,v in functions.items()}['local_vars']  if k != 'Parameter'and k != 'Return']
    total_nanoentities_function_local_vars = 0
    for k,v in functions.items():
        if 'local_vars' in v.keys():
            for a,b in v['local_vars'].items():
                if a != 'Parameter' and a != 'Return':
                    total_nanoentities_function_local_vars = total_nanoentities_function_local_vars + 1

    return total_nanoentities_globals + total_nanoentities_functions + total_nanoentities_function_local_vars

def _calculate_average_no_nanoentities(total_no_nanoentities, total_services):
    return total_no_nanoentities / total_services

def _calculate_loc(tree_contents):
    if 'loc' in tree_contents.keys():
        return tree_contents['loc']

def _calculate_average_loc(total_loc, total_services):
    return total_loc / total_services

def _calculate_sgm(functions):
    endpoint_functions = {function_name: function_data for function_name, function_data in functions.items() if "Http_method" in function_data.get("local_vars", {})}

    total_FP = sum(len(local_vars.get("Parameter", [])) for local_vars in (func.get("local_vars", {}) for func in endpoint_functions.values()))
    total_CP = sum(len(local_vars.get("Return", [])) for local_vars in (func.get("local_vars", {}) for func in endpoint_functions.values()))

    total_O = sum(
        fgs_operation_weights.get(endpoint_functions[func]["local_vars"].get("Http_method", "").lower(), 0)
        for func in endpoint_functions
    )

    sgm = 0

    for key, value in endpoint_functions.items():
        dgs, ipr, opr = calculate_dgs(value, total_FP, total_CP)

        fgs, ot = calculate_fgs(value, total_O)

        # print(key, dgs, ipr, opr, total_FP, total_CP, fgs, ot, total_O)
        sgm = sgm + (dgs * fgs)

    return sgm


def calculate_dgs(function, total_FP, total_CP):

    local_vars = function.get("local_vars", {})

    # Count input parameters (IPR)
    input_params = local_vars.get("Parameter", [])
    IPR = len(input_params)

    # Count output parameters (OPR)
    output_params = local_vars.get("Return", [])
    OPR = len(output_params)

    dgs = (IPR / total_FP if total_FP > 0 else 0) + (OPR / total_CP if total_CP > 0 else 0)
    return dgs, IPR, OPR

def calculate_fgs(function, total_O):
    http_method = function["local_vars"].get("Http_method", "").lower()
    OT = fgs_operation_weights.get(http_method, 0)

    fgs = OT / total_O if total_O > 0 else 0
    return fgs, OT

def _calculate_asgm(total_sgm, total_services):
    return total_sgm / total_services if total_services > 0 else 0

'''Run command'''
lang_list = {
    'java': {'lang': 'java', 'extract': java._extract_from_dir, 'parse' : java._parse_tree_content, 'func': java._parse_function_variable},
    'py': {'lang': 'py', 'extract': py._extract_from_dir, 'parse' : py._parse_tree_content, 'func': py._parse_function_variable},
    'js': {'lang': 'js', 'extract': js._extract_from_dir, 'parse' : js._parse_tree_content, 'func': js._parse_function_variable},
    'php': {'lang': 'php', 'extract': php._extract_from_dir, 'parse' : php._parse_tree_content, 'func': php._parse_function_variable},
    'go': {'lang': 'go', 'extract': go._extract_from_dir, 'parse' : go._parse_tree_content, 'func': go._parse_function_variable}
}

fgs_operation_weights = {
    "get": 1,    # Read
    "post": 4,   # Create
    "put": 3,    # Update
    "delete": 2  # Delete
}

# lang = 'java'
# dir_path = "D://DATA//java//intellij//bravo-branch-service//src//main"
# dir_path = 'C://Users//ARD//Desktop//DeathStarBench-master//hotelReservation//services'
# dir_path = "C://Users//ARD//Desktop//robot-shop"
# dir_path = "./example/js/rs"
# dir_path = "C://Users//ARD//Desktop//andromeda//agent_management"
# tree_contents = lang_list[lang]['extract'](dir_path, lang_list[lang]['parse'], lang)
# print(tree_contents)
# variable_func = lang_list[lang]['func'](tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['global_vars'], indent=2))
# print(json.dumps(variable_func['functions'], indent=2))

# noo = calculate_noo(variable_func['functions'])
# print(noo)

# no_nanoentities = calculate_no_nanoentities(variable_func)
# print(no_nanoentities)

# loc = calculate_loc(tree_contents)
# print(loc)

# sgm = _calculate_sgm(variable_func['functions'])
# print(sgm)