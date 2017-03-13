from netmiko import ConnectHandler


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
            print i
            output.append(self.session.send_command(i))
        return output
