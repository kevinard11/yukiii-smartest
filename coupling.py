import re
import os
import javalang

def java_extract_service_calls(contents, base_url_dict) -> dict:
    service_calls = {}

    # Regex patterns untuk berbagai pemanggilan service
    patterns = {
        "http_calls": [
            r'\.(?:getForObject|getForEntity|postForObject|postForEntity|exchange)\(\s*["\'](http[s]?://[\w\-\.]+/[\w/\-\.]*)["\']',
            r'WebClient\.create\(\)\.(?:get|post|put|delete)\(\)\.uri\(\s*["\'](http[s]?://[\w\-\.]+/[\w/\-\.]*)["\']',
            r'@FeignClient\s*\(\s*["\']([\w\-\.]+)["\']\s*\).*?\n\s*@(?:GetMapping|PostMapping|PutMapping|DeleteMapping)\(["\'](/[\w/\-\.]*)["\']\)',
        ],
        "rabbitMQ": [
            r'\.(?:convertAndSend|channel\.basicPublish)\(\s*["\']([\w\-\.]+)["\']'
        ]
    }

    for file_path in contents:
        # Menangani HTTP-based service calls
        for pattern in patterns["http_calls"]:
            matches = re.findall(pattern, contents[file_path])
            for match in matches:
                full_url = match if isinstance(match, str) else match[0]

                # Cek apakah full_url cocok dengan salah satu base URL dalam dictionary
                matched_service = next((key for key, base_url in base_url_dict.items() if isinstance(base_url, str) and full_url.startswith(base_url)), None)

                if matched_service:  # Hanya tambahkan jika service ditemukan dalam dictionary
                    if matched_service not in service_calls:
                        service_calls[matched_service] = []
                    service_calls[matched_service].append(full_url)

        # Menangani RabbitMQ Calls
        for pattern in patterns["rabbitMQ"]:
            matches = re.findall(pattern, contents[file_path])
            for match in matches:
                exchange = match  # Nama exchange yang dipublikasikan

                # Cek apakah exchange ada dalam daftar RabbitMQ service
                if "rabbitMQ" in base_url_dict and exchange in base_url_dict["rabbitMQ"]:
                    if "rabbitMQ" not in service_calls:
                        service_calls["rabbitMQ"] = []
                    service_calls["rabbitMQ"].append(exchange)

    return service_calls

def _extract_params_from_dir(dir_path, parser, lang) -> dict:
    contents = {}
    for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                if filename.endswith(f".{lang}"):
                    file_path = os.path.join(dirpath, filename)
                    contents[file_path] = parser(file_path)
    return contents

def java_parse_content(file_path) -> any:
    with open(file_path, "r") as f:
        file_contents = f.read()

    return file_contents

# Contoh penggunaan
# directory_path = "path/to/your/java/project"
# result = extract_service_calls(directory_path)

# service_base_url = {
#     'order': 'http://ldalda/order',
#     'payment': 'http://ldalda/payment',
#     'cart': 'http://sss',
#     'rabbitMQ': ['asss', 'sdsaa']
# }
# contents = _extract_params_from_dir("./java/rs", java_parse_content, "java")
# print(contents)
# service_calls = java_extract_service_calls(contents, service_base_url)
# print(service_calls)
contents = _extract_params_from_dir("./java/test", java_parse_content, "java")
# print(contents)