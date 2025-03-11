import java, py, js, php, go

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
                    baseurl = format_baseurl(baseurl)

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
                    # baseurl = baseurl.replace('"', '').replace('"', '')
                    baseurl = format_baseurl(baseurl)
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

def get_all_MQ_client_function(functions, global_vars):
    MQ_funcs = {}
    for key, function in functions.items():
        if function:
            for func in function['called_methods']:
                if func['method'] in MQ_framework.keys():
                    if len(func['arguments']) in MQ_framework[func['method']] and (func['qualifier'] and 'template' in func['qualifier'].lower()):
                        MQ_funcs[key] = function
                    elif len(func['arguments']) in MQ_framework[func['method']]:
                        MQ_funcs[key] = function

    for key, global_var in global_vars.items():
        global_var_func_MQ = []
        if global_var and key.endswith('.called_methods'):
            for func in global_var:
                if func['method'] in MQ_framework.keys():
                    if MQ_framework[func['method']] == len(func['arguments']):
                        global_var_func_MQ.append(func)
            MQ_funcs[key] = {
                'called_methods': global_var_func_MQ
            }

    # print(MQ_funcs)
    return MQ_funcs

def get_MQ_called_service(MQ_funcs, called_method, global_vars, called_services, service_queue_topic_routing, local_vars, nearest_key):
    method_name = called_method['method']
    method_args = called_method['arguments']
    method_qua = called_method['qualifier']
    # print('a', method_name, method_args)

    found = False

    for MQ_key, MQ_func in MQ_funcs.items():
        for MQ_fun in MQ_func['called_methods']:
            if MQ_fun['method'] in MQ_framework.keys():
                # print(method_name, MQ_fun['method'], len(MQ_func['local_vars']['Parameter']), len(method_args))
                if method_name in MQ_key.split('.') and ('local_vars'in MQ_func and 'Parameter' in MQ_func['local_vars'] and len(MQ_func['local_vars']['Parameter']) == len(method_args)):
                    # print('asdasd', method_name, MQ_fun['method'], MQ_fun['arguments'])
                    for arg in method_args:
                        if arg and isinstance(arg, str) and (arg.startswith('"') or arg.startswith("'")) and (arg.endswith('"') or arg.endswith("'")):

                            arg = arg.replace('"', '').replace("'", '')
                            if any(arg in values for values in service_queue_topic_routing.values()):
                                called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, arg)
                                for called_service in called_queue:
                                    if called_service in called_services.keys():
                                        called_services[called_service].append(arg)
                                        found = True
                                    elif called_service != None:
                                        called_services[called_service] = []
                                        called_services[called_service].append(arg)
                                        found = True
                                # print(called_services)
                                # break
                        elif arg and isinstance(arg, dict):
                            for key, value in arg.items():
                                if value and isinstance(value, str) and (value.startswith('"') or value.startswith("'")) and (value.endswith('"') or value.endswith("'")):
                                    value = value.replace('"', '').replace("'", '')
                                    if any(value in values for values in service_queue_topic_routing.values()):
                                        called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, value)
                                        for called_service in called_queue:
                                            if called_service in called_services.keys():
                                                called_services[called_service].append(value)
                                                found = True
                                            elif called_service != None:
                                                called_services[called_service] = []
                                                called_services[called_service].append(value)
                                                found = True
                                        # print(called_services)
                                        # break
                                else: # reference in local or global variable
                                    if value and isinstance(value, str):
                                        value = value.replace('"', '').replace('${', '').replace('}', '').replace("'",'')
                                        baseurl = find_in_local_global_vars(global_vars, local_vars, value, nearest_key)
                                        if baseurl:
                                            baseurl = format_baseurl(baseurl)
                                            if any(baseurl in values for values in service_queue_topic_routing.values()):
                                                called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, baseurl)
                                                for called_service in called_queue:
                                                    if called_service in called_services.keys():
                                                        called_services[called_service].append(baseurl)
                                                        found = True
                                                    elif called_service != None:
                                                        called_services[called_service] = []
                                                        called_services[called_service].append(baseurl)
                                                        found = True
                                                # print(called_services)
                                                # break
                        else: # reference in local or global variable
                            if arg and isinstance(arg, str):
                                arg = arg.replace('"', '').replace('${', '').replace('}', '').replace("'", '')
                                baseurl = find_in_local_global_vars(global_vars, local_vars, arg, nearest_key)
                                if baseurl:
                                    baseurl = format_baseurl(baseurl)
                                    if any(baseurl in values for values in service_queue_topic_routing.values()):
                                        called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, baseurl)
                                        for called_service in called_queue:
                                            if called_service in called_services.keys():
                                                called_services[called_service].append(baseurl)
                                                found = True
                                            elif called_service != None:
                                                called_services[called_service] = []
                                                called_services[called_service].append(baseurl)
                                                found = True
                                        # print(called_services)
                                        # break

                elif MQ_key.endswith('.called_methods') and method_name == MQ_fun['method'] and (len(MQ_fun['arguments']) == len(method_args)):
                    for arg in method_args:
                        if arg and isinstance(arg, str) and (arg.startswith('"') or arg.startswith("'")) and (arg.endswith('"') or arg.endswith("'")):
                            arg = arg.replace('"', '').replace("'", '')
                            if any(arg in values for values in service_queue_topic_routing.values()):
                                called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, arg)
                                for called_service in called_queue:
                                    if called_service in called_services.keys():
                                        called_services[called_service].append(arg)
                                        found = True
                                    elif called_service != None:
                                        called_services[called_service] = []
                                        called_services[called_service].append(arg)
                                        found = True
                                # print(called_services)
                                # break
                        elif arg and isinstance(arg, dict):
                            for key, value in arg.items():
                                if value and isinstance(value, str) and (value.startswith('"') or value.startswith("'")) and (value.endswith('"') or value.endswith("'")):
                                    value = value.replace('"', '').replace("'", '')
                                    if any(value in values for values in service_queue_topic_routing.values()):
                                        called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, value)
                                        for called_service in called_queue:
                                            if called_service in called_services.keys():
                                                called_services[called_service].append(value)
                                                found = True
                                            elif called_service != None:
                                                called_services[called_service] = []
                                                called_services[called_service].append(value)
                                                found = True
                                        # print(called_services)
                                        # break
                                else: # reference in local or global variable
                                    if value and isinstance(value, str):
                                        value = value.replace('"', '').replace('${', '').replace('}', '').replace("'", '')
                                        baseurl = find_in_local_global_vars(global_vars, local_vars, value, nearest_key)
                                        if baseurl:
                                            baseurl = format_baseurl(baseurl)
                                            if any(baseurl in values for values in service_queue_topic_routing.values()):
                                                called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, baseurl)
                                                for called_service in called_queue:
                                                    if called_service in called_services.keys():
                                                        called_services[called_service].append(baseurl)
                                                        found = True
                                                    elif called_service != None:
                                                        called_services[called_service] = []
                                                        called_services[called_service].append(baseurl)
                                                        found = True
                                                # print(called_services)
                                                # break
                        else: # reference in local or global variable
                            if arg and isinstance(arg, str):
                                arg = arg.replace('"', '').replace('${', '').replace('}', '').replace("'")
                                baseurl = find_in_local_global_vars(global_vars, local_vars, arg, nearest_key)
                                if baseurl:
                                    baseurl = format_baseurl(baseurl)
                                    if any(baseurl in values for values in service_queue_topic_routing.values()):
                                        called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, baseurl)
                                        for called_service in called_queue:
                                            if called_service in called_services.keys():
                                                called_services[called_service].append(baseurl)
                                                found = True
                                            elif called_service != None:
                                                called_services[called_service] = []
                                                called_services[called_service].append(baseurl)
                                                found = True
                                        # print(called_services)
                                        # break
            if found:
                break

    # print(method_name, found)
    if not found:
        if method_name in MQ_framework.keys() and len(method_args) in MQ_framework[method_name]:
            # print(method_name)
            for arg in method_args:
                if arg and isinstance(arg, str) and (arg.startswith('"') or arg.startswith("'")) and (arg.endswith('"') or arg.endswith("'")):
                    arg = arg.replace('"', '').replace("'", '')
                    if any(arg in values for values in service_queue_topic_routing.values()):
                        called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, arg)
                        for called_service in called_queue:
                            if called_service in called_services.keys():
                                called_services[called_service].append(arg)
                                found = True
                            elif called_service != None:
                                called_services[called_service] = []
                                called_services[called_service].append(arg)
                                found = True
                        # print(called_services)
                        break
                elif arg and isinstance(arg, dict):
                    for key, value in arg.items():
                        if value and isinstance(value, str) and (value.startswith('"') or value.startswith("'")) and (value.endswith('"') or value.endswith("'")):
                            value = value.replace('"', '').replace("'", '')
                            if any(value in values for values in service_queue_topic_routing.values()):
                                called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, value)
                                for called_service in called_queue:
                                    if called_service in called_services.keys():
                                        called_services[called_service].append(value)
                                        found = True
                                    elif called_service != None:
                                        called_services[called_service] = []
                                        called_services[called_service].append(value)
                                        found = True
                                # print(called_services)
                                break
                        else: # reference in local or global variable
                            if value and isinstance(value, str):
                                value = value.replace('"', '').replace('${', '').replace('}', '').replace("'", '')
                                baseurl = find_in_local_global_vars(global_vars, local_vars, value, nearest_key)
                                if baseurl:
                                    baseurl = format_baseurl(baseurl)
                                    if any(baseurl in values for values in service_queue_topic_routing.values()):
                                        called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, baseurl)
                                        for called_service in called_queue:
                                            if called_service in called_services.keys():
                                                called_services[called_service].append(baseurl)
                                                found = True
                                            elif called_service != None:
                                                called_services[called_service] = []
                                                called_services[called_service].append(baseurl)
                                                found = True
                                        # print(called_services)
                                        break
                else: # reference in local or global variable
                    if arg and isinstance(arg, str):
                        arg = arg.replace('"', '').replace('${', '').replace('}', '').replace("'", '')
                        baseurl = find_in_local_global_vars(global_vars, local_vars, arg, nearest_key)
                        if baseurl:
                            baseurl = format_baseurl(baseurl)
                            if any(baseurl in values for values in service_queue_topic_routing.values()):
                                called_queue = find_in_service_queue_topic_routing(service_queue_topic_routing, baseurl)
                                for called_service in called_queue:
                                    if called_service in called_services.keys():
                                        called_services[called_service].append(baseurl)
                                        found = True
                                    elif called_service != None:
                                        called_services[called_service] = []
                                        called_services[called_service].append(baseurl)
                                        found = True
                                # print(called_services)
                                break
    # print(method_name, method_args, found)
    # print(called_services)

