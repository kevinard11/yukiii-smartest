# Tesis

## Version

- 0.0.1 : parse java file, parse py file, cohesion metrix
- 0.0.2 -> parse all file, cohesion metrix (LCOM5), main program

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

create microservice manually (command/uncommand)

```bash
mss.create_microservice('payment', 'go', ["C://Users//ARD//Desktop//DeathStarBench-master//hotelReservation//services"])
mss.create_microservice('dispatch','py')
mss.create_microservice('cart', 'java')
mss.create_microservice('shipment', 'php', ["C://Users//ARD//Desktop//robot-shop"])
mss.create_microservice('user', 'js', ["C://Users//ARD//Desktop//robot-shop"])
```

then

```bash
python ./main.py
```

## Examples

microservice examples used:

- robot-shop: https://github.com/instana/robot-shop
