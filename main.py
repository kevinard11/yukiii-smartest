from properties import microservices
import yaml

def main():

    # Import config
    config = import_config("C://Users//ARD//Desktop//train-ticket//smartest.yaml")

    # Create microservices
    mss = microservices.Microservices(config)
    print(mss.graph.edges())

    mss.print()
    for ms in mss.services:
        ms.print()

def import_config(filepath):
    # read yaml configuration
    config = {}
    with open(filepath, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)

    return config

if __name__ == "__main__":
    main()

