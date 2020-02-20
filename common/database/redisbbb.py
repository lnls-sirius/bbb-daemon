from time import sleep
import redis
import sys

REDIS_JSON_KEY = 'JSON_FILE'
REDIS_NODE_CONTROLLER_KEY = 'NODE_CONTROLLER'
REDIS_MASTER_IP_KEY = "MASTER_IP"
REDIS_SLAVE_IP_KEY = "SLAVE_IP"

NODE_CONTROLLERS = ["MASTER", "SLAVE"]

class RedisDatabase:
    def __init__(self, host, port=6379):
        self.host = host
        self.port = port
        self.db = redis.StrictRedis(host=host, port=port)


    def is_available(self, retries = 3, delay = 10):
        for _i in range(retries):
            try:
                sys.stdout.write("({} out of {}). Verify if server is avalable...\n".format(_i+1, retries))
                sys.stdout.flush()
                self.db.client()
                return True
            except:
                sleep(delay)
        return False


    def reconnect(self, retries = 3, delay = 10):
        for _ in range(retries):
            try:
                self.db = redis.StrictRedis(host=self.host, port=self.port)
                self.db.client()
                return True
            except:
                sleep(delay)
        return False


    def enable_external_connections(self):
        self.db.config_set('protected-mode','no')


    def disable_external_connections(self):
        self.db.config_set('protected-mode','yes')
        for id in [i['id'] for i in self.db.client_list()]:
            self.db.client_kill_filter(id, skipme = True)


    def getJSON(self):
        return self.db.get(REDIS_JSON_KEY)


    def setJSON(self, info):
        return self.db.set(REDIS_JSON_KEY, info)


    def getNodeController(self):
        return self.db.get(REDIS_NODE_CONTROLLER_KEY)


    def setNodeController(self, node_controller):
        if node_controller.upper() in NODE_CONTROLLERS:
            return self.db.set(REDIS_NODE_CONTROLLER_KEY, node_controller)
        else:
            return "Invalid controller"


    def getMasterIP(self):
        return self.db.get(REDIS_MASTER_IP_KEY)


    def setMasterIP(self, ip):
        return self.db.set(REDIS_MASTER_IP_KEY, ip)


    def getSlaveIP(self):
        return self.db.get(REDIS_SLAVE_IP_KEY)


    def setSlaveIP(self, ip):
        return self.db.set(REDIS_SLAVE_IP_KEY, ip)
