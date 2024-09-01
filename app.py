import mysql.connector
from flask import Flask,request,render_template,redirect,url_for, session
import re,datetime,time

current_time = datetime.datetime.now()
time_diff = 0

app = Flask(__name__)
app.secret_key = "nurav"
conn = mysql.connector.connect(host = 'localhost',user= 'root',password= 'nps@1234',database= 'parking_system') 
cursor = conn.cursor()

@app.route('/home',methods=['GET'])
def index():
    #home page showing available spots
    conn = mysql.connector.connect(host = 'localhost',user= 'root',password= 'nps@1234',database= 'parking_system')
    cursor = conn.cursor()
    cursor.execute('Select spot_number from parking_spots where status = "available"')
    data = cursor.fetchall()
    print("hello")
    
    cursor.execute('Select spot_number from parking_spots where status = "booked" AND user_id= %s',(session['id'],))
    booked = cursor.fetchall()
    #print("Available spots", list(data))
    return render_template('home.html',available_spots =data, booked_spots=booked)
    cursor.close()
    conn.close()


@app.route('/book_spot', methods=['POST'])
def book_spot():
    #accepting user input 
    if request.method =='POST':
        session['spot_number']= request.form['spot_number']
        session['from_date'] = request.form['from_date_time']
        session['to_date'] = request.form['to_date_time']
        
    
        conn = mysql.connector.connect(host = 'localhost',user= 'root',password= 'nps@1234',database= 'parking_system')
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM parking_spots WHERE spot_number = %s", (session['spot_number'],))
        result = cursor.fetchone()
      
    
    
        if result:
            
            cursor.execute("UPDATE parking_spots SET status = 'booked' ,user_id =%s , from_booking_time = %s , to_booking_time = %s WHERE spot_number = %s ", (session['id'],session['from_date'],session['to_date'],session['spot_number']))
            conn.commit()
            message = 'Spot booked successfully!'
            
            cursor.execute("SELECT TIMEDIFF(from_booking_time, to_booking_time) AS time_difference FROM parking_spots where spot_number = %s", (session['spot_number'],))
            global time_diff
            time_diff = cursor.fetchone()
            print(time_diff)

         
        
    else:
        message = 'Spot is occupied or not found'
    return render_template('book_spot.html',message=message)


    


#login
@app.route('/',methods=['GET','POST'])
def login():
    msg=''
    session['loggedin'] = False
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = mysql.connector.connect(host = 'localhost',user= 'root',password= 'nps@1234',database= 'parking_system')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            print(account[3])
            session['id'] = int(account[0])
            session['user'] = account[3]
            session['firstname']=account[1]
            
            msg = 'Logged in successfully !'
            print(session)
            #return render_template('home.html', msg=msg)
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

        

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    session['loggedin'] = False
    if request.method == 'POST':
        username = request.form['firstName']
        password1 = request.form['password1']
        password2 = request.form['password2']
        email = request.form['email']

        conn = mysql.connector.connect(host = 'localhost',user= 'root',password= 'nps@1234',database= 'parking_system')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM accounts WHERE email = %s', (email, ))
        account = cursor.fetchone()
     
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        elif password1 != password2:
            msg = 'confirmation password does not match!'
        else:
            cursor.execute('INSERT INTO accounts(username, password, email) VALUES \
            ( %s, %s, %s)',
                           (username, password1, email))

            conn.commit()
            msg = 'You have successfully registered !'
            return redirect(url_for('login'))
    elif request.method == 'GET':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)
 
@app.route('/logout')
def logout():
    session['loggedin'] = False
    return redirect(url_for('login'))
    
    

if __name__ == '__main__':
    app.run(debug=True)


cursor.close()
conn.close()

'''time.sleep(time_diff)
conn = mysql.connector.connect(host = 'localhost',user= 'root',password= 'nps@1234',database= 'parking_system')
cursor = conn.cursor()
cursor.execute('update status ="available",from_booking_time = "NULL", to_booking_time = "NULL" FROM accounts WHERE userid', (session[id], ))

'''
