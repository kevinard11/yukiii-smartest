# Tesis

## Version

- 0.0.1 : parse all file
- 0.0.2 : cohesion metric
- 0.0.3 : coupling metric
- 0.0.4 : all granularity metric
- 0.0.5 : all complexity metric
- 0.0.6 : main program
- 0.0.7 : reorganize file and folder
- 0.0.8 : endpoint

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
