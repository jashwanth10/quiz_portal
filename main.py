from flask import Flask,render_template,flash,redirect,logging,request,url_for,session
from flask_mysqldb import MySQL
from wtforms import Form,StringField,PasswordField,validators
from passlib.hash import sha256_crypt
import random
from question import *


app = Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='gajjala2000'
app.config['MYSQL_DB']='flaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql = MySQL(app)


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/<a>')
def i(a):
    return redirect(url_for("home"))


@app.route('/home',methods=['GET','POST'])
def home():
    if 'name' in session:
            redirect(url_for('verification'))
    if 'logged_in' in session:
        if session['username']=='Adminvj':
            return redirect(url_for('admin_view'))
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM rmainquiz')
        mquiz = cur.fetchall()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz')
        quiz = cur.fetchall()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz WHERE us_id >= 1')
        data = cur.fetchall()
        return render_template('user_int.html',mquiz=mquiz,quiz=quiz,data = data)
    return redirect(url_for('register' ))


@app.route('/admin_view',methods=['GET','POST'])
def admin_view():
    if 'logged_in' in session:
        if session['username'] == 'Adminvj':
            return render_template('test.html')
    return redirect(url_for('home'))


@app.route('/myscoreboard')
def myscoreboard():
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM scoreboard where user_id = %s',[session['user_id']])
        rows = cur.fetchall()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz where us_id = %s',[session['user_id']])
        rows2=cur.fetchall()
        return render_template('scoreboard.html',rows=rows,rows2=rows2)
    return redirect(url_for('home'))


@app.route('/leaderboard')
def leaderboard():
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM scoreboard ORDER BY score DESC')
        ordered_data = cur.fetchall()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM  users')
        users = cur.fetchall()
        cur.close()
        quiz_name=[]
        user_name=[]
        quiz_ids=[]
        user_score = []
        quiz_len=[]
        cum = []
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz WHERE us_id = 17')
        name = cur.fetchall()
        cur.close()
        for row in name:
            quiz_name.append(row['q_title'])
        for i in range(len(quiz_name)):
            quiz_len.append(0)
            for row in ordered_data:
                cur = mysql.connection.cursor()
                cur.execute('SELECT q_title FROM quiz WHERE pr_id = %s',[row['quiz_id']])
                name = cur.fetchone()
                if(name['q_title'] == quiz_name[i]):
                    cur = mysql.connection.cursor()
                    cur.execute('SELECT username FROM users WHERE id = %s',[row['user_id']])
                    u_name = cur.fetchone()
                    user_name.append(u_name['username'])
                    cur.close()
                    quiz_len[i] += 1
                    user_score.append(row['score'])
        cum.append(quiz_len[0])
        for i in range(1,len(quiz_name)):
            cum.append(cum[i-1] + quiz_len[i])
        cum.append(0)
        return render_template('leaderboard.html',cum=cum,l = len(quiz_name),quiz_name=quiz_name,quiz_len = quiz_len,user_score = user_score, user_name = user_name)


@app.route('/admin_show_users')
def admin_users():
    if session['username'] == 'Adminvj':
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users')
        rows = cur.fetchall()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz')
        rows2 = cur.fetchall()
        cur.close()
        return render_template('user.html',rows=rows,rows2 = rows2)
    return 'NOT ACCESSIBLE'


@app.route('/admin_delete_users',methods = ['GET','POST'])
def del_users():
    if session['username'] == 'Adminvj':
        if request.method == 'POST':
            username = request.form['username']
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM users WHERE username = %s',[username])
            user_id = cur.fetchone()
            user_id = user_id['id']
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('DELETE  FROM scoreboard WHERE user_id = %s',[user_id])
            mysql.connection.commit()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM quiz_user_answer WHERE user_id = %s',[user_id])
            mysql.connection.commit()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM quiz_user_restore WHERE user_id = %s',[user_id])
            mysql.connection.commit()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM quiz WHERE us_id = %s',[user_id])
            mysql.connection.commit()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM users WHERE id = %s',[user_id])
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('home'))
        return render_template('delete_users.html')
    return 'NOT ACCESSIBLE'


