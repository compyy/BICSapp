import Router
import sros
import F5
import os
from Dictionary import cmd_dict
from flask import Flask, request, flash, url_for, redirect, render_template, g, session
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
import ansibleapi
from easysnmp import Session
import re

app = Flask(__name__)
app.secret_key = "g0AwAy"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:P@$$w0rd12@localhost/EmpLog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
os.environ['MIBDIRS'] = '/home/beta/BICSapp/MIB'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(db.Model):
    __tablename__ = "User"
    id = db.Column('userId', db.Integer, primary_key=True)
    username = db.Column('userName', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(10))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % self.username


def initate_session(input):
    try:
        session = Session(hostname=input['hostname'], community='public', version=2)
        description = session.get('.1.3.6.1.2.1.1.1.0')


    except Exception as e:
        print "Unable to Login to the Host Error: ", e

    if (re.search('Cisco IOS', description.value, flags=re.IGNORECASE)):
        driver = 'cisco_ios'

    elif (re.search('ALCATEL', description.value, flags=re.IGNORECASE) or re.search('nokia', description.value,
                                                                                    flags=re.IGNORECASE)):
        driver = 'alcatel_sros'

    else:
        print "Unable to identify System"
        driver = ''

    return Router.Router(input, driver)


def processCMD(connection, input):
    returncmd = []
    for i in cmd:
        if 'GRX' in i:
            if connection.driver == 'cisco_ios':
                if 'GRX_ARP_C' in i:
                    arp_codif = True
                elif 'GRX_ARP_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + input['iparp']
                    returncmd.append(j)
                elif 'GRX_BGP_N_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + 'summary | i ' + input['AS']
                    returncmd.append(j)
                elif 'GRX_BGP_N_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + 'neighbors ' + input['bgppeer']
                    returncmd.append(j)
                elif 'GRX_BGP_N_RR_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + ' neighbors ' + input['bgppeer'] + ' routes'
                    returncmd.append(j)
                elif 'GRX_BGP_N_AR_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + ' neighbors ' + input[
                        'bgppeer'] + ' advertised-routes'
                    returncmd.append(j)
                elif 'GRX_BGP_R_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + 'regexp ^' + input['AS']
                    returncmd.append(j)
                elif 'GRX_INT_C' in i:
                    int_codif = True
                elif 'GRX_PING_VRF' in i:
                    j = 'ping vrf cbugrx1 ' + input['bgppeer']
                    returncmd.append(j)
                elif 'GRX_RT' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + input['prefix']
                    returncmd.append(j)
                elif 'GRX_TR' in i:
                    j = 'traceroute vrf cbugrx1 ' + input['bgppeer']
                    returncmd.append(j)

            elif connection.driver == 'alcatel_sros':
                if 'GRX_ARP_C' in i:
                    arp_codif = True
                elif 'GRX_ARP_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 arp ' + input['iparp']
                    returncmd.append(j)
                elif 'GRX_BGP_N_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + 'bgp neighbor ' + input['AS']
                    returncmd.append(j)
                elif 'GRX_BGP_N_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + 'bgp neighbor ' + input['bgppeer']
                    returncmd.append(j)
                elif 'GRX_BGP_N_RR_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + 'bgp neighbor ' + input[
                        'bgppeer'] + ' received-routes'
                    returncmd.append(j)
                elif 'GRX_BGP_N_AR_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + 'bgp neighbor ' + input[
                        'bgppeer'] + ' advertised-routes'
                    returncmd.append(j)
                elif 'GRX_BGP_R_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + 'bgp routes aspath-regex ^' + input['AS']
                    returncmd.append(j)
                elif 'GRX_INT_C' in i:
                    int_codif = True
                elif 'GRX_PING_VRF' in i:
                    j = 'ping service-name 110 ' + input['pingtrace']
                    returncmd.append(j)
                elif 'GRX_RT' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + 'bgp routes ' + input['prefix']
                    returncmd.append(j)
                elif 'GRX_TR' in i:
                    j = 'traceroute service-name 110 ' + input['pingtrace']
                    returncmd.append(j)

        if 'BGP_G' in i:
            if connection.driver == 'cisco_ios':
                if 'BGP_G_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' ' + input['bgppeer']
                    returncmd.append(j)
                elif 'BGP_G_AR_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' ' + input['bgppeer'] + ' advertised-routes'
                    returncmd.append(j)
                elif 'BGP_G_RR_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' ' + input['bgppeer'] + ' routes'
                    returncmd.append(j)
                elif 'BGP_G_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' ' + ' summary | i ' + input['AS']
                    returncmd.append(j)
                elif 'BGP_G_AR_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' ' + ' summary | i ' + input['AS']
                    returncmd.append(j)
                elif 'BGP_G_RR_AS' in i:
                    j = cmd_dict[connection.driver][i] + 'regexp ^' + input['AS']
                    returncmd.append(j)

            elif connection.driver == 'alcatel_sros':
                if 'BGP_G_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' ' + input['bgppeer']
                    returncmd.append(j)
                elif 'BGP_G_AR_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' ' + input['bgppeer'] + ' advertised-routes'
                    returncmd.append(j)
                elif 'BGP_G_RR_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' ' + input['bgppeer'] + ' received-routes'
                    returncmd.append(j)
                elif 'BGP_G_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' ' + input['AS']
                    returncmd.append(j)
                elif 'BGP_G_AR_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' ' + input['bgppeer'] + ' advertised-routes'
                    returncmd.append(j)
                elif 'BGP_G_RR_AS' in i:
                    j = cmd_dict[connection.driver][i] + 'bgp routes aspath-regex ^' + input['AS']
                    returncmd.append(j)

    outputCMD = connection.ansible_show(returncmd)
    return outputCMD


