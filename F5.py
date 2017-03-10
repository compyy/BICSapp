from f5.bigip import ManagementRoot

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



class F5:
    def __init__(self, username, password, hostname):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.dead = False

        try:
            self.mgmt = ManagementRoot(self.hostname, self.username, self.password)

        except:
            self.dead = True

    def runHC(self):
        pools = self.mgmt.tm.ltm.pools.get_collection()
        for pool in pools:
            print pool.name
            for member in pool.members_s.get_collection():
                print member.name

        mypool = self.mgmt.tm.ltm.pools.pool.create(name='mypool', partition='Common')

        pool_a = self.mgmt.tm.ltm.pools.pool.load(name='mypool', partition='Common')
        pool_a.description = "New description"
        pool_a.update()

        pools = self.mgmt.tm.ltm.pools.get_collection()
        for pool in pools:
            print pool.name
            for member in pool.members_s.get_collection():
                print member.name

        if self.mgmt.tm.ltm.pools.pool.exists(name='mypool', partition='Common'):
            pool_b = self.mgmt.tm.ltm.pools.pool.load(name='mypool', partition='Common')
            pool_b.delete()