@app.route('/admin_create_quiz',methods=['GET','POST'])
def create_quiz():
    if session['username'] == 'Adminvj':
        y = 0
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz')
        quiz = cur.fetchall()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM rmainquiz')
        m_quiz = cur.fetchall()
        cur.close()
        if request.method == 'POST':
            newquizname = request.form['new_quiz']
            mainquizname = request.form['main_quiz']
            iurl=request.form['iurl']
            cur = mysql.connection.cursor()
            test = cur.execute('SELECT * FROM rmainquiz  WHERE  q_maintitle = %s',[mainquizname])
            cur.close()
            x = 17
            if len(iurl) < 4:
                    iurl="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRIjnJmL8vUo71h8fgIDPceMC_hd1EGR17BAkzlhuCnYskoWB2_"
            if(test == 0):
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO rmainquiz(q_maintitle,qu_id,url) VALUES(%s,%s,%s)',(mainquizname,x,iurl))
                mysql.connection.commit()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute('SELECT * FROM rmainquiz WHERE id = (SELECT max(id) FROM rmainquiz )')
                data = cur.fetchone()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO quiz(q_title,us_id,m_id) VALUES(%s,%s,%s)',(newquizname,x,data['id']))
                mysql.connection.commit()
                cur.close()
                cur=mysql.connection.cursor()
                iid = cur.execute('SELECT id FROM rmainquiz  WHERE  q_maintitle = %s',[mainquizname])
                iid= cur.fetchone()
                cur.execute('INSERT INTO images(url,qu_id) VALUES(%s,%s)',[iurl,iid['id']])
                mysql.connection.commit()
                cur.close()
            else:
                cur = mysql.connection.cursor()
                f_id = cur.execute('SELECT id FROM rmainquiz WHERE  q_maintitle = %s',[mainquizname])
                f_id = cur.fetchone()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO quiz(q_title,us_id,m_id) VALUES(%s,%s,%s)',(newquizname,x,f_id['id']))
                mysql.connection.commit()
                cur.close()
            cur = mysql.connection.cursor()
            cur.execute('SELECT pr_id FROM quiz WHERE q_title = %s AND us_id = %s',(newquizname,x))
            _id = cur.fetchone()
            cur.close()
            try :
                test = request.form['type']
                print(test)
                if (test == 'type_s'):
                    y = 1
                else:
                    y = 0
                print('sahooooooooooooooooo')
            except :
                pass
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO quiz_type(quiz_id,q_type) VALUES(%s,%s)',(_id['pr_id'],y))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('addq'))
        return render_template('create_quiz.html',quiz=quiz,m_quiz=m_quiz)

    return 'NOT ACCESSIBLE'


@app.route('/add_question',methods=['GET','POST'])
def addq():
    if session['username'] == 'Adminvj':
        if request.method =='POST':
            x=0
            q_text = request.form['q_text']
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM quiz WHERE pr_id = (SELECT max(pr_id) FROM quiz )')

            data = cur.fetchone()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO quiz_questions(question,quiz_id) VALUES(%s, %s)',(q_text,data['pr_id']))
            mysql.connection.commit()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM quiz_questions WHERE id = (SELECT max(id) FROM quiz_questions )')
            data = cur.fetchone()
            cur.close()
            try :
                test = request.form['a_valid']
                x+=1
            except :
                pass
            try :
                test = request.form['b_valid']
                x+=2
            except :
                pass
            try :
                test = request.form['c_valid']
                x+=4
            except :
                pass
            try :
                test = request.form['d_valid']
                x+=8
            except :
                pass
            optA = request.form['a_name']
            optB = request.form['b_name']
            optC = request.form['c_name']
            optD = request.form['d_name']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO quiz_question_options(optA,optB,optC,optD,ans,question_id) VALUES(%s,%s,%s,%s,%s,%s)',(optA,optB,optC,optD,x,data['id']))
            mysql.connection.commit()
            cur.close()
            try:
                test = request.form['last']
                return redirect(url_for('admin_view'))
            except :
                return redirect(url_for('addq'))
        return render_template('create_question.html')
    return 'NOT ACCESSIBLE'