def format_baseurl(baseurl):
    if isinstance(baseurl, str):
        if baseurl.startswith('"') or baseurl.startswith("'"):
            baseurl = baseurl[1:]

        if baseurl.endswith('"') or baseurl.endswith("'"):
            baseurl = baseurl[:-1]
    return baseurl

def get_called_service(variable_func, service_base_url, service_queue_topic_routing):

    global_vars = variable_func["global_vars"]
    functions = variable_func["functions"]
    called_services = {}

    # Java
    feign_funcs = get_all_feign_client_function(functions)
    MQ_funcs = get_all_MQ_client_function(functions, global_vars)

    for key, function in functions.items():
        nearest_key = '.'.join(key.split('.')[:-1])
        local_vars = function['local_vars']
        for called_method in function['called_methods']:
            find_called_service(called_services, global_vars, local_vars, called_method, service_base_url, service_queue_topic_routing, feign_funcs, MQ_funcs, nearest_key)

    for key, function in global_vars.items(): # called outside function (possible in python, go)
        nearest_key = '.'.join(key.split('.')[:-1])
        local_vars = {}
        if key.split('.')[-1] == 'called_methods' :
            for called_method in function:
                find_called_service(called_services, global_vars, local_vars, called_method, service_base_url, service_queue_topic_routing,feign_funcs, MQ_funcs, nearest_key)
        elif isinstance(function, dict) and 'method' in function and 'arguments' in function:
            find_called_service(called_services, global_vars, local_vars, function, service_base_url, service_queue_topic_routing, feign_funcs, MQ_funcs, nearest_key)

    return called_services

