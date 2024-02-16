from flask import Flask, flash, render_template, request, redirect, session
import mysql.connector
import pymysql


app = Flask(__name__,template_folder='template')
app.secret_key = 'jw123'

def connect_to_database():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'car_db'
    }
    return mysql.connector.connect(**db_config)


def register_user(username, password, phoneno, email):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        #hashed_password = hash_password(password)

        insert_query = "INSERT INTO register (username, password, phoneno, email) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (username, password, phoneno, email))

        connection.commit()
        cursor.close()
        connection.close()

        print(f"User '{username}' registered successfully!")
        return True
    except Exception as e:
        print(f"Error during registration: {e}")
        return False

def login_user(username, password):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        select_query = "SELECT password FROM register WHERE username = %s"
        cursor.execute(select_query, (username,))
        result = cursor.fetchone()

        if result :
            stored_password = result[0]
            if password == stored_password:
                print("Login successful!")
                session['username'] = username
                return True
            else:
                print("Incorrect password.")
        else:
            print("User not found.")

        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error during login: {e}")
        return False
    
def reg_details(date, car_model,actual_amount, selling_amount, car_remains):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        #hashed_password = hash_password(password)

        insert_query = "INSERT INTO car_details (date, car_model, actual_amount, selling_amount, car_remains) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (date, car_model, actual_amount, selling_amount, car_remains))

        connection.commit()
        cursor.close()
        connection.close()

        print(f"Details stored successfully!")
        return True
    except Exception as e:
        print(f"Error during registration: {e}")
        return False
        
default_username = "admin"
default_password = "password"


@app.route('/')
def front_page():
    return render_template('front_page.html')   

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phoneno = request.form['phoneno']
        email = request.form['email']
        
        # Register the user
        if register_user(username, password, phoneno, email):
            return redirect('/login')
        

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Login the user
        if login_user(username, password):
            return redirect('/home')

    return render_template('login.html')


@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        provided_username = request.form.get('username')
        provided_password = request.form.get('password')

        # Check if provided credentials match the default ones
        if provided_username == default_username and provided_password == default_password:
            # Perform any additional login logic if needed
            return redirect('/display_details')
        else:
            # Handle invalid login
            return render_template('admin_login.html', error="Invalid credentials")

    # For GET request, render the login form
    return render_template('admin_login.html', username=default_username, password=default_password)
    
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        date=request.form['date']
        carmodel = request.form['carmodel']
        actualamount = request.form['actualamount']
        sellingamount = request.form['sellingamount']
        car_remain = request.form['car_remain']
        
        success = reg_details(date, carmodel, actualamount, sellingamount, car_remain)

        if success:
            flash('Registered successfully!', 'success')
            return redirect('/home')
        else:
            flash('Error during registration. Please try again.', 'error')

    return render_template('home.html')


@app.route('/display_details',methods=["GET"])
def display_details():
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        search_query = request.args.get('search_query', default='', type=str)
               
        select_query = f"SELECT * FROM car_details WHERE car_model LIKE '%{search_query}%' COLLATE utf8mb4_bin"
        
        select_query = f"SELECT * FROM car_details WHERE date LIKE '%{search_query}%' COLLATE utf8mb4_bin"
        
        select_query = f"SELECT * FROM car_details WHERE car_remains LIKE '%{search_query}%' COLLATE utf8mb4_bin"
              
            #select_query = "SELECT * FROM car_details"
        cursor.execute(select_query)
        car_detail = cursor.fetchall()

        cursor.close()
        connection.close()
        
        print("Car Details:", car_detail)
        
        return render_template('display_details.html', car_detail=car_detail)
    
    except pymysql.Error as e:
        
        print(f"Error in fetching details: {e}")

        return render_template('error.html',error_message="Error fetching billing details")

if __name__ == '__main__':
    app.run(debug=True)