@app.route('/register',methods=['GET','POST'])
def register():
    if 'name' in session:
            return redirect(url_for('verification'))
    if 'logged_in'  in session:
        if session['username']=='Adminvj':
            return redirect(url_for('admin_view'))
        return redirect(url_for('home'))
    form = registerform(request.form)
    if request.method == 'POST' and form.validate():
        name = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur = mysql.connection.cursor()
        test = cur.execute('SELECT * FROM users WHERE username = %s',[name])
        if(test > 0):
            flash('Sorry,but that username is already existing,Try another interesting Name','danger')
            return redirect(url_for('register'))
        cur.execute('INSERT INTO users(username,email,password) VALUES(%s, %s, %s)',(name,email,password))
        mysql.connection.commit()
        cur.close()
        try:
            aaaaa=request.form['b_valid']
            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO otp(username) VALUES(%s)',[name])
            mysql.connection.commit()
            cur.close()
        except:
            pass
        flash('Registered successfully!!','success')
        return redirect(url_for('login'))
    return render_template('reg.html',form=form)

@app.route('/verification',methods =['GET','POST'])
def verification():
        if 'name' in session:
            if request.method== 'POST':
                ans=request.form['ans']
                if str(ans) == str(session['otp']):
                    name = session['name']
                    session['username']=session['name']
                    session['logged_in']=True
                    session.pop('name')
                    return redirect(url_for('home'))
                error="wrong otp"
                return render_template('verification.html',error=error)
            return render_template('verification.html')
        return redirect(url_for('home'))


@app.route('/login',methods = ['GET','POST'])
def login():
    if 'name' in session:
            return redirect(url_for('verification'))
    if 'logged_in' in session:
        if session['username']=='Adminvj':
            return redirect(url_for('admin_view'))
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password']
        cur =  mysql.connection.cursor()
        result = cur.execute('SELECT * FROM users WHERE username = %s',[username])
        if(result > 0):
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(password1,password):
                app.logger.info('PASSWORD MATCHED')
                session['logged_in']=True
                session['username']=username
                cur = mysql.connection.cursor()
                user_id = cur.execute('SELECT * FROM users WHERE username = %s',[username])
                user_id = cur.fetchone()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute('SELECT * FROM otp WHERE username=%s',[username])
                test=cur.fetchone()
                session['user_id'] = user_id['id']
                cur.close()
                if test is not None :
                    session['name']=username
                    session['mail']=user_id['email']
                    session['id']=test['id']
                    OTP=random.randint(1000,9999)
                    session['otp']=OTP
                    fun(user_id['email'],OTP)
                    session.pop('logged_in')
                    session.pop('username')
                    return redirect(url_for('verification'))
                if session['username'] == 'Adminvj':
                    return redirect(url_for('admin_view'))
                return redirect(url_for('home'))
            else:
                error = 'INVALID PASSWORD'
                return render_template('login.html',error=error)
            cur.close()
        else:
            error = 'INVALID USERNAME'
            return render_template('login.html',error=error)
    return render_template('login.html')


@app.route('/ehjklo')
def logout():
    if 1==1:
        session.clear()
        flash('logged out','success')
    return redirect(url_for('login'))


