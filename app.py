import Router
import telnetlib
from Dictionary import cmd_dict
from Dictionary import driver_dict
from flask import Flask, request, flash, url_for, redirect, render_template, g
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "g0AwAy"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:P@$$w0rd12@localhost/EmpLog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
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


def initate_session(username, password, hostname):
    driver='Cisco'
    try:
        session = telnetlib.Telnet(hostname, 22)
        get_driver = session.expect([r'^SSH\-\d\.\d+\-(.*)(\-|\_).*', ])
        driver = get_driver[1].group(1)
        session.close()

    except Exception as e:
        print "Unable to Login to the Host Error: ", e

    return Router.Router(username, password, hostname, driver_dict[driver])

def processCMD(session, cmd):
    returncmd = []

    for i in cmd:
        if 'BGP_N_G' in i:
            if 'BGP_N_G_RR' in i:
                i = cmd_dict[session.driver][i] + ' ' + session.peer + ' received-routes'
                returncmd.append(i)

            elif 'BGP_N_G_AR' in i:
                i = cmd_dict[session.driver][i] + ' ' + session.peer + ' advertised-routes'
                returncmd.append(i)

            else:
                i = cmd_dict[session.driver][i] + ' ' + session.peer
                returncmd.append(i)

        elif 'BGP_N_V' in i:
            if session.driver == 'cisco_ios':
                if 'BGP_N_V_RR' in i:
                    i = cmd_dict[session.driver][i] + ' ' + session.vrf + ' neighbors ' + session.peer + ' routes'
                    returncmd.append(i)

                elif 'BGP_N_V_AR' in i:
                    i = cmd_dict[session.driver][
                            i] + ' ' + session.vrf + ' neighbors ' + session.peer + ' advertised-routes'
                    returncmd.append(i)

                else:
                    i = cmd_dict[session.driver][i] + ' ' + session.vrf + ' neighbors ' + session.peer
                    returncmd.append(i)

            elif session.driver == 'alcatel_sros':
                if 'BGP_N_V_RR' in i:
                    i = cmd_dict[session.driver][i] + ' ' + session.vrf + ' ' + session.peer + ' received-routes'
                    returncmd.append(i)

                elif 'BGP_N_V_AR' in i:
                    i = cmd_dict[session.driver][i] + ' ' + session.vrf + ' ' + session.peer + ' advertised-routes'
                    returncmd.append(i)

                else:
                    i = cmd_dict[session.driver][i] + ' ' + session.vrf + ' ' + session.peer
                    returncmd.append(i)

        elif 'R_INT' in i:
            if 'R_INT_C' in i:
                if session.driver == 'alcatel_sros':
                    i = cmd_dict[session.driver][i] + ' ' + session.interface + '  statistics'
                    returncmd.append(i)
                else:
                    i = cmd_dict[session.driver][i] + ' ' + session.interface + ' | i rate'
                    returncmd.append(i)
            else:
                i = cmd_dict[session.driver][i] + ' ' + session.interface
                returncmd.append(i)

    outputCMD = session.runCMD(returncmd)
    return outputCMD


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
@login_required
def index():
    return redirect(url_for('executeCLI'))


@app.route('/form', methods=['GET', 'POST'])
@login_required
def executeCLI():
    if request.method == 'GET':
        return render_template('form.html')

    username = request.form['username']
    password = request.form['password']
    hostname = request.form['hostname']
    cmd = request.form.getlist('q9_checks')
    session = initate_session(username, password, hostname)
    if session.dead:
        ifHostAlive = hostname + " is Dead or could not login, Check if IP is correct or contact 2LINF."
        return render_template("output.html", ifHostAlive=ifHostAlive, cmd='')

    session.peer = request.form['PEER']
    session.vrf = request.form['VRF']
    session.interface = request.form['INT']

    if cmd[0] == 'ifHostAlive':
        ifHostAlive = "Yes: " + hostname + " is Alive."
        cmd.pop(0)
    else:
        ifHostAlive = "Output of Applied Commands: "

    outputCMD = processCMD(session, cmd)
    return render_template("output.html", ifHostAlive=ifHostAlive, cmd=outputCMD)


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
