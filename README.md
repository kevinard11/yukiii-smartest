# Tesis
## Version

- 0.0.1 : parse all file
- 0.0.2 : cohesion metric
- 0.0.3 : coupling metric
- 0.0.4 : all granularity metric
- 0.0.5 : all complexity metric
- 0.0.6 : main program
- 0.0.7 : endpoint
- 0.0.8 : reorganize file and folder
- 0.0.9 : dashboard, database
- 0.1.0 : dockerization

# Smartest
## Config

Create config file in the source repository that want to be analyze. Description will be given in the next version.

## Run via docker
```bash
docker-compose up --build
```


## Run via command
```bash
cd smartest
```

### Setup Lib
- install lib

```bash
pip install -r ./requirements.txt
```

- install lib ast (tree-sitter)

```bash
python ./setup-lib.py
```

### Run smartest via main
Setup mongo in local and edit user and password for mongo in mongo_db.py

--repo = repo url used for calculate

```bash
python ./main.py --repo="yourgiturl"
```

### Run smartest via app

- run app
```bash
cd smartest
python ./app.py
```

- run dashboard
```bash
cd dashboard
```
open index.html

## Examples

microservice examples used:

- robot-shop: https://github.com/instana/robot-shop