@app.route('/home/<name>/<x>',methods=['GET','POST'])
def quizz(name,x):
    y = 0
    print(x)
    gar1 = 17
    gar = 4
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT pr_id FROM quiz WHERE q_title = %s AND us_id = %s',(name,gar1))
        _id = cur.fetchone()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT q_type FROM quiz_type WHERE quiz_id = %s',[_id['pr_id']])
        q_type = cur.fetchone()
        cur.close()
        if ( x == '1' ):

            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM quiz WHERE q_title = %s',[name])
            create = cur.fetchall()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('SELECT pr_id FROM quiz WHERE q_title = %s AND us_id =%s',[name,session['user_id']])
            id_q = cur.fetchone()
            cur.close()
            if id_q is not None:
                cur = mysql.connection.cursor()
                cur.execute('SELECT score FROM scoreboard WHERE quiz_id = %s AND user_id = %s',[id_q['pr_id'],session['user_id']])
                score_q = cur.fetchone()
                cur.close()
                if score_q is not None:
                    for i in create:
                        if i['us_id'] != 1:
                            return render_template('restricted.html',score = score_q['score'])
        if(x == '1'):
            cur = mysql.connection.cursor()
            test = cur.execute('SELECT * FROM quiz WHERE us_id = %s AND q_title = %s',[session['user_id'],name])
            cur.close()
            if test == 0:
                cur = mysql.connection.cursor()
                print(session['user_id'])
                cur.execute('INSERT INTO quiz(q_title,us_id,m_id) VALUES(%s,%s,%s)',[name,session['user_id'],gar])
                mysql.connection.commit()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute('SELECT pr_id FROM quiz WHERE q_title = %s AND us_id =%s',[name,session['user_id']])
                id_q = cur.fetchone()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO quiz_user_restore(quiz_id,user_id,question_id) VALUES(%s, %s, %s)',[id_q['pr_id'],session['user_id'],x])
                mysql.connection.commit()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute('SELECT * FROM quiz WHERE q_title=%s AND us_id = %s',[name,session['user_id']])
                mata = cur.fetchone()
                cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz WHERE q_title=%s AND us_id = 17',[name])
        mata = cur.fetchone()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz_questions WHERE quiz_id=%s',[mata['pr_id']])
        data = cur.fetchall()
        print(type(data))
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz_question_options')
        data2 = cur.fetchall()
        cur.close()
        m = int(x) - 1
        if request.method == 'POST':
            cur = mysql.connection.cursor()
            cur.execute('SELECT pr_id FROM quiz WHERE q_title = %s AND us_id =%s',[name,session['user_id']])
            id_q = cur.fetchone()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('SELECT pr_id FROM quiz WHERE q_title = %s AND us_id =%s',[name,gar1])
            idm_q = cur.fetchone()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('UPDATE quiz_user_restore  SET question_id = %s WHERE quiz_id =%s AND user_id =%s',[data[m]['id'],id_q['pr_id'],session['user_id']])
            mysql.connection.commit()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('SELECT q_type FROM quiz_type WHERE quiz_id = %s ',[idm_q['pr_id']])
            q_type = cur.fetchone()
            cur.close()
            if(q_type['q_type'] == 0):
                try :
                    test = request.form['a_valid']
                    y+=1
                except :
                    pass
                try :
                    test = request.form['b_valid']
                    y+=2
                except :
                    pass
                try :
                    test = request.form['c_valid']
                    y+=4
                except :
                    pass
                try :
                    test = request.form['d_valid']
                    y+=8
                except :
                    pass
            else:
                try :
                    test = request.form['r_type']
                    if (test == 'a_valid'):
                        y+=1
                    if(test == 'b_valid'):
                        y+=2
                    if(test == 'c_valid'):
                        y+=4
                    if(test == 'd_valid'):
                        y += 8
                except:
                    pass
            cur = mysql.connection.cursor()
            test1 = cur.execute('SELECT * FROM quiz_user_answer WHERE question_id = %s AND user_id = %s',(data[m]['id'],session['user_id']) )
            if test1 == 0:
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO quiz_user_answer(ans,question_id,user_id) VALUES(%s, %s, %s)',(y,data[m]['id'],session['user_id']) )
                mysql.connection.commit()
                cur.close()
            else:
                print('ysessssssssssssssss')
                cur = mysql.connection.cursor()
                cur.execute('UPDATE quiz_user_answer SET ans = %s WHERE question_id = %s AND user_id = %s',[y,data[m]['id'],session['user_id']])
                mysql.connection.commit()
                cur.close()
            if(len(data) > int(x)):
                return redirect(url_for('quizz',name=name,x=int(x)+1))
        if (len(data) >= int(x)):
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM quiz_user_answer WHERE question_id=%s AND user_id=%s',(data[m]['id'],session['user_id']))
            test3=cur.fetchone()
            A=0
            B=0
            C=0
            D=0
            if test3 is not None:
                xx=test3['ans']
                if xx>=8:
                    D=1
                    xx-=8
                if xx>=4:
                    C=1
                    xx-=4
                if xx>=2:
                    B=1
                    xx-=2
                if xx>=1:
                    A=1
                    xx-=1
            return render_template('quizz.html',data=data[m],data2=data2,name=name,x=int(x),check = len(data),A=A,B=B,C=C,D=D,q_type = q_type['q_type'])
        return redirect(url_for('submit(name)'))


