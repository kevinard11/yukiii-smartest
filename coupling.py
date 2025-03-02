import re
import os
import java, py, js, php, go
import json

def get_all_feign_client_function(functions):
    feign_funcs = {}
    for key, function in functions.items():
        if '@FeignClient' in key.split('.'):
            feign_funcs[key] = function

    return feign_funcs

def get_all_feign_client_global_vars(global_vars):
    feign_global_var = {}
    for key, value in global_vars.items():
        if '@FeignClient' in key.split('.'):
            feign_global_var[key] = value

    return feign_global_var

def get_feign_called_service(feign_funcs, called_method, global_vars, called_services, service_base_url):
    # feign_var = get_all_feign_client_global_vars(global_vars)
    method_name = called_method['method']
    method_args = called_method['arguments']
    method_qua = called_method['qualifier']

    for feign_key, feign_func in feign_funcs.items():
        # print(feign_func['local_vars'])
        if method_name in feign_key.split('.') and ('Parameter' in feign_func['local_vars'] and len(feign_func['local_vars']['Parameter']) == len(method_args)):
            if method_qua.lower() in feign_key.lower().split('.') or method_name in [k.split('.')[-1] for k in feign_funcs.keys()]:
                baseurl = global_vars['.'.join(feign_key.split('.')[:-1]) + '.baseurl']
                if baseurl.startswith('"${') and baseurl.endswith('}"'):
                    baseurl = baseurl.replace('"${', '').replace('}"', '')
                    baseurl = find_in_global_vars(global_vars, baseurl)

                    if baseurl in service_base_url.values():
                        called_service = find_in_service_base_url(service_base_url, baseurl)
                        # print(baseurl, called_service, called_service in called_services)
                        if called_service in called_services.keys():
                            called_services[called_service].append(baseurl)
                        elif called_service != None:
                            called_services[called_service] = []
                            called_services[called_service].append(baseurl)
                        # print(called_services)
                        break

                elif baseurl.startswith('"') and baseurl.endswith('"'):
                    baseurl = baseurl.replace('"', '').replace('"', '')
                    if baseurl in service_base_url.values():
                        called_service = find_in_service_base_url(service_base_url, baseurl)
                        # print(baseurl, called_service, called_service in called_services)
                        if called_service in called_services.keys():
                            called_services[called_service].append(baseurl)
                        elif called_service != None:
                            called_services[called_service] = []
                            called_services[called_service].append(baseurl)
                        # print(called_services)
                        break

def get_all_MQ_client_function(functions):
    MQ_funcs = {}
    for key, function in functions.items():
        if function:
            for func in function['called_methods']:
                if func['method'] in MQ_framework.keys():
                    if MQ_framework[func['method']] == len(func['arguments']) and 'template' in func['qualifier'].lower():
                        MQ_funcs[key] = function

    return MQ_funcs

def get_MQ_called_service(MQ_funcs, called_method, global_vars, called_services, service_queue, local_vars, nearest_key):
    method_name = called_method['method']
    method_args = called_method['arguments']
    method_qua = called_method['qualifier']

    for MQ_key, MQ_func in MQ_funcs.items():
        for MQ_fun in MQ_func['called_methods']:
            if MQ_fun['method'] in MQ_framework.keys():
                if method_name in MQ_key.split('.') and ('Parameter' in MQ_func['local_vars'] and len(MQ_func['local_vars']['Parameter']) == len(method_args)):
                    for arg in method_args:
                        if arg and isinstance(arg, str) and arg.startswith('"') and arg.endswith('"') :
                            arg = arg.replace('"', '').replace('"', '')
                            if any(arg in values for values in service_queue.values()):
                                called_queue = find_in_service_queue(service_queue, arg)
                                for called_service in called_queue:
                                    if called_service in called_services.keys():
                                        called_services[called_service].append(arg)
                                    elif called_service != None:
                                        called_services[called_service] = []
                                        called_services[called_service].append(arg)
                                # print(called_services)
                                break
                        else: # reference in local or global variable
                            arg = arg.replace('"', '').replace('${', '').replace('}', '')
                            baseurl = find_in_local_global_vars(global_vars, local_vars, arg, nearest_key)
                            if baseurl:
                                if any(baseurl in values for values in service_queue.values()):
                                    called_queue = find_in_service_queue(service_queue, baseurl)
                                    for called_service in called_queue:
                                        if called_service in called_services.keys():
                                            called_services[called_service].append(baseurl)
                                        elif called_service != None:
                                            called_services[called_service] = []
                                            called_services[called_service].append(baseurl)
                                    # print(called_services)
                                    break

