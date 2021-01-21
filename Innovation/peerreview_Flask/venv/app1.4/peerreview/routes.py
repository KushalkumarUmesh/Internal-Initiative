from flask import render_template,request,redirect,url_for,flash
from peerreview import app,db
from peerreview.forms import LoginForm
from peerreview.models import EmployeeDetails,Login,CreateProject
from flask_login import login_user,logout_user,current_user,login_required,login_manager
from werkzeug.security import generate_password_hash,check_password_hash

# Base page routing in case of multiple applications
# @app.route("/")
# @app.route("/index")
# def index():
#     return render_template('index.html',title='Index')

@app.route("/")
@app.route("/home")
@login_required  
def home():
    userlevel=current_user.USR_LEVEL_ID
    return render_template('home.html',title='Home',userlevel=userlevel) 

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = EmployeeDetails.query.filter_by(LOGIN_USR_ID=form.email.data).first()
        # if user and user.LOGIN_PASSWORD == form.password.data:
        if user and check_password_hash(user.LOGIN_PASSWORD,form.password.data):
            login_user(user,remember=form.remember.data)
            flash('Logged in successfully!','success')
            #saving login user details to Login_info table
            log=Login(LOGIN_NAME=user.EMP_NAME,LOGIN_USR_ID=user.LOGIN_USR_ID,LOGIN_DATE=None)
            db.session.add(log)
            db.session.commit()

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))   
        else:
            flash('Login Unsuccessful.Please check your Email and Password.','danger')
    return render_template('login.html',title='login' ,form = form)

@app.route("/logout")
@login_required 
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/reset")
def reset():
    return render_template('reset.html', title='Reset')
    
@app.route("/create_new_project",methods=['GET','POST'])
@login_required 
def create_new_project():
    if request.method == 'POST':
        
        PRJ_NAME = request.form['Projectname'],
        MANUAL_CHECKLIST = request.form.get('manual-chkbox'),
        MANUAL_DEFECT_CHECKLIST = request.form.get('manual-defect-chkbox'),
        MANUAL_TESTCASE_CHECKLIST = request.form.get('manual-testcase-chkbox'),
        MANUAL_TRACEABILITY_CHECKLIST = request.form.get('manual-reqtrace-chkbox'),
        AUTOMATION_CHECKLIST = request.form.get('auto-chkbox'),
        AUTO_STD_CHECKLIST = request.form.get('auto-autostd-chkbox'),
        AUTO_PYTHON_CHECKLIST = request.form.get('auto-python-chkbox'),
        AUTO_JAVA_CHECKLIST = request.form.get('auto-java-chkbox'),
        AUTO_C_CHECKLIST = request.form.get('auto-c#-chkbox'),
        AUTO_TOSCA_CHECKLIST = request.form.get('auto-tosca-chkbox'),
        AUTO_UFT_CHECKLIST = request.form.get('auto-uft-chkbox'),
        MANAGEMENT_CHECKLIST = request.form.get('mgmt-chkbox'),
        MGMT_TESTPLAN_CHECKLIST = request.form.get('mgmt-testplan-chkbox'),
        MGMT_TESTREPORT_CHECKLIST = request.form.get('mgmt-testreport-chkbox'),
        MGMT_TESTENVISETUP_CHECKLIST = request.form.get('mgmt-testenvtsetup-chkbox'),
        PERFORMANCE_CHECKLIST = request.form.get('performance-chkbox'),
        SECURITY_CHECKLIST = request.form.get('security-chkbox'),
        SPOC_ID = request.form['spoc'],
        REVIEWERS = request.form.getlist('lstBox2'),
        FREQUENCY_ID = request.form.get('frq-chkbox')

        Reviewers_list = list(REVIEWERS)
        flatlist = []
        for element in Reviewers_list:
            flatlist.extend(element)
        str1 = ';'.join(flatlist)


        new_project = CreateProject(PRJ_NAME=PRJ_NAME,MANUAL_CHECKLIST=MANUAL_CHECKLIST,MANUAL_DEFECT_CHECKLIST=MANUAL_DEFECT_CHECKLIST,MANUAL_TESTCASE_CHECKLIST=MANUAL_TESTCASE_CHECKLIST,
                                    MANUAL_TRACEABILITY_CHECKLIST=MANUAL_TRACEABILITY_CHECKLIST,AUTOMATION_CHECKLIST=AUTOMATION_CHECKLIST,AUTO_STD_CHECKLIST=AUTO_STD_CHECKLIST,
                                    AUTO_PYTHON_CHECKLIST=AUTO_PYTHON_CHECKLIST,AUTO_JAVA_CHECKLIST=AUTO_JAVA_CHECKLIST,AUTO_C_CHECKLIST=AUTO_C_CHECKLIST,
                                    AUTO_TOSCA_CHECKLIST=AUTO_TOSCA_CHECKLIST,AUTO_UFT_CHECKLIST=AUTO_UFT_CHECKLIST,MANAGEMENT_CHECKLIST=MANAGEMENT_CHECKLIST,
                                    MGMT_TESTPLAN_CHECKLIST=MGMT_TESTPLAN_CHECKLIST,MGMT_TESTREPORT_CHECKLIST=MGMT_TESTREPORT_CHECKLIST,MGMT_TESTENVISETUP_CHECKLIST=MGMT_TESTENVISETUP_CHECKLIST,
                                    PERFORMANCE_CHECKLIST=PERFORMANCE_CHECKLIST,SECURITY_CHECKLIST=SECURITY_CHECKLIST,SPOC_ID=SPOC_ID,REVIEWERS=str1,FREQUENCY_ID=FREQUENCY_ID)
        db.session.add(new_project)
        db.session.commit()
        
        return redirect(url_for('create_new_project'))

    return render_template('create_new_project.html',title='create_new_project')

@app.route("/edit_existing_project",methods=['GET','POST'])
@login_required 
def edit_existing_project():
    return render_template('edit_existing_project.html') 

@app.route("/update_tracker",methods=['GET','POST'])
@login_required 
def update_tracker():
    return render_template('update_tracker.html')         