@app.route('/admin/quiz')
def qui():
    if 'logged_in' in session:
        if session['username']!='Adminvj':
            return redirect(url_for('home'))
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM rmainquiz')
        mquiz = cur.fetchall()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz')
        quiz = cur.fetchall()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz WHERE us_id >= 1')
        data = cur.fetchall()
        return render_template('adminquiz.html',mquiz=mquiz,quiz=quiz,data = data)
    return redirect(url_for('home'))


@app.route('/question/<quiz>')
def questions(quiz):
        yy = 17
        if 'logged_in' in session:
            if session['username']!='Adminvj':
                cur = mysql.connection.cursor()
                xx=17
                cur.excute('SELECT * FROM quiz WHERE q_title=%s AND us_id=%s',[quiz,xx])
                idd=cur.fetchone()
                cur.execute('SELECT question FROM quiz_questions WHERE qu_id=%s',[idd])
                question=cur.fetchall()
                option=[]
                cur.execute('SELECT id FROM quiz_questions WHERE qu_id=%s',[idd])
                data=cur.fetchall()
                for data1 in data:
                    cur.excute('SELECT * FROM quiz_question_options WHERE question_id=%s',[data])
                    aa=cur.fetchone()
                    option.push(aa)
                l=len(question)
                return render_template('questions.html',question=question,option=option)
            if session['username'] == 'Adminvj':
                cur = mysql.connection.cursor()
                cur.execute('SELECT pr_id FROM quiz WHERE q_title=%s AND us_id = %s',[quiz,yy])
                q_id = cur.fetchone()
                q_id = q_id['pr_id']
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute('SELECT * FROM quiz_questions WHERE quiz_id = %s',[q_id])
                question_rows = cur.fetchall()
                cur.close()
                options = []
                answers=[]
                for data in question_rows:
                    cur = mysql.connection.cursor()
                    cur.execute('SELECT * FROM quiz_question_options WHERE question_id = %s',[data['id']])
                    x = cur.fetchall()
                    x = x[0]
                    options.append(x)
                    cur.close()
                    ans = x['ans']
                    string = ''
                    if ans>=8:
                        string += 'D'
                        ans-=8
                    if ans>=4:
                        string += 'C'
                        ans-=4
                    if ans>=2:
                        string += 'B'
                        ans-=2
                    if ans>=1:
                        string += 'A'
                        ans-=1
                    string = ''.join(reversed(string))
                    answers.append(string)
                return render_template('adm_questions.html',l = len(question_rows),question_rows=question_rows,options=options,answers=answers)

@app.route('/qcond')
def qcond():
    return render_template('restricted.html')


@app.route('/home/<name>/submit')
def submit(name):
    da = 17
    score = 0
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT pr_id FROM quiz WHERE q_title = %s AND us_id = %s',[name,da])
        quiz_id = cur.fetchone()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT pr_id FROM quiz WHERE q_title = %s AND us_id = %s',[name,session['user_id']])
        quiz_user_id = cur.fetchone()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM quiz_questions WHERE quiz_id = %s',[quiz_id['pr_id']])
        data = cur.fetchall()
        print(data)
        cur.close()
        for row in data:
            cur1 = mysql.connection.cursor()
            cur1.execute('SELECT ans FROM quiz_user_answer WHERE question_id = %s AND user_id = %s',[row['id'],session['user_id']])
            user_answer = cur1.fetchone()
            cur1.close()
            cur2 = mysql.connection.cursor()
            cur2.execute('SELECT ans FROM quiz_question_options WHERE question_id = %s',[row['id']])
            actual_answer = cur2.fetchone()
            cur2.close()
            if(user_answer == actual_answer):
                score += 1
                cur = mysql.connection.cursor()
                cur.close()
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO scoreboard(score,quiz_id,user_id) VALUES(%s, %s, %s)',[score,quiz_user_id['pr_id'],session['user_id'],])
        mysql.connection.commit()
        cur.close()
        return render_template('submit.html',score = score)



class registerform(Form):
    username = StringField('UserName',[validators.Length(min=1,max=50)])
    email = StringField('Email-ID',[validators.Length(min=1,max=100)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.Length(min=8,max=80),
        validators.EqualTo('confirm',message='Passwords do not match')
    ])
    confirm  = PasswordField('Confirm Password')








if(__name__ == '__main__'):
    app.secret_key = 'secret123'
    app.run(debug=True)