def get_called_service(global_vars, functions, service_base_url, service_queue):
    called_services = {}

    # Java
    feign_funcs = get_all_feign_client_function(functions)
    MQ_funcs = get_all_MQ_client_function(functions)

    for key, function in functions.items():
        nearest_key = '.'.join(key.split('.')[:-1])
        local_vars = function['local_vars']
        for called_method in function['called_methods']:
            # print(called_method['method'], called_method['arguments'], called_method['qualifier'])

            # if ('qualifier' in called_method and called_method['qualifier']):
            method_name = called_method['method']
            method_args = called_method['arguments']
            method_qua = called_method['qualifier']

            for arg in method_args:
                if arg and isinstance(arg, str):

                    if arg.startswith('"') and arg.endswith('"') and (arg.replace('"','') in service_base_url or arg.replace('"', '').startswith(('http://', 'https://'))): # string
                        baseurl = arg.replace('"', '').replace('${', '').replace('}', '')
                        if baseurl:
                            called_service = find_in_service_base_url(service_base_url, baseurl)
                            # print(baseurl, called_service, called_service in called_services)
                            if called_service in called_services.keys():
                                called_services[called_service].append(baseurl)
                            elif called_service != None:
                                called_services[called_service] = []
                                called_services[called_service].append(baseurl)
                            # print(called_services)
                            break

                    else: # reference in local or global variable
                        arg = arg.replace('"', '').replace('${', '').replace('}', '')
                        baseurl = find_in_local_global_vars(global_vars, local_vars, arg, nearest_key)
                        # print(baseurl, arg)
                        if baseurl:
                            called_service = find_in_service_base_url(service_base_url, baseurl)
                            # print(baseurl, called_service, called_service in called_services)
                            if called_service in called_services.keys():
                                # print(called_services)
                                called_services[called_service].append(baseurl)
                            elif called_service != None:
                                called_services[called_service] = []
                                called_services[called_service].append(baseurl)
                            # print(called_services)
                            break

            # Java
            # Feign Client
            get_feign_called_service(feign_funcs, called_method, global_vars, called_services, service_base_url)
            get_MQ_called_service(MQ_funcs, called_method, global_vars, called_services, service_queue, local_vars, nearest_key)

    return called_services

def find_in_local_global_vars(global_vars, local_vars, key, nearest_key):
    try:
        if key in local_vars and local_vars[key]: # find in local variable
            if isinstance(local_vars[key], str):
                local_key = local_vars[key].replace('"', '').replace('${', '').replace('}', '')
                if (local_key in local_vars and local_vars[local_key]) or find_in_global_vars(global_vars, local_key):
                    return find_in_local_global_vars(global_vars, local_vars, local_key, nearest_key)
                else:
                    return local_key
        else: # find in global variable
            if find_in_global_vars(global_vars, f"{nearest_key}.{key}"):
                use_key = f"{nearest_key}.{key}"
            else :
                use_key = key

            local_key = find_in_global_vars(global_vars, use_key)
            if isinstance(local_key, str):
                local_key = local_key.replace('"', '').replace('${', '').replace('}', '') if local_key else None
                if find_in_global_vars(global_vars, local_key):
                    return find_in_local_global_vars(global_vars, local_vars, local_key, nearest_key)
                else:
                    return local_key
    except Exception:
        return None

def find_in_global_vars(global_vars, key_var):
    for key, value in global_vars.items():
        if key_var and key.endswith(key_var):
            return value

def find_in_service_base_url(service_base_url, value_var):
    for key, value in service_base_url.items():
        if value_var == value:
            return key

    if value_var and value_var.replace('"', '').startswith(('http://', 'https://')):
        return 'others'

def find_in_service_queue(service_queue, value_var):
    called_queue = []
    for key, values in service_queue.items():
        for value in values:
            if value_var == value:
                called_queue.append(key)

    return called_queue if called_queue else ['others']

## ------------------------------------------------------------------- ##
'''Run command'''
lang_list = {
    'java': {'lang': 'java', 'extract': java._extract_from_dir, 'parse' : java._parse_tree_content, 'func': java._parse_function_variable},
    'py': {'lang': 'py', 'extract': py._extract_from_dir, 'parse' : py._parse_tree_content, 'func': py._parse_function_variable},
    'js': {'lang': 'js', 'extract': js._extract_from_dir, 'parse' : js._parse_tree_content, 'func': js._parse_function_variable},
    'php': {'lang': 'php', 'extract': php._extract_from_dir, 'parse' : php._parse_tree_content, 'func': php._parse_function_variable},
    'go': {'lang': 'go', 'extract': go._extract_from_dir, 'parse' : go._parse_tree_content, 'func': go._parse_function_variable}
}

lang = 'java'
# dir_path = "D://DATA//java//intellij//bravo-agent-service//src//main"
# dir_path = 'C://Users//ARD//Desktop//DeathStarBench-master//hotelReservation//services'
# dir_path = "C://Users//ARD//Desktop//robot-shop"
dir_path = "./java/test"
tree_contents = lang_list[lang]['extract'](dir_path, lang_list[lang]['parse'], lang)
# print(tree_contents)
variable_func = lang_list[lang]['func'](tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['global_vars'], indent=2))
# print(json.dumps(variable_func['functions'], indent=2))

service_base_url = {
    'warriors': 'https://gateway-gc.bfi.co.id/bfibravo/cloud/agency_api/api',
    'confins': 'https://gateway-gc.bfi.co.id',
    'master': 'https://microservices.dev.bravo.bfi.co.id/master',
}

service_queue = {
    'master': ['agent_queue', 'ssssss'],
    'agent': ['agent_queue'],
}

api_call_framework = {
    "getForObject", "getForEntity", "postForObject", "postForEntity", "put", "delete", "exchange", # Java RestTemplate
}

MQ_framework = {
    "convertAndSend" : 2, # Java rabbitMQ
    "send": 2, # Java Kafka
}

# feign_function = get_all_feign_client_function(variable_func['functions'])
# print(feign_function)
# feign_global_vars = get_all_feign_client_global_vars(variable_func['global_vars'])
# print(feign_global_vars)
# rabbitMQ_function = get_all_rabbitMQ_client_function(variable_func['functions'])
# print(rabbitMQ_function)
called_services = get_called_service(variable_func['global_vars'], variable_func['functions'], service_base_url, service_queue)
print(called_services)

