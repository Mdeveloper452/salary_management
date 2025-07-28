from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table,TableStyle
from flask import send_file
from mysql.connector import connection
from db import db_connection
from io import BytesIO
from dotenv import load_dotenv
import os

from flask import send_from_directory
load_dotenv()
app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        emp_Id = request.form['emp_Id']
        username = request.form['username']
        password = request.form['password']
      # hashed_password = hashlib.sha256(password.encode()).hexdigest()
       #print(f"Received: emp_Id={emp_Id}, username={username}")
        test_db=db_connection()
        cursor=test_db.cursor()
        cursor.execute("SELECT * FROM users WHERE emp_Id = %s", (emp_Id,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("Employee ID already exists. Try a different one.", 'danger')
            return redirect(url_for('register'))

        cursor.execute("INSERT INTO users(emp_Id, username, password) VALUES (%s, %s, %s)", (emp_Id, username, password))
        test_db.commit()

        cursor.close()
        test_db.close()
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Testing login")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
      # hashed_password = hashlib.sha256(password.encode()).hexdigest()
        test_db = db_connection()
        print(username)
        print(password)
        cursor = test_db.cursor()
        print("Testing login if")
        cursor.execute("SELECT * FROM users WHERE  username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        test_db.close()
        print(user)
        if user:
            print("True")
            session['username'] = username
            #flash("Login Successful!", "success")
            #print("testflash")
            return redirect(url_for('dashboard'))
            
        else:
            print("false")
            flash("Invalid Employee ID or Password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    print("connection done")
    
    return render_template('dashboard.html')

@app.route('/pis_form', methods=['GET', 'POST'])
def pis_form():
    if request.method =='POST':
        emp_Id= request.form['emp_Id']
        name= request.form['name']
        deptt= request.form['deptt']
        category= request.form['category']
        desgg=request.form['desgg']
        sex= request.form['sex']
        pwd=request.form['pwd']
        dob=request.form['dob']
        dateofjoining=request.form['dateofjoining']
        dateofleaving=request.form['dateofleaving']
        panno=request.form['panno']
        aadharno=request.form['aadharno']
        basicpay=request.form['basicpay']
        hraadmissable=request.form['hraadmissable']
        bankaccountno=request.form['bankaccountno']
        bankaccountcode=request.form['bankaccountcode']
        ifsccode=request.form['ifsccode']
        status=request.form['status']
        print("TESTING PIS")
        test_db=db_connection()
        cursor=test_db.cursor()
        cursor.execute("INSERT INTO pis (emp_Id, name, deptt, category, desgg, sex, pwd,dob, dateofjoining, dateofleaving, panno, aadharno, basicpay, hraadmissable, bankaccountno, bankaccountcode, ifsccode, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(emp_Id,name,deptt,category,desgg,sex,pwd,dob,dateofjoining,dateofleaving,panno,aadharno,basicpay,hraadmissable,bankaccountno,bankaccountcode,ifsccode,status))
        test_db.commit()
        cursor.close()
        test_db.close()
        flash(" PIS details saved successfully ", "success")
        return redirect(url_for('dashboard'))
    return render_template('pis_form.html')

@app.route('/get_department_name', methods=['GET'])
def get_department_name():
    dept_code =request.args.get('deptt', '')
    print(f"Recieved department code: {dept_code}")
    test_db=db_connection()
    cursor=test_db.cursor()
    cursor.execute("SELECT depttname FROM departments WHERE deptt = %s",(dept_code,))
    result=cursor.fetchone()
    cursor.close()
    test_db.close()
    print(f"Query result: {result}")

    if result:
        return jsonify({'depttname': result[0]})
    else:
        return jsonify({'depttname': 'Invalid Code'})

@app.route('/get_designation_name', methods=['GET'])
def get_designation_name():
    desg_code=request.args.get('desgg','')
    print(f"recieved designation code: {desg_code}")
    test_db=db_connection()
    cursor=test_db.cursor()
    cursor.execute("SELECT desggname FROM designation WHERE desgg = %s", (desg_code,))
    result=cursor.fetchone()
    cursor.close()
    test_db.close()
    print(f"Query result:{result}")
    if result:
        return jsonify({'desggname': result[0]})
    else:
        return jsonify({"error": "invalid code"})

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/get_employee/<emp_Id>')
def get_employee(emp_Id):
    test_db=db_connection()
    cursor=test_db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pis WHERE emp_Id =%s", (emp_Id,))
    employee=cursor.fetchone()
    test_db.close()
    if employee:
        return jsonify(employee)

    return jsonify({"error": "Employee not found"})
    

@app.route('/get_department/<deptt>')
def get_department(deptt):
    status_filter = request.args.get('status')
    test_db=db_connection()
    cursor=test_db.cursor(dictionary=True)
    cursor.execute("SELECT depttname FROM departments WHERE deptt = %s", (deptt,))
    department=cursor.fetchone()
    if not department:
        return jsonify({"error": "Invalid department code"})
    dept_name = department["depttname"]
    employees=[]
    if status_filter =='all':
        cursor.execute("SELECT emp_Id, name FROM pis WHERE deptt = %s", (deptt,))
        employees=cursor.fetchall()
    elif status_filter =='available':
        cursor.execute("SELECT emp_Id, name  FROM pis WHERE deptt=%s AND status ='available'", (deptt,))
        employees=cursor.fetchall()
    elif status_filter =='retired':
        cursor.execute("SELECT emp_Id, name   FROM pis WHERE deptt =%s AND status='retired'", (deptt,))
        employees=cursor.fetchall()
    elif status_filter=='suspend':
        cursor.execute("SELECT emp_Id,name FROM pis WHERE deptt = %s AND status='suspend'", (deptt,))
        employees=cursor.fetchall()
        print("if statement compile successful")
    
    print("fetched employee", employees)
    cursor.close()
    test_db.close()
    print(f"Retired employess: {employees}")
    return jsonify({"dept_name": dept_name, "employees": employees})



    

@app.route('/get_designation/<desgg>')
def get_designation(desgg):
    status_filter= request.args.get("status", "all")
    test_db=db_connection()
    cursor=test_db.cursor(dictionary=True)
    cursor.execute("SELECT desggname FROM designation WHERE desgg =%s", (desgg,))
    desg_name=cursor.fetchone()
    if not desg_name:
        return jsonify({"error": "Invalid designation code"})
    
    employees=[]
    if status_filter=='all':
        cursor.execute("SELECT emp_Id, name FROM pis WHERE desgg = %s", (desgg,))
  
    elif status_filter=='available':
        cursor.execute("SELECT emp_Id, name FROM pis WHERE desgg =%s AND status ='available", (desgg,))

    elif status_filter=='retired':
        cursor.execute("SELECT emp_Id, name FROM pis WHERE desgg =%s AND  status ='retired'",(desgg,))

    elif status_filter=='suspend':
        cursor.execute("SELECT emp_Id, name FROM pis WHERE desgg =%s AND status ='suspend'",(desgg,))
    employees= cursor.fetchall()
    cursor.close()
    test_db.close()
    return jsonify({"desg_name": desg_name["desggname"], "employees": employees})

@app.route('/salary_form', methods=['GET', 'POST'])
def salary_form():
    employee_data = None  # This will hold the fetched employee data if available
    pdf_download_link = None  # Initialize a variable to hold the link for the generated PDF


    if request.method == 'POST':
        action = request.form.get('action')
        # Collect the data from the form
        emp_Id = request.form.get('emp_Id')
        if not emp_Id:
            flash("employee id is missing", "danger")
            return redirect(url_for('salary_form'))
        basicpay = float(request.form['basicpay'])
        netbasicpay = float(request.form['netbasicpay'])
        hra = float(request.form['hra'])
        month = request.form['month']
        year = request.form['year']
        #otherearning = request.form['otherearning']
        #deduction = request.form['deduction']
        netpay = request.form['netpay']
        absentdays = request.form['absentdays']
        remainingleave = request.form['remainingleave']
        name = request.form['name']
        deptt = request.form['deptt']
        bankaccountno = request.form['bankaccountno']
        depttname = request.form['depttname']  # Retrieve depttname from the form

          # Initialize lists for deductions and other earnings
        #deductions = []  # List to store all deductions
        #other_earnings = []  # List to store all other earnings
        if action =="preview":
            return generate_salary_slip(emp_Id, name, depttname, basicpay,netbasicpay, hra, month, year, netpay, absentdays, remainingleave, bankaccountno,deductions=[], other_earnings=[])
        
         # If user clicked "Save to Database"
        if action == "save":
            test_db = db_connection()
            cursor = test_db.cursor()



        total_deduction =0
        total_other_earning=0

        # Insert the salary details into the salary table
        test_db = db_connection()
        cursor = test_db.cursor()
         # Check if a record already exists for the given emp_Id, month, and year
        cursor.execute("""
            SELECT * FROM salary
            WHERE emp_Id = %s AND month = %s AND year = %s
        """, (emp_Id, month, year))
        existing_record = cursor.fetchone()

        if existing_record:
            # If an existing record is found, delete it
            cursor.execute("""
                DELETE FROM salary
                WHERE emp_Id = %s AND month = %s AND year = %s
            """, (emp_Id, month, year))
            test_db.commit()

             # Calculate deductions
        deductions=[]
        deduction_count = int(request.form.get('deductionCount', 0))
        for i in range(1, deduction_count + 1):
            deduction_code = request.form.get(f'deduction_code_{i}')
            deduction_amount = float(request.form.get(f'deduction_amount_{i}', 0))
            deductions.append((deduction_code, deduction_amount))
            total_deduction +=deduction_amount
            cursor.execute("""
                    INSERT INTO deductions (emp_Id, deduction_code, deduction_amount)
                    VALUES (%s, %s, %s)
                """, (emp_Id, deduction_code, deduction_amount))

        # Calculate other earnings
        other_earnings=[]
        otherearning_count = int(request.form.get('otherearningCount', 0))  # Get other earnings count
        for i in range(1, otherearning_count + 1):
            otherearning_code = request.form.get(f'otherearning_code_{i}')
            otherearning_amount = float(request.form.get(f'otherearning_amount_{i}', 0))
            # Ensure other earning details are added to the list
            other_earnings.append((otherearning_code, otherearning_amount))
            # Add the amount to total other earnings
            total_other_earning += otherearning_amount
            # Insert each other earning into the database
            cursor.execute("""
                           INSERT INTO otherearnings (emp_Id, other_earning_code, other_earning_amount)
                           VALUES (%s, %s, %s)
                           """, (emp_Id, otherearning_code, otherearning_amount))
            # After all earnings are inserted, proceed with your calculations
            netpay = netbasicpay + hra + total_other_earning - total_deduction

            if action == "preview":
                return generate_salary_slip(
                emp_Id, name, depttname, basicpay, netbasicpay, hra, month, year,
                netpay, absentdays, remainingleave, bankaccountno
            )
            elif action == "save":
                test_db = db_connection()
            cursor = test_db.cursor()

            # Insert the final salary record into the database
            cursor.execute("""
                           INSERT INTO salary (emp_Id, name, deptt, depttname, basicpay, netbasicpay, hra, month, year, 
                           otherearning, deduction, netpay, absentdays, remainingleave, bankaccountno)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """, (emp_Id, name, deptt, depttname, basicpay, netbasicpay, hra, month, year, 
                                 total_other_earning, total_deduction, netpay, absentdays, remainingleave, bankaccountno))
            test_db.commit()
            cursor.close()
            test_db.close()
            flash("Salary details saved successfully.", "success")
            return render_template('dashboard.html', pdf_download_link=pdf_download_link)


 # Check if it's a GET request and emp_Id is passed
    if request.method == 'GET' and 'emp_Id' in request.args:
        emp_Id = request.args['emp_Id']
        test_db = db_connection()
        cursor = test_db.cursor(dictionary=True)

        # Fetch employee data from pis table
        cursor.execute("""
            SELECT pis.name, pis.deptt, pis.basicpay, pis.bankaccountno
            FROM pis
            WHERE pis.emp_Id = %s
        """, (emp_Id,))
        employee_data = cursor.fetchone()  # Get the first matching employee

        # Fetch department name from departments table using deptt code
        if employee_data:
            deptt = employee_data['deptt']
            cursor.execute("""
                SELECT depttname
                FROM departments
                WHERE deptt = %s
            """, (deptt,))
            depttname = cursor.fetchone()

            # Add depttname to employee data if found
            if depttname:
                employee_data['depttname'] = depttname['depttname']
            else:
                employee_data['depttname'] = 'Unknown'

        cursor.close()
        test_db.close()

        # If no employee found, return error or handle accordingly
        if not employee_data:
            flash("Employee not found.", "danger")
            return redirect(url_for('dashboard'))  # Redirect to a safer page
    


    return render_template('salary_form.html', employee_data=employee_data)

def generate_salary_slip(emp_Id, name, depttname, basicpay, netbasicpay, hra, month, year, netpay, absentdays, 
                          remainingleave, bankaccountno, deductions=None, other_earnings=None):
    
    # Set default empty lists if None is passed
    if deductions is None:
        deductions = []
    if other_earnings is None:
        other_earnings = []


    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 50, f"Salary Slip - {month} {year}")

        # Employee Info
    c.setFont("Helvetica", 10)
    y = height - 90
    line_gap = 15

    info = [
            f"Employee ID: {emp_Id}",
            f"Name: {name}",
            f"Department: {depttname}",
            f"Bank Account: {bankaccountno}",
            f"Absent Days: {absentdays}",
            f"Remaining Leave: {remainingleave}",
        ]

    for item in info:
            c.drawString(50, y, item)
            y -= line_gap

        # Salary Table
    salary_data = [
            ["Component", "Amount (₹)"],
            ["Basic Pay", f"{float(basicpay):.2f}"],
            ["Net Basic Pay", f"{float(netbasicpay):.2f}"],
            ["HRA", f"{float(hra):.2f}"],
            ["Net Pay", f"{float(netpay):.2f}"]
        ]

    table = Table(salary_data, colWidths=[200, 120])
    table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, y - 120)

    # Other Earnings Table
    if other_earnings:
        c.drawString(50, y, "Other Earnings:")
        y -= line_gap
        earnings_data = [["Earning Type", "Amount (₹)"]] + [
            [str(code), f"{float(amount):.2f}"] for code, amount in other_earnings
        ]
        earnings_table = Table(earnings_data, colWidths=[200, 120])
        earnings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        earnings_table.wrapOn(c, width, height)
        earnings_table.drawOn(c, 50, y - 100)
        y -= 140

    # Deductions Table
    if deductions:
        c.drawString(50, y, "Deductions:")
        y -= line_gap
        deductions_data = [["Deduction Type", "Amount (₹)"]] + [
            [str(code), f"{float(amount):.2f}"] for code, amount in deductions
        ]
        deductions_table = Table(deductions_data, colWidths=[200, 120])
        deductions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        deductions_table.wrapOn(c, width, height)
        deductions_table.drawOn(c, 50, y - 100)


        # Finalize PDF
    c.showPage()
    c.save()

    buffer.seek(0)
    filename = f"salary_slip_{emp_Id}_{month}_{year}.pdf"

    return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    




@app.route('/fetch_employee', methods=['GET'])
def fetch_employee():
    emp_id = request.args.get('emp_Id')  # Get the employee ID from query parameters
    if emp_id:
        test_db=db_connection()
        cursor = test_db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pis WHERE emp_Id = %s", (emp_id,))
        employee_data = cursor.fetchone()
        if employee_data:
            dept_code=employee_data.get('deptt')
            cursor.execute("SELECT depttname FROM departments WHERE deptt=%s" ,(dept_code,))
            department_data=cursor.fetchone()
            if department_data:
                employee_data['depttname'] = department_data['depttname']
            else:
                employee_data['depttname'] = 'Department not found'
        cursor.close()
        test_db.close()
        return jsonify(employee_data)
    else:
        cursor.close()
        test_db.close()
        return jsonify({'error': 'Employee not found'}), 404



@app.route('/logout')
def logout():
   if session.pop('username', None):
    flash("Logged out successfully", "success")
   return render_template('logout.html')




if __name__ == '__main__':
    app.run(debug=True)
