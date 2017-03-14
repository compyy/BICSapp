# -*- coding: utf-8 -*-
import json
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins import callback_loader
from ansible.plugins.callback import CallbackBase


loader = DataLoader()
variable_manager = VariableManager()
inventory = Inventory(loader=loader, variable_manager=variable_manager)
variable_manager.set_inventory(inventory)


# get result output
class ResultsCollector(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = []
        self.host_unreachable = []
        self.host_failed = []

    def v2_runner_on_unreachable(self, result, ignore_errors=False):
        name = result._host.get_name()
        task = result._task.get_name()
        print(result._result)
        # self.host_unreachable[result._host.get_name()] = result
        self.host_unreachable.append(dict(ip=name, task=task, result=result))

    def v2_runner_on_ok(self, result, *args, **kwargs):
        name = result._host.get_name()
        task = result._task.get_name()
        #print json.dumps(result._result)
        self.host_ok.append(dict(ip=name, task=task, result=result))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        name = result._host.get_name()
        task = result._task.get_name()
        print(result._result)
        self.host_failed.append(dict(ip=name, task=task, result=result))


class Options(object):
    def __init__(self):
        self.connection = 'local'
        self.forks = 10
        self.check = False
        self.become = None
        self.become_method = None
        self.become_user = None

    def __getattr__(self, name):
        return None


options = Options()


def run_adhoc(username, password, hostname, cmd, driver):
    play_source = dict(
        name='BICS  API',
        hosts=hostname,
        gather_facts='False',

        tasks=[dict(action=dict(module='ntc_show_command', args=dict(
            connection = 'netmiko_ssh',
            platform = driver,
            command = cmd,
            template_dir = '/home/beta/ntc-ansible/ntc-templates/templates',
            host = hostname,
            username = username,
            password = password,
            secret = password,
        )))]
    )

    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    tqm = None
    callback = ResultsCollector()

    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=None,
            run_tree=False,
        )
        tqm._stdout_callback = callback
        result = tqm.run(play)
        return callback

    finally:
        if tqm is not None:
            tqm.cleanup()


def run_playbook(books):
    results_callback = callback_loader.get('json')
    playbooks = [books]

    variable_manager.extra_vars = {'ansible_ssh_user': 'cisco', 'ansible_ssh_pass': 'cisco'}
    callback = ResultsCollector()

    pd = PlaybookExecutor(
        playbooks=playbooks,
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        options=options,
        passwords=None,

    )
    pd._tqm._stdout_callback = callback

    try:
        result = pd.run()
        return callback

    except Exception as e:
        print e



#if __name__ == '__main__':
#    object = run_adhoc('cisco', 'cisco', '192.168.124.250', 'show ip int brief', 'cisco_ios')
#    print object.host_ok[0]['result']._result['response']
    # run_playbook('yml/info/process.yml')