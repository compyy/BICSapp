from netmiko import ConnectHandler
import ansibleapi

class Router:
    def __init__(self, input, driver):
        self.username = input['username']
        self.password = input['password']
        self.hostname = input['hostname']
        self.dead = False
        self.driver = driver

        self.ROUTER = {
            'device_type': self.driver,
            'ip': self.hostname,
            'username': self.username,
            'password': self.password,
            'verbose': True,

        }
        try:
            self.session = ConnectHandler(**self.ROUTER)

        except:
            self.dead = True

    def runCMD(self, cmd):
        output = []
        for i in cmd:
            output.append(self.session.send_command(i))
        return output


    def ansible_show(self, cmd):
        output = []
        for i in cmd:
            ansibleoutput = ansibleapi.run_ntcshow(self.username, self.password, self.hostname, i, self.driver)
            output.append(ansibleoutput.host_ok[0]['result']._result['response'])

        return output


