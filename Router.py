from netmiko import ConnectHandler


class Router:
    def __init__(self, username, password, hostname, driver):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.dead = False
        self.driver = driver
        self.peer = ''
        self.interface = ''
        self.vrf = ''

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
