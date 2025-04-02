# Tesis

## Version

- 0.0.1 : parse java file, parse py file, cohesion metric
- 0.0.2 : parse all file, cohesion metric (LCOM5), main program
- 0.0.3 : coupling metric (AIS) for java
- 0.0.4 : all coupling metric
- 0.0.5 : all granularity metric
- 0.0.6 : all complexity metric
- 0.0.7 : reorganize file and folder

## Setup

- install lib

```bash
pip install -r ./requirements.txt
```

- install lib ast (tree-sitter)

```bash
python ./setup-lib.py
```
## Config
Create config file in the source repository that want to be analyze. Description will be given in the next version.

## Run

- calculate metric

--repo = repo url used for calculate
```bash
python ./main.py --repo="yourgiturl"
```

## Examples

microservice examples used:

- robot-shop: https://github.com/instana/robot-shop
