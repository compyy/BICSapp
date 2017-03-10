import Router
import F5
import telnetlib
from Dictionary import cmd_dict
from Dictionary import driver_dict
from flask import Flask, request, flash, url_for, redirect, render_template, g, session
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "g0AwAy"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:P@$$w0rd12@localhost/EmpLog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)
global cmd

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
    driver = 'Cisco'
    try:
        connection = telnetlib.Telnet(input['hostname'], 22)
        get_driver = connection.expect([r'^SSH\-\d\.\d+\-(.*)(\-|\_).*', ])
        driver = get_driver[1].group(1)
        connection.close()

    except Exception as e:
        print "Unable to Login to the Host Error: ", e

    return Router.Router(input, driver_dict[driver])


def processCMD(connection, input):
    returncmd = []
    for i in cmd:
        if 'GRX' in i:
            if connection.driver == 'cisco_ios':
                if 'GRX_ARP_C' in i:
                    arp_codif = True
                elif 'GRX_ARP_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + input['peer']
                    returncmd.append(j)
                elif 'GRX_BGP_N_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + 'summary | i ' + input['AS']
                    returncmd.append(j)
                elif 'GRX_BGP_N_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + 'neighbors ' + input['peer']
                    returncmd.append(j)
                elif 'GRX_BGP_N_RR' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + ' neighbors ' + input['peer'] + ' routes'
                    returncmd.append(j)
                elif 'GRX_BGP_N_AR' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + ' neighbors ' + input['peer'] + ' advertised-routes'
                    returncmd.append(j)
                elif 'GRX_BGP_R_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + 'regexp ^' + input['AS']
                    returncmd.append(j)
                elif 'GRX_INT_C' in i:
                    int_codif = True
                elif 'GRX_PING_VRF' in i:
                    j = 'ping vrf cbugrx1 ' + input['peer']
                    returncmd.append(j)
                elif 'GRX_RT' in i:
                    j = cmd_dict[connection.driver][i] + ' cbugrx1 ' + input['prefix']
                    returncmd.append(j)
                elif 'GRX_TR' in i:
                    j = 'traceroute vrf cbugrx1 ' + input['peer']
                    returncmd.append(j)

            elif connection.driver == 'alcatel_sros':
                if 'GRX_ARP_C' in i:
                    arp_codif = True
                elif 'GRX_ARP_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 arp ' + input['peer']
                    returncmd.append(j)
                elif 'GRX_BGP_N_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + ' bgp neighbor ' + input['AS']
                    returncmd.append(j)
                elif 'GRX_BGP_N_IP' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + ' bgp neighbor ' + input['peer']
                    returncmd.append(j)
                elif 'GRX_BGP_N_RR' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + ' bgp neighbor ' + input['peer'] + ' received-routes'
                    returncmd.append(j)
                elif 'GRX_BGP_N_AR' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + ' bgp neighbor ' + input['peer'] + ' advertised-routes'
                    returncmd.append(j)
                elif 'GRX_BGP_R_AS' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + 'bgp routes aspath-regex ^' + input['AS']
                    returncmd.append(j)
                elif 'GRX_INT_C' in i:
                    int_codif = True
                elif 'GRX_PING_VRF' in i:
                    j = 'ping service-name 110 ' + input['peer']
                    returncmd.append(j)
                elif 'GRX_RT' in i:
                    j = cmd_dict[connection.driver][i] + ' 110 ' + 'bgp routes ' + input['prefix']
                    returncmd.append(j)
                elif 'GRX_TR' in i:
                    j = 'traceroute service-name 110 ' + input['peer']
                    returncmd.append(j)

    outputCMD = connection.runCMD(returncmd)
    return outputCMD


@app.route('/GRX', methods=['GET', 'POST'])
@login_required
def GRX():
    if request.method == 'GET':
        return render_template('GRX.html')

    input = {'username': request.form['username'],
             'password': request.form['password'],
             'hostname': request.form['hostname'],
             'cmd': cmd,
             'peer': request.form['peer'],
             'codif': request.form['codif'],
             'prefix': request.form['prefix'],
             'AS': request.form['AS']}

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