@app.route('/GRX', methods=['GET', 'POST'])
@login_required
def GRX():
    if request.method == 'GET':
        return render_template('GRX.html', cmd=cmd)

    input = request.form.to_dict()
    input['cmd'] = cmd
    connection = initate_session(input)
    outputCMD = processCMD(connection, input)
    return render_template("output.html", ifHostAlive='', cmd=outputCMD)


@app.route('/ASASHOW', methods=['GET', 'POST'])
@login_required
def ASASHOW():
    if request.method == 'GET':
        return render_template('showasa.html', cmd=cmd)

    input = request.form.to_dict()
    command = []
    module = 'asa_command'

    for i in cmd:
        if 'ASASHOW_S_O' in i:
            command.append(cmd_dict['cisco_asa'][i] + input['obj'])
        elif 'ASASHOW_S_GO' in i:
            command.append(cmd_dict['cisco_asa'][i] + input['objg'])
        elif 'ASASHOW_S_ACL' in i:
            command.append(cmd_dict['cisco_asa'][i] + input['acl'])

    ansibleoutput = ansibleapi.run_asa(input, command, module)
    output = ansibleoutput.host_ok[0]['result']._result['stdout']
    return render_template("outputasa.html", ifHostAlive='Host is reachable', output=output)


@app.route('/ASACONF', methods=['GET', 'POST'])
@login_required
def ASACONF():
    if request.method == 'GET':
        return render_template('confasa.html', cmd=cmd)

    input = request.form.to_dict()

    ansibleoutput = []
    output = []
    for i in cmd:
        if 'ASACONF_C_ACL' in i:
            ansibleoutput.append(ansibleapi.run_asa(input, cmd_dict['cisco_asa'][i], 'asa_acl'))
        elif 'ASACONF_C_O' in i:
            ansibleoutput.append(ansibleapi.run_asa(input, cmd_dict['cisco_asa'][i], 'asa_config'))
        elif 'ASACONF_C_GO' in i:
            ansibleoutput.append(ansibleapi.run_asa(input, cmd_dict['cisco_asa'][i], 'asa_config'))


    for i in ansibleoutput:
        print i.host_ok[0]['result']._result
        changed = i.host_ok[0]['result']._result['changed']
        if changed:
            output.append('Following configurations has been applied on the FW.\n' +
                          '\n'.join([str(j) for j in i.host_ok[0]['result']._result['updates']]))
        else:
            parent = i.host_ok[0]['result']._result['invocation']['module_args'].get('parents', '')
            output.append('Following Configurations were not applied as same config already present in FW.\n' +'\n'+ '\n'.join(
                [str(j) for j in parent]) +'\n'+ '\n'.join(
                [str(k) for k in i.host_ok[0]['result']._result['invocation']['module_args']['lines']]))

    return render_template("outputasa.html", ifHostAlive='Host is reachable', output=output)


@app.route('/BGP_GLOBAL', methods=['GET', 'POST'])
@login_required
def BGP_GLOBAL():
    if request.method == 'GET':
        return render_template('BGP.html', cmd=cmd)

    input = request.form.to_dict()
    input['cmd'] = cmd
    # for i in cmd:
    #   if 'BGP_G_IP' in i:
    #       args = dict()
    #       args['community'] = 'public'
    #       nokia = sros.SrosDriver(input['hostname'], input['username'], input['password'], 20, args)
    #       nokia.open()
    #       if hasattr(nokia, 'get_bgp_neighbors'):
    #           out = getattr(nokia, 'get_bgp_neighbors')()

    #       print out
    #        return redirect(url_for('index'))
    connection = initate_session(input)
    outputCMD = processCMD(connection, input)
    return render_template("output.html", ifHostAlive='', cmd=outputCMD)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
@login_required
def index():
    return redirect(url_for('take_input'))


@app.route('/input', methods=['GET', 'POST'])
@login_required
def take_input():
    if request.method == 'GET':
        return render_template('input.html')

    options = request.form.getlist('selectcmd')
    global cmd
    cmd = []
    cmd = request.form.getlist(options[0])
    return redirect(url_for(options[0]))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['sqlusername']
    password = request.form['sqlpassword']
    registered_user = User.query.filter_by(username=username, password=password).first()
    if registered_user is None:
        flash('Username or Password is invalid, Try again or Contact Administrator', 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    return redirect(request.args.get('next') or url_for('index'))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