def find_called_service(called_services, global_vars, local_vars, called_method, service_base_url, service_queue_topic_routing, feign_funcs, MQ_funcs, nearest_key):
    method_name = called_method['method']
    method_args = called_method['arguments']
    method_qua = called_method['qualifier']

    for arg in method_args:
        if arg and isinstance(arg, str):
            # print(arg, (arg.startswith('"') or arg.endswith("'")) )
            if (arg.startswith('"') or arg.startswith("'")) and (arg.endswith('"') or arg.endswith("'")) and (any(arg.replace('"','') in values for values in service_queue_topic_routing.values()) or any(arg.replace("'",'') in values for values in service_queue_topic_routing.values()) or arg.replace('"', '').startswith(('http://', 'https://')) or arg.replace("'", '').startswith(('http://', 'https://'))): # string
                # print(arg)
                baseurl = arg.replace('"', '').replace('${', '').replace('}', '').replace("'",'')
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
    get_MQ_called_service(MQ_funcs, called_method, global_vars, called_services, service_queue_topic_routing, local_vars, nearest_key)

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
    for key, values in service_base_url.items():
        for value in values:
            if value_var.lower() == value.lower() or value.lower() in value_var.lower():
                return key

    if value_var and value_var.replace('"', '').startswith(('http://', 'https://')):
        return 'others'

def find_in_service_queue_topic_routing(service_queue_topic_routing, value_var):
    called_queue = []
    for key, values in service_queue_topic_routing.items():
        for value in values:
            if value_var == value:
                called_queue.append(key)

    return called_queue if called_queue else ['others']

