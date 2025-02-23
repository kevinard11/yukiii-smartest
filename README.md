# Tesis

## Version

- 0.0.1 : parse java file, parse py file, cohesion metrix


## Setup

- install lib
```bash
pip install -r ./requirement.txt
```

- install lib ast
```bash
python ./setup-lib.py
```

## Run

- parse java file
```bash
python ./java.py
```

- parse py file
```bash
python ./py.py
```

- calculate cohesion

command/uncommand
```bash
tree_contents = java._extract_from_dir("./java/rs", java._parse_tree_content, "java")
print(tree_contents)
variable_func = java._parse_function_variable(tree_contents)
print(json.dumps(variable_func, indent=2))

tree_contents = py._extract_from_dir("./py/rs", py._parse_tree_content, "py")
print(tree_contents)
variable_func = py._parse_function_variable(tree_contents)
print(json.dumps(variable_func, indent=2))
```
then

```bash
python ./cohesion.py
```

## Examples

microservice examples used:

- robot-shop: https://github.com/instana/robot-shop




