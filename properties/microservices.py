from properties import cohesion, coupling, granularity, complexity, service
import networkx as nx

class Microservices():
    def __init__(self, config):
        self.name = config['name']
        self.dir_path = config['root-dir']
        self.services = []
        self.service_base_url = {}
        self.service_queue_key = {}
        self.metric = {
            'Cohesion':{}, 'Coupling':{}, 'Complexity':{}, 'Granularity':{}
        }

        # Create each service
        self.create_services(config)

    def create_services(self, config):

        for service_key in config['services']:

            service = config['services'][service_key]
            if 'dir' in service:
                dir = self.dir_path+service['dir']

            if 'lang' in service:
                lang = service['lang']

            self.create_service(service_key, lang, [dir])

            if 'base-url' in service:
                base_url = service['base-url']
                self.set_service_base_url(service_key, base_url)

            if 'queue-key' in service:
                queue_key = service['queue-key']
                self.set_service_queue_key(service_key, queue_key)

        self.get_called_services()

        # Calculate defined metric
        self.calculate_metric()

    def set_services(self, service):
        self.services.append(service)

    def set_service_base_url(self, service_name, base_url):
        self.service_base_url[service_name] = base_url

    def set_service_queue_key(self, service_name, queue_key):
        self.service_queue_key[service_name] = queue_key

    def calculate_metric(self):
        self.calculate_alcom() #ALCOM
        self.calculate_alcom4() #Average LCOM4
        self.calculate_alcom5() #Average LCOM5
        self.calculate_adcs() #ADCS
        self.calculate_scf() #SCF
        self.calculate_aacs() #Average ACS
        self.calculate_average_noo() #Average NOO
        self.calculate_average_no_nanoentities() #Average NO nanoentities
        self.calculate_average_loc() # Average LOC
        self.calculate_asgm() #ASGM
        self.calculate_tcm() #TCM
        self.calculate_average_hm() #Average Halstead's metric (Difficulty)
        self.calculate_average_cc() #Average CC
        self.calculate_average_icc() #Average ICC

    def calculate_alcom(self):
        self.metric['Cohesion']['ALCOM']= cohesion._calculate_alcom(sum([ms.cohesion['LCOM'] for ms in self.services]), len(self.services))

    def calculate_alcom4(self):
        self.metric['Cohesion']['Average LCOM4'] = cohesion._calculate_avg_lcom4(sum([ms.cohesion['LCOM4'] for ms in self.services]), len(self.services))

    def calculate_alcom5(self):
        self.metric['Cohesion']['Average LCOM5'] = cohesion._calculate_avg_lcom5(sum([ms.cohesion['LCOM5'] for ms in self.services]), len(self.services))

    def calculate_adcs(self):
        self.metric['Coupling']['ADCS'] = coupling.calculate_adcs(sum([ms.coupling['ADS'] for ms in self.services]), len(self.services))

    def calculate_scf(self):
        self.metric['Coupling']['SCF'] = coupling.calculate_scf(sum([ms.coupling['ADS'] for ms in self.services]), len(self.services))

    def calculate_aacs(self):
        self.metric['Coupling']['Average ACS'] = coupling.calculate_aacs(sum([ms.coupling['ACS'] * ms.coupling['AIS'] for ms in self.services]), len(self.services))

    def calculate_average_noo(self):
        self.metric['Granularity']['Average NOO'] = granularity._calculate_average_noo(sum([ms.granularity['NOO'] for ms in self.services]), len(self.services))

    def calculate_average_no_nanoentities(self):
        self.metric['Granularity']['Average NO nanoentities'] = granularity._calculate_average_no_nanoentities(sum([ms.granularity['NO nanoentities'] for ms in self.services]), len(self.services))

    def calculate_average_loc(self):
        self.metric['Granularity']['Average LOC'] = granularity._calculate_average_loc(sum([ms.granularity['LOC'] for ms in self.services]), len(self.services))

    def calculate_asgm(self):
        self.metric['Granularity']['Average SGM'] = granularity._calculate_asgm(sum([ms.granularity['SGM'] for ms in self.services]), len(self.services))

    def calculate_tcm(self):
        self.metric['Complexity']['TCM'] = sum([(ms.complexity['TCM'] if 'TCM' in ms.complexity else 0) * (ms.complexity['ComF'] if 'ComF' in ms.complexity else 0) for ms in self.services])

    def calculate_average_hm(self):
        self.metric['Complexity']["Average Halstead's metric (Difficulty)"] = complexity._calculate_average_agg_hm(sum([ms.complexity['HM'] if 'HM' in ms.complexity else 0 for ms in self.services]), len(self.services))

    def calculate_average_cc(self):
        self.metric['Complexity']['Average CC'] = complexity._calculate_avg_ccs_services(sum([ms.complexity['CC'] for ms in self.services]), len(self.services))

    def calculate_average_icc(self):
        self.metric['Complexity']['Average ICC'] = complexity._calculate_avg_ccs_services(sum([ms.complexity['ICC'] for ms in self.services]), len(self.services))

    def print_metric(self):
        for key, aspect in self.metric.items():
            for metric, value in aspect.items():
                print(f"Metric {key}, {metric}: {value}")

    def print(self):
        print(f"Microservice Name: {self.name}")
        self.print_metric()
        print()

    def create_service(self, name, lang, dir_path=[]):
        if len(dir_path) == 0:
            dir_path = [self.dir_path]

        ms = service.Service(name, lang, dir_path)
        self.set_services(ms)

    def print_service(self):
        for service in self.services:
            service.print()

    def get_called_services(self):
        for ms in self.services:
            ms.get_called_service(self.service_base_url, self.service_queue_key)
            ms.set_ads()

        G = nx.DiGraph()
        for ms in self.services:
            ais = 0
            for ms1 in self.services:
                if ms.name != ms1.name and ms.name in ms1.called_service.keys():
                    G.add_edge(ms1.name, ms.name)
                    ais = ais + 1
            ms.set_ais(ais)
            ms.set_coupling_metric()

        self.graph = G
        for ms in self.services:
            for node, connected_nodes in complexity.get_indirect_coupling(self.graph).items():
                if ms.name == node :
                    ms.set_indirect_coupling(connected_nodes)
            ms.set_complexity_metric()