def calculate_adcs(ads, total_microservice):

    return ads / total_microservice if total_microservice > 0 else 0

def calculate_scf(ads, total_microservice):
    max_conn = (total_microservice**2) - total_microservice
    # print(max_conn, total_microservice)
    return ads / max_conn if max_conn > 0 else 0

def calculate_ads(name, called_services):
    called_services_per_service = get_called_services_per_service(called_services)

    # return sum(v for k,v in called_services_per_service if k != name and k != 'others') # 1 call count 1

    return sum(1 for k in called_services_per_service if k != name and k != 'others') # all call in 1 service count 1

def get_called_services_per_service(called_services):
    return {k: len(v) for k,v in called_services.items()}

def _calculate_acs(ads, ais):
    return ads * ais

def calculate_aacs(total_acs, total_services):
    # print(total_acs, total_services)
    return total_acs/total_services if total_services > 0 else 0


## ------------------------------------------------------------------- ##
'''Run command'''
lang_list = {
    'java': {'lang': 'java', 'extract': java._extract_from_dir, 'parse' : java._parse_tree_content, 'func': java._parse_function_variable},
    'py': {'lang': 'py', 'extract': py._extract_from_dir, 'parse' : py._parse_tree_content, 'func': py._parse_function_variable},
    'js': {'lang': 'js', 'extract': js._extract_from_dir, 'parse' : js._parse_tree_content, 'func': js._parse_function_variable},
    'php': {'lang': 'php', 'extract': php._extract_from_dir, 'parse' : php._parse_tree_content, 'func': php._parse_function_variable},
    'go': {'lang': 'go', 'extract': go._extract_from_dir, 'parse' : go._parse_tree_content, 'func': go._parse_function_variable}
}

lang = 'py'
# dir_path = "D://DATA//java//intellij//bravo-branch-service//src//main"
# dir_path = 'C://Users//ARD//Desktop//DeathStarBench-master//hotelReservation//services'
# dir_path = "C://Users//ARD//Desktop//robot-shop"
dir_path = "./py/rs"
tree_contents = lang_list[lang]['extract'](dir_path, lang_list[lang]['parse'], lang)
# print(tree_contents)
variable_func = lang_list[lang]['func'](tree_contents)
# print(json.dumps(variable_func, indent=2))
# print(json.dumps(variable_func['global_vars'], indent=2))
# print(json.dumps(variable_func['functions'], indent=2))

# service_base_url = {
#     'warriors': ['https://gateway-gc.bfi.co.id/bfibravo/cloud/agency_api/api'],
#     'confins': ['https://gateway-gc.bfi.co.id'],
#     'master': ['https://microservices.dev.bravo.bfi.co.id/master'],
#     'user': ['http://user:8080/', 'http://user:8081/'],
#     'cart': ['http://CART:8080/']
# }

# service_queue_topic_routing = {
#     'master': ['master_queue', 'ssssss'],
#     'agent': ['agent_queue'],
#     'order': ['orders']
# }

api_call_framework = {
    "getForObject", "getForEntity", "postForObject", "postForEntity", "put", "delete", "exchange", # Java
    "requests.get", "httpx.get", # Py
    "file_get_contents", "request", "curl_init", "Request.get", # Php
    "fetch", "axios.get", "got", # Js
    "http.Get", "http.Post", "http.Put" # Go
}

MQ_framework = {
    "convertAndSend" : [2], # Java rabbitMQ
    "send": [2,3], # Java Kafka
    "basic_publish": [3, 4], # 4 Py rabbitMQ (pika)
    "publish": [2], # Py rabbitMQ (aiopika)
    "produce": [3,4], # Py kafka (confluence-kafka)
    "send_and_wait": [2], # Py kafka (aiokafka)
    # "send": 2, # Py kafka (kafka-python)
    "queue_declare": [5], # Php rabbitMQ (php-amqplib)
    "createQueue": [1], # Php rabbitMQ (enqueue-amqlib)
    "set": [2], "newTopic": [1], # Php kafka (php-rdkafka)
    "sendToQueue": [2], # Js rabbitMQ (amqlib)
    # "send": 2, # Js kafka (kafkajs)
    "QueueDeclare": [6], # Go rabbitMQ (streadway/amqp)
    "NewWriter": [1], # Go kafka (kafka-go)

}

# feign_function = get_all_feign_client_function(variable_func['functions'])
# print(feign_function)
# feign_global_vars = get_all_feign_client_global_vars(variable_func['global_vars'])
# print(feign_global_vars)
# rabbitMQ_function = get_all_rabbitMQ_client_function(variable_func['functions'])
# print(rabbitMQ_function)
# called_services = get_called_service(variable_func, service_base_url, service_queue_topic_routing)
# print(called_services)

