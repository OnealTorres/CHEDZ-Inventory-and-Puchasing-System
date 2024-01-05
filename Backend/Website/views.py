from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify, abort, send_file
import psycopg2
from psycopg2 import extras, Binary
from configparser import ConfigParser
from .validation import *
from datetime import date, timedelta
import os
from io import BytesIO
from functools import wraps

views = Blueprint('views', __name__)
# Configuration
config = ConfigParser()

# Read the config.ini file
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config.read(config_path)

#database connection
conn = psycopg2.connect(
    host=config.get('conn', 'host'),
    port=config.get('conn', 'port'),
    database=config.get('conn', 'database'),
    user=config.get('conn', 'user'),
    password=config.get('conn', 'password')
)

# Decorator to check if the user is logged in or is admin
def login_required(f):
    @wraps(f)
    def wrapped_view(*args, **kwargs):
        # Check if the user is logged in
        if not session.get('emp_id'):
            return redirect('/')
        # Call the original route function
        return f(*args, **kwargs)
    return wrapped_view

def admin_required(f):
    @wraps(f)
    def wrapped_admin(*args, **kwargs):
        # Check if the user is logged in
        if not session.get('emp_id'):
            return redirect('/')

        is_admin = True if session.get('emp_type') == 'ADMIN' else False
        # Check if the user is an admin
        if not is_admin:
            return "<h1><strong>Forbidden Access</strong></h1>"
        # Call the original route function
        return f(*args, **kwargs)
    return wrapped_admin

#===============================
#              HOME
#===============================

@views.route('/home', methods=['GET','POST'])
@login_required
def home():
    # items_count = 0
    # employees_count = 0
    # near_expiry_count = 0
    # expired_count = 0 
    
    emp_data = get_employee(session['emp_id'])
    
    all_count =[0,0,0,0]
    recent = None
    
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) as items FROM ITEM;")
    rows = cur.fetchone()
    
    if (rows):
        all_count[0] = rows['items']
        
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) as employees FROM EMPLOYEE WHERE emp_status = 'Active';")
    rows = cur.fetchone()
    
    if (rows):
        all_count[1] = rows['employees']
    
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) as near_expiry FROM DELIVERED_ITEM WHERE di_quantity != di_deducted AND di_expiry < (CURRENT_DATE + INTERVAL '15 days');")
    rows = cur.fetchone()
    
    if (rows):
        all_count[2] = rows['near_expiry']
    
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) as expired FROM DELIVERED_ITEM WHERE di_quantity != di_deducted AND di_expiry <= CURRENT_DATE ;")
    rows = cur.fetchone()
    
    if (rows):
        all_count[3] = rows['expired']
    
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM ITEM LEFT JOIN UNIT USING (unit_id) LEFT JOIN DELIVERED_ITEM USING (item_id) WHERE di_quantity != di_deducted ORDER BY(DELIVERED_ITEM.date_created) DESC LIMIT 10;")
    rows = cur.fetchall()
    
    if (rows):
        recent = rows
    cur.close()
  
    return render_template('home.html', counter = all_count, recent_added = recent, account = emp_data)

#===============================
#           INVENTORY
#===============================

@views.route('/inventory', methods=['GET','POST'])
@login_required
def inventory():
    all_units = None
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM UNIT;")
    rows = cur.fetchall()
    if(rows):
        all_units = rows

    current_inventory = None
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT ITEM.item_id, item_name, item_type, item_reorder_lvl, UNIT.unit_name, COALESCE(SUM(DELIVERED_ITEM.di_quantity - di_deducted), 0) AS total_quantity FROM ITEM LEFT JOIN UNIT ON ITEM.unit_id = UNIT.unit_id LEFT JOIN DELIVERED_ITEM ON ITEM.item_id = DELIVERED_ITEM.item_id AND (DELIVERED_ITEM.di_expiry > CURRENT_DATE OR DELIVERED_ITEM.di_expiry IS NULL) AND (DELIVERED_ITEM.di_quantity != DELIVERED_ITEM.di_deducted OR DELIVERED_ITEM.di_quantity IS NULL) GROUP BY ITEM.item_id, ITEM.item_name, item_type, item_reorder_lvl, UNIT.unit_name ORDER BY total_quantity DESC;")
    rows = cur.fetchall()
    if(rows):
        current_inventory = rows
    cur.close()
    emp_data = get_employee(session['emp_id'])
    return render_template('inventory.html', inventory = current_inventory, units = all_units, account = emp_data)

@views.route('/inventory/near-expiry', methods=['GET','POST'])
@login_required
def inventoryExpiry():
    all_units = None
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM UNIT;")
    rows = cur.fetchall()
    if(rows):
        all_units = rows
    
    expiring_inventory = None
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM ITEM LEFT JOIN UNIT USING (unit_id) LEFT JOIN DELIVERED_ITEM USING (item_id) WHERE  di_quantity != di_deducted AND di_expiry >= CURRENT_DATE AND di_expiry < CURRENT_DATE + INTERVAL '15 days'  ORDER BY(di_expiry);")
    rows = cur.fetchall()
    if(rows):
        expiring_inventory = rows
    cur.close()
    emp_data = get_employee(session['emp_id'])
    return render_template('inventory-nearly-expired.html',  expiring = expiring_inventory, units = all_units, account = emp_data)

@views.route('/inventory/add-item', methods=['GET','POST'])
@admin_required
def inventoryAddItem():
    if request.method == 'POST':
        data = request.json 
        if add_item(data['item_name']):
            #checks if the item is already in db
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT * FROM ITEM WHERE item_name = '"+data['item_name']+"';")
            rows = cur.fetchall()
            if(rows):
                abort(404)
            #insert the new item
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("INSERT INTO ITEM (item_name, item_type, item_reorder_lvl, unit_id) VALUES ('"+data['item_name']+"', '"+data['item_type']+"', "+str(data['item_reorder_lvl'])+", "+str(data['unit_id'])+") ;")
            conn.commit()
            cur.close()
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    abort(404)

@views.route('/inventory/update-item/<int:item_id>' , methods=['GET','POST'])
@login_required
def inventoryUpdateItem(item_id):
    if request.method == 'GET':
        item_data = None
        delivered_items = None
        new_date = date.today() + timedelta(days=15)
        #takes the specific item on db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM ITEM WHERE item_id = "+str(item_id)+" ;")
        rows = cur.fetchall()
        
        if(rows):
            item_data = rows
        else:
            abort(404)
        
        #takes the quantity in delivered items on db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM DELIVERED_ITEM WHERE item_id = "+str(item_id)+" AND (di_quantity > di_deducted OR di_quantity IS NULL) AND (di_expiry > CURRENT_DATE OR di_expiry IS NULL) ;")
        rows = cur.fetchall()
        
        if(rows):
            delivered_items = rows
            
        all_units = None
        #takes all the units
        cur = conn.cursor(cursor_factory=extras.RealDictCursor) 
        cur.execute("SELECT * FROM UNIT;")
        rows = cur.fetchall()
        cur.close()
        if(rows):
            all_units = rows
        emp_data = get_employee(session['emp_id'])
        return render_template('inventory-update.html', units = all_units, item = item_data, delivered = delivered_items, date = new_date, account = emp_data), 200
    
    elif request.method == 'POST':
        data = request.json 
        if update_item(data['item_name']):
            #updates the specified item
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("UPDATE ITEM SET item_name ='"+data['item_name']+"',  item_type = '"+data['item_type']+"',  item_reorder_lvl = "+str(data['item_reorder_lvl'])+", unit_id = "+str(data['unit_id'])+" WHERE item_id = "+str(item_id)+" ;")
            conn.commit()
            cur.close()
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    abort(404)    

@views.route('/inventory/search/<searched_data>', methods=['GET','POST'])
@login_required
def inventorySearch(searched_data):
    if request.method == 'GET':
        all_inventory = None
        all_units = None
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM UNIT;")
        rows = cur.fetchall()
        if(rows):
            all_units = rows
        
        #searches the item on db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT ITEM.item_id, item_name, item_type, item_reorder_lvl, UNIT.unit_name, COALESCE(SUM(DELIVERED_ITEM.di_quantity - di_deducted), 0) AS total_quantity FROM ITEM LEFT JOIN UNIT ON ITEM.unit_id = UNIT.unit_id LEFT JOIN DELIVERED_ITEM ON ITEM.item_id = DELIVERED_ITEM.item_id WHERE item_name LIKE '%"+searched_data+"%' AND (DELIVERED_ITEM.di_expiry > CURRENT_DATE OR DELIVERED_ITEM.di_expiry IS NULL) AND (di_quantity != di_deducted OR di_quantity IS NULL) GROUP BY ITEM.item_id, ITEM.item_name, item_type, item_reorder_lvl, UNIT.unit_name ORDER BY(total_quantity) DESC;;")
        rows = cur.fetchall()
        cur.close()
        if(rows):
            all_inventory = rows
        emp_data = get_employee(session['emp_id'])
        return render_template('inventory.html', inventory = all_inventory, units = all_units, account = emp_data)
    abort(404)
        
#===============================
#           EMPLOYEE            
#===============================

@views.route('/employee', methods=['GET','POST'])
@admin_required
def employee():
    all_employees = None
    #gets all the employee from the db
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM EMPLOYEE;")
    rows = cur.fetchall()
    cur.close()
    if(rows):
        all_employees = rows
    emp_data = get_employee(session['emp_id'])
    return render_template('employees.html', employees = all_employees, account = emp_data)

@views.route('/employee/add-employee', methods=['GET','POST'])
@admin_required
def employeeAdd():
    if request.method == 'POST':
        data = request.json 
   
        if emp_register(data['emp_fname'],data['emp_mname'],data['emp_lname'],data['emp_email'],data['emp_password']):
            #checks if the employee is already on the database
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT * FROM EMPLOYEE WHERE emp_email='"+data['emp_email']+"' OR (emp_fname = '"+data['emp_fname']+"' AND emp_mname = '"+data['emp_lname']+"' AND emp_lname = '"+data['emp_fname']+"' );")
            rows = cur.fetchall()
            cur.close()
            if (rows):
                abort(404)
            
            #inserts the new employee on the database 
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("INSERT INTO EMPLOYEE (emp_fname, emp_mname, emp_lname, emp_email, emp_password, emp_type) VALUES ( '"+data['emp_fname'].title()+"', '"+data['emp_mname'].title()+"','"+data['emp_lname'].title()+"','"+data['emp_email']+"', '"+data['emp_password']+"','"+data['emp_type']+"');")
            conn.commit()
            cur.close()    
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    abort(404)    

@views.route('/employee/update-employee/<int:emp_id>', methods=['GET','POST'])
@admin_required
def employeeUpdate(emp_id):
    if request.method == 'GET':
        employee_data = None
        #gets the employee information in db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM EMPLOYEE WHERE emp_id = "+str(emp_id)+" ;")
        rows = cur.fetchone()
        cur.close()
        if (rows):
            employee_data = rows
        emp_data = get_employee(session['emp_id'])
        return render_template('employee-update.html', employee = employee_data, account = emp_data), 200
    
    elif request.method == 'POST':
        data = request.json
        if emp_register(data['emp_fname'],data['emp_mname'],data['emp_lname'],data['emp_email'],data['emp_password']):
            #checks if the employee is already on the database
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT * FROM EMPLOYEE WHERE (emp_email='"+data['emp_email']+"' AND emp_id != "+str(emp_id)+") OR (emp_fname = '"+data['emp_fname']+"' AND emp_mname = '"+data['emp_lname']+"' AND emp_lname = '"+data['emp_fname']+"' );")
            rows = cur.fetchall()
            cur.close()
            if (rows):
                abort(404)
            
           #updates the specified employee
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("UPDATE EMPLOYEE SET emp_fname ='"+data['emp_fname'].title()+"',  emp_mname = '"+data['emp_mname'].title()+"', emp_lname = '"+data['emp_lname'].title()+"', emp_email = '"+data['emp_email']+"', emp_password = '"+data['emp_password']+"', emp_status = '"+data['emp_status']+"', emp_type = '"+data['emp_type']+"' WHERE emp_id = "+str(emp_id)+" ;")
            conn.commit()
            cur.close()
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    abort(404)

@views.route('/employee/search/<searched_data>' , methods=['GET','POST'])
@admin_required
def employeeSearch(searched_data):
    if request.method == 'GET':
        emp_data = None
        #searches the employee on db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM EMPLOYEE WHERE emp_fname LIKE '%"+searched_data+"%' OR emp_mname LIKE '%"+searched_data+"%' OR emp_lname LIKE '%"+searched_data+"%' OR emp_email LIKE '%"+searched_data+"%' ;")
        rows = cur.fetchall()
        cur.close()
        if(rows):
            emp_data = rows
        emp = get_employee(session['emp_id'])
        return render_template('employees.html', employees = emp_data,account = emp), 200
    abort(404)

#===============================
#            VENDOR
#===============================

@views.route('/vendors', methods=['GET','POST'])
@admin_required
def vendor():
    all_vendors = None
    #gets all the vendors from the db
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM VENDOR;")
    rows = cur.fetchall()
    if(rows):
        all_vendors = rows
    emp_data = get_employee(session['emp_id'])
    return render_template('vendors.html', vendors = all_vendors , account = emp_data)

@views.route('/vendors/add', methods=['GET','POST'])
@admin_required
def vendorAdd():
    if request.method == 'POST':
        data = request.json 
        if add_vendor(data['vnd_name'],data['vnd_contact'],data['vnd_email']):
            #checks if the vendor is already on the database
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT * FROM VENDOR WHERE vnd_name='"+data['vnd_name']+"' OR vnd_contact='"+data['vnd_contact']+"' OR vnd_email='"+data['vnd_email']+"';")
            rows = cur.fetchall()
            if (rows):
                abort(404)
            
            #inserts the new vendor on the database 
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("INSERT INTO VENDOR (vnd_name, vnd_contact, vnd_email ) VALUES ( '"+data['vnd_name']+"', '"+data['vnd_contact']+"','"+data['vnd_email']+"');")
            conn.commit()
            cur.close()    
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    abort(404)    


@views.route('/vendors/update/<int:vnd_id>', methods=['GET','POST'])
@admin_required
def vendorUpdate(vnd_id):
    if request.method == 'GET':
        vendor_data = None
        #gets the vendor from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM VENDOR WHERE vnd_id = "+str(vnd_id)+" ;")
        rows = cur.fetchone()
        cur.close()
        if(rows):
            vendor_data = rows
        else:
            abort(404)
        emp_data = get_employee(session['emp_id'])
        return render_template('vendor-update.html', vendor = vendor_data, account = emp_data), 200
    
    elif request.method == 'POST':
        data = request.json
     
        if add_vendor(data['vnd_name'],data['vnd_contact'],data['vnd_email']):
            #checks if the vendor is already on the database
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT * FROM VENDOR WHERE (vnd_name='"+data['vnd_name']+"' OR vnd_contact='"+data['vnd_contact']+"' OR vnd_email='"+data['vnd_email']+"') AND vnd_id != "+str(vnd_id)+";")
            rows = cur.fetchall()
            if (rows):
                abort(404)
            
            #updates the specified vendor
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("UPDATE VENDOR SET vnd_name ='"+data['vnd_name']+"',  vnd_contact = '"+data['vnd_contact']+"', vnd_email = '"+data['vnd_email']+"' WHERE vnd_id = "+str(vnd_id)+" ;")
            conn.commit()
            cur.close() 
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    abort(404)

#===============================
#         REQUISITIONS
#===============================

@views.route('/requisitions', methods=['GET','POST'])
@login_required
def requisitions():
    all_requisitions = None
    # requisitions_count = 0
    # approved_count = 0
    # disapproved_count = 0
    # completed_count = 0
    all_count = [0,0,0,0]
    
    #queries
    if_employee_query = " AND emp_id = "+str(session.get('emp_id'))+" "
    
    #checks if user is admin
    is_admin = True if session.get('emp_type') == 'ADMIN' else False
    
    #gets the request count
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) FROM REQUEST WHERE 1 = 1"+ (if_employee_query if not is_admin else ""))
    rows = cur.fetchall()
    if (rows):
        all_count[0] = rows[0]['count']
        
    #gets the approved count
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) FROM REQUEST WHERE 1 = 1"+(if_employee_query if not is_admin else "")+" AND rq_status = 'Approved'" )
    rows = cur.fetchall()
    if (rows):
        all_count[1] = rows[0]['count']
    
    #gets the disapproved count
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) FROM REQUEST WHERE 1 = 1"+(if_employee_query if not is_admin else "")+" AND rq_status = 'Disapproved'" )
    rows = cur.fetchall()
    if (rows):
        all_count[2] = rows[0]['count']
        
    #gets the completed count
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) FROM REQUEST WHERE 1 = 1"+(if_employee_query if not is_admin else "")+" AND rq_status = 'Completed'" )
    rows = cur.fetchall()
    if (rows):
        all_count[3] = rows[0]['count']
    
    #gets all the request from the db
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT *, REQUEST.date_created as date_requested FROM REQUEST INNER JOIN EMPLOYEE USING (emp_id) WHERE 1 = 1"+ (if_employee_query if not is_admin else "") + " ORDER BY (REQUEST.date_created) DESC LIMIT 10")
    rows = cur.fetchall()
    cur.close()
    if(rows):
        all_requisitions = rows
    emp_data = get_employee(session['emp_id'])
    return render_template('requisition.html', requisitions = all_requisitions, counter = all_count, account = emp_data)
    
@views.route('/requisitions/all', methods=['GET','POST'])
@login_required
def requisitionsAll():
    all_requisitions = None
    #queries
    if_employee_query = " AND emp_id = "+str(session.get('emp_id'))+" "
    
    #checks if user is admin
    is_admin = True if session.get('emp_type') == 'ADMIN' else False
    
    #gets all the request from the db
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT *, REQUEST.date_created as date_requested FROM REQUEST INNER JOIN EMPLOYEE USING (emp_id) WHERE 1 = 1 "+(if_employee_query if not is_admin else "")+ " ORDER BY REQUEST.date_created DESC")
    rows = cur.fetchall()
    cur.close()
    if(rows):
        all_requisitions = rows
    emp_data = get_employee(session['emp_id'])
    return render_template('requisition-all.html', requisitions = all_requisitions, account = emp_data)

@views.route('/requisitions/all/search/<int:rq_id>', methods=['GET','POST'])
@login_required
def requisitionsAllSeach(rq_id):
    if request.method == 'GET':
        all_requisitions = None
        #queries
        if_employee_query = " AND emp_id = "+str(session.get('emp_id'))+" AND rq_id = "+str(rq_id)+" ;"
        if_admin_query = " AND rq_id = "+str(rq_id)+" ;"
        #checks if user is admin
        is_admin = True if session.get('emp_type') == 'ADMIN' else False
        
        #gets all the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, REQUEST.date_created as date_requested FROM REQUEST INNER JOIN EMPLOYEE USING (emp_id) WHERE 1 = 1"+ (if_employee_query if not is_admin else if_admin_query))
        rows = cur.fetchall()
        cur.close()
        if(rows):
            all_requisitions = rows
        emp_data = get_employee(session['emp_id'])
        return render_template('requisition-all.html', requisitions = all_requisitions, account = emp_data)
    abort(404)

@views.route('/requisitions/new-requisition/job', methods=['GET','POST'])
@login_required
def requisitionsNewJob():
    if request.method == 'GET':
        emp_data = get_employee(session['emp_id'])
        return render_template('requisition-create-job.html',employee = emp_data, account = emp_data)
    
    if request.method == 'POST':
        data = request.json
        if add_job(data['rq_desc']):
            #inserts the new requisition on the database 
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("INSERT INTO REQUEST (rq_type, rq_desc, emp_id) VALUES ( '"+data['rq_type']+"', '"+data['rq_desc']+"',"+str(session.get('emp_id'))+") RETURNING rq_id;")
            conn.commit()
            
            request_id = cur.fetchone()
            #inserts the new job requisition on the database 
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("INSERT INTO REQ_JOB (rq_id) VALUES ("+str(request_id['rq_id'])+");")
            conn.commit()
            cur.close()
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    abort(404)    

@views.route('/requisitions/update-requisition/job/<int:rq_id>', methods=['GET','POST'])
@login_required
def requisitionsUpdateJob(rq_id):
    if request.method == 'GET':
        job_request = None
        
        #gets the employee id from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM EMPLOYEE INNER JOIN REQUEST USING(emp_id) WHERE rq_id ="+str(rq_id)+";")
        rows = cur.fetchone()
        cur.close()
        if not rows:
            abort(404)
        emp_data = get_employee(rows['emp_id'])
        
        #gets the job from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM REQUEST WHERE rq_id ="+str(rq_id)+"")
        rows = cur.fetchone()
        cur.close()
        if rows:
            job_request = rows
            
        emp = get_employee(session['emp_id'])
        return render_template('requisition-job-update.html',job = job_request, employee = emp_data, account = emp)
    
    elif request.method == 'POST':
        data = request.json
        if add_job(data['rq_desc']):
            #updates the requisition on the database 
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("UPDATE REQUEST SET rq_status = '"+data['rq_status']+"', rq_approved_by = "+(str(session.get("emp_id")) if data['rq_status'] == 'Approved' else "NULL ") + ", rq_desc = '"+data['rq_desc'] +"' WHERE rq_id = "+str(rq_id)+" ;")
            conn.commit()
            cur.close()
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    abort(404)   
    
@views.route('/requisitions/new-requisition/goods', methods=['GET','POST'])
@login_required
def requisitionsNewGoods():
    if request.method == 'GET':
        emp_data = get_employee(session['emp_id'])
        
        all_raw_items = None
        all_equipment_items = None
        all_units = None
        #gets all the raw items
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM ITEM INNER JOIN UNIT USING(unit_id)WHERE item_type = 'RAW';")
        rows = cur.fetchall()
        cur.close()
        if rows:
            all_raw_items = rows
            
        #gets all the equipment items
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM ITEM INNER JOIN UNIT USING(unit_id) WHERE item_type = 'EQUIPMENT';")
        rows = cur.fetchall()
        cur.close()
        if rows:
            all_equipment_items = rows
            
        #gets all the equipment items
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM UNIT;")
        rows = cur.fetchall()
        cur.close()
        if rows:
            all_units = rows
        return render_template('requisition-create-goods.html',employee = emp_data, raw_items = all_raw_items, equipment_items = all_equipment_items, units = all_units, account = emp_data)
    
    if request.method == 'POST': 
        data = request.json
        if add_job(data['rq_desc']):
            #inserts the new requisition on the database 
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("INSERT INTO REQUEST (rq_type, rq_desc, emp_id) VALUES ( 'GOODS', '"+data['rq_desc']+"',"+str(session.get('emp_id'))+") RETURNING rq_id;")
            conn.commit()
            
            request_id = cur.fetchone()

            for item in data['items']:
                #inserts the new goods requisition in requested items on the database 
                cur = conn.cursor(cursor_factory=extras.RealDictCursor)
                cur.execute("INSERT INTO REQ_ITEM (ri_quantity, rq_id, item_id) VALUES ( "+str(item['item_quantity'])+", "+str(request_id['rq_id'])+","+str(item['item_id'])+") ;")
                conn.commit()
                
            cur.close()
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    abort(404)

@views.route('/requisitions/update-requisition/goods/<int:rq_id>', methods=['GET','POST'])
@login_required
def requisitionsUpdateGoods(rq_id):
    if request.method == 'GET':
        
        all_vendors = None
        #gets all the vendors from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM VENDOR;")
        rows = cur.fetchall()
        if(rows):
            all_vendors = rows
        
        #gets the employee id from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM EMPLOYEE INNER JOIN REQUEST USING(emp_id) WHERE rq_id ="+str(rq_id)+"")
        rows = cur.fetchone()
        if not rows:
            abort(404)
        emp_data = get_employee(rows['emp_id'])
        
        requisition_data = None
        
        #gets the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM REQUEST LEFT JOIN REQ_ITEM USING (rq_id) LEFT JOIN ITEM USING (item_id) LEFT JOIN UNIT USING(unit_id) LEFT JOIN ACKNOWLEDGEMENT USING (ac_id) WHERE REQUEST.rq_id = "+str(rq_id)+" ;")
        rows = cur.fetchall()
        cur.close()
        if(rows):
            requisition_data = rows
        emp = get_employee(session['emp_id'])         
        return render_template('requisition-goods-update.html', requisition = requisition_data, employee = emp_data, vendors = all_vendors, account = emp)   
    
    if request.method == 'POST':
        rq_status = request.form.get('rq_status')
        ac_receipt_id = None
        ac_receipt = None
        if request.files.get('ac_receipt'):
            ac_receipt = request.files.get('ac_receipt').read()
        
        if ac_receipt:
                cur = conn.cursor(cursor_factory=extras.RealDictCursor)
                cur.execute("SELECT COUNT(ac_id) FROM REQUEST WHERE rq_id="+str(rq_id)+" ;")
                rows = cur.fetchone()
                if rq_status == 'Approved' and rows['count'] == 0:
                    
                    #inserts the new acknowledgement receipt on the database 
                    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

                    # Use the encoded binary data in the query
                    cur.execute("INSERT INTO ACKNOWLEDGEMENT (ac_receipt) VALUES (%s) RETURNING ac_id;", (psycopg2.Binary(ac_receipt),))
                    rq_status = 'Completed' 
                    conn.commit()
                    ac_receipt_id  = cur.fetchone()
                    
                    #updates the status of request
                    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
                    cur.execute("UPDATE REQUEST SET rq_status = 'Completed' WHERE rq_id = "+str(rq_id)+" ;")
                    conn.commit()
                
        #updates the specified request
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        query = ",  ac_id = "+str(ac_receipt_id['ac_id']) if ac_receipt_id else " "
        cur.execute("UPDATE REQUEST SET rq_status ='"+rq_status+"'"+query+" WHERE rq_id = "+str(rq_id)+" ;")
        conn.commit()
        cur.close()
        response_data = {"message": "Success"}
        return jsonify(response_data), 200
    abort(404)

#REMOVES THE ITEMS IN INVENTORY
@views.route('/requisitions/update-requisition/goods/release/<int:rq_id>', methods=['GET','POST'])
@admin_required
def requisitionsUpdateGoodsRelease(rq_id):
    if request.method == 'POST':
        is_releasable = True
        total_count = 0
        data = request.json
        
        #checks if this is already released
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT is_released FROM REQUEST WHERE rq_id = "+str(rq_id)+"")
        rows = cur.fetchone()
        if rows['is_released']:
            abort(404)
        
        #gets the requested item in db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM REQUEST INNER JOIN REQ_ITEM USING(rq_id) WHERE rq_id = "+str(rq_id)+";")
        rows = cur.fetchall()
        if rows:
            data = rows
            
        total_quantity = []
        for item in data:
            #gets the total count of an item id from the db
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT SUM(di_quantity - di_deducted) as total_count FROM DELIVERED_ITEM WHERE (di_expiry > CURRENT_DATE OR di_expiry IS NULL) AND (di_quantity != di_deducted OR di_quantity != 0) AND item_id ="+str(item['item_id'])+"")
            rows = cur.fetchone()
            
            if rows['total_count'] > 0:
                total_count = rows['total_count']   
                total_quantity.append(total_count)

                if total_count and total_count < item['ri_quantity']:
                    is_releasable = False
                    break
            else:
                is_releasable = False

        if is_releasable:
            for item in data:
                print(item['item_id'])
                #gets the total count of an item id from the db
                cur = conn.cursor(cursor_factory=extras.RealDictCursor)
                cur.execute("SELECT di_id, (di_quantity - di_deducted) AS quantity FROM DELIVERED_ITEM WHERE (di_expiry > CURRENT_DATE OR di_expiry IS NULL) AND (di_quantity != di_deducted OR di_quantity != 0) AND item_id ="+str(item['item_id'])+" ORDER BY di_expiry ASC;")
                rows = cur.fetchall()
                if rows:
                    for inv_item in rows:
                        if item['ri_quantity'] == 0:
                            break
                        
                        if item['ri_quantity'] > inv_item['quantity']:
                            item['ri_quantity'] = item['ri_quantity'] - inv_item['quantity']
                            #updates the specified delivered item
                            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
                            cur.execute("UPDATE DELIVERED_ITEM SET di_deducted = di_deducted + "+str(inv_item['quantity'])+" WHERE di_id = "+str(inv_item['di_id'])+" ;")
                            conn.commit()
                            
                        elif item['ri_quantity'] <=  inv_item['quantity']:
                            #updates the specified delivered item
                            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
                            cur.execute("UPDATE DELIVERED_ITEM SET di_deducted = di_deducted + "+str(item['ri_quantity'])+" WHERE di_id = "+str(inv_item['di_id'])+" ;")
                            conn.commit()
                            item['ri_quantity'] = item['ri_quantity'] - inv_item['quantity']
                                
                            
            #updates the status of request
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("UPDATE REQUEST SET rq_status = 'Approved', is_released = True  WHERE rq_id = "+str(rq_id)+" ;")
            conn.commit()
            cur.close()
            
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    
        abort(404)
                       

#CREATE ACKNOWLEDGEMENT RECEIPT
@views.route('/requisitions/update-requisition/goods/acknowledgement-receipt/<int:rq_id>', methods=['GET','POST'])
@login_required
def requisitionsUpdateAcknowledgementReceipt(rq_id):
    if request.method =='GET':
        
        #gets the employee id from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM EMPLOYEE INNER JOIN REQUEST USING(emp_id) WHERE rq_id ="+str(rq_id)+"")
        rows = cur.fetchone()
        if not rows:
            abort(404)
        emp_data = get_employee(rows['emp_id'])
        
        requisition_data = None
        current_date = date.today()
        
        #gets the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM REQUEST LEFT JOIN REQ_ITEM USING (rq_id) LEFT JOIN ITEM USING (item_id) LEFT JOIN UNIT USING(unit_id) LEFT JOIN ACKNOWLEDGEMENT USING (ac_id) WHERE REQUEST.rq_id = "+str(rq_id)+" ;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            requisition_data = rows   
        emp = get_employee(session['emp_id'])      
        return render_template('generated-acknowledgement-receipt.html', requisition = requisition_data, employee = emp_data, date = current_date, account = emp)   
    
    elif request.method == 'POST':
        ac_receipt_data = None
        
        #gets the delivered items from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM REQUEST INNER JOIN ACKNOWLEDGEMENT USING(ac_id) WHERE REQUEST.rq_id = "+str(rq_id)+" ;")
        rows = cur.fetchone()
        cur.close()      
        if(rows):
            ac_receipt_data = rows['ac_receipt']
        else:
            abort(404)
        
        pdf_data  = BytesIO(ac_receipt_data)
        return send_file(pdf_data, as_attachment=True, download_name='AcknowledgementReceipt.pdf', mimetype='application/pdf'), 200
    abort(404)

#CREATE PURCHASING ORDER
@views.route('/requisitions/update-requisition/goods/create-po/<int:rq_id>', methods=['GET','POST'])
@login_required
def requisitionsUpdateGoodsCreatePO(rq_id):
    if request.method == 'POST':
        data = request.json
        
        #checks if the there is already a request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM PURCHASING_ORDER WHERE rq_id ="+str(rq_id)+"")
        rows = cur.fetchone()
        if rows:
            abort(404)
        
        #inserts the new goods requisition on the database 
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("INSERT INTO PURCHASING_ORDER (rq_id, vnd_id) VALUES ("+str(rq_id)+","+str(data['vnd_id'])+");")
        conn.commit()
        
        #updates the goods requisition on the database 
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("UPDATE REQUEST SET rq_status = 'Approved' WHERE rq_id = "+str(rq_id)+" ;")
        conn.commit()
        
        cur.close()
        response_data = {"message": "Success"}
        return jsonify(response_data), 200
    abort(404)

#===============================
#       PURCHASING ORDER
#===============================

@views.route('/purchasing-order', methods=['GET','POST'])
@admin_required
def purchasingOrder():
    if request.method == 'GET':
        all_purchasing_orders = None
        all_purchasing_orders_completed = None
        
        #gets the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, PURCHASING_ORDER.date_created as po_date_created FROM EMPLOYEE LEFT JOIN REQUEST USING (emp_id) INNER JOIN PURCHASING_ORDER USING (rq_id) WHERE po_status != 'Completed' ORDER BY(PURCHASING_ORDER.date_created) DESC;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_purchasing_orders = rows 
        
        #gets the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, PURCHASING_ORDER.date_created as po_date_created FROM EMPLOYEE LEFT JOIN REQUEST USING (emp_id) INNER JOIN PURCHASING_ORDER USING (rq_id) WHERE po_status = 'Completed' ORDER BY(PURCHASING_ORDER.date_created) DESC;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_purchasing_orders_completed = rows     
        emp_data = get_employee(session['emp_id'])
        return render_template('purchasing-order-list.html', purchasing_orders = all_purchasing_orders, purchasing_orders_completed = all_purchasing_orders_completed, account = emp_data)
    abort(404)

@views.route('/purchasing-order/search/<int:po_id>', methods=['GET','POST'])
@admin_required
def purchasingOrderSearch(po_id):
    if request.method == 'GET':
        all_purchasing_orders = None
        all_purchasing_orders_completed = None
        
        #gets the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM EMPLOYEE LEFT JOIN REQUEST USING (emp_id) INNER JOIN PURCHASING_ORDER USING (rq_id) WHERE po_id = "+str(po_id)+" ORDER BY(po_id) DESC;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_purchasing_orders = rows 
        
        #gets the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM EMPLOYEE LEFT JOIN REQUEST USING (emp_id) INNER JOIN PURCHASING_ORDER USING (rq_id) WHERE po_status = 'Completed' AND po_id = "+str(po_id)+" ORDER BY(po_id) DESC;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_purchasing_orders_completed = rows     
        emp_data = get_employee(session['emp_id'])
        return render_template('purchasing-order-list.html', purchasing_orders = all_purchasing_orders, purchasing_orders_completed = all_purchasing_orders_completed, account = emp_data)

@views.route('/purchasing-order/update/<int:po_id>', methods=['GET','POST'])
@admin_required
def purchasingOrderUpdate(po_id):
    if request.method == 'GET':
        all_purchasing_orders = None
        all_delivery = None
        is_inserted = False
        
        #gets the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, ITEM.item_id as tb_item_id FROM EMPLOYEE LEFT JOIN REQUEST USING (emp_id) LEFT JOIN REQ_ITEM USING (rq_id) LEFT JOIN ITEM USING (item_id) LEFT JOIN UNIT USING(unit_id) LEFT JOIN PURCHASING_ORDER USING(rq_id) LEFT JOIN DELIVERY USING(po_id) LEFT JOIN VENDOR USING(vnd_id) WHERE PURCHASING_ORDER.po_id = "+str(po_id)+"  ORDER BY(ITEM.item_id);")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_purchasing_orders = rows 
        
        #gets the delivery from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM DELIVERED_ITEM WHERE dlr_id = (SELECT dlr_id FROM DELIVERY WHERE po_id = "+str(po_id)+") ORDER BY(item_id) ;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_delivery = rows 
            
        #checks if the items are already inserted
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT COUNT(di_id) FROM DELIVERED_ITEM WHERE dlr_id = (SELECT dlr_id FROM DELIVERY WHERE po_id = "+str(po_id)+" );")
        rows = cur.fetchone()
        if  rows['count'] > 0:
            is_inserted = True
        emp_data = get_employee(session['emp_id'])  
        return render_template('purchasing-order-update.html', purchasing_orders = all_purchasing_orders, delivery = all_delivery, inserted = is_inserted, account = emp_data)
    
    if request.method == 'POST':
        po_status = request.form.get('po_status')
        po_quotation = None
        dlr_receiving_memo = None
        
        if request.files.get('po_quotation'):
            po_quotation = request.files.get('po_quotation').read()
            
        if request.files.get('dlr_receiving_memo'):
            dlr_receiving_memo = request.files.get('dlr_receiving_memo').read()
        
        if po_quotation:
            #checks if theres a quotation on db
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT COUNT(po_quotation) FROM PURCHASING_ORDER WHERE po_id = "+str(po_id)+" ;")
            rows = cur.fetchone()
            
            if rows['count'] == 0:
                #inserts the new quotation on the database 
                cur = conn.cursor(cursor_factory=extras.RealDictCursor)
                cur.execute("UPDATE PURCHASING_ORDER SET po_quotation = %s WHERE po_id = "+str(po_id)+" ;", (psycopg2.Binary(po_quotation),))
                conn.commit()
                
                
               
        if dlr_receiving_memo: 
            #checks if theres a receiving memo on db
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT COUNT(dlr_receiving_memo), po_id FROM DELIVERY WHERE po_id = "+str(po_id)+" GROUP BY(po_id) ;")
            rows = cur.fetchone()
            if rows and rows['count'] == 0:
                #inserts the new receiving memo on the database 
                cur = conn.cursor(cursor_factory=extras.RealDictCursor)
                cur.execute("UPDATE DELIVERY SET dlr_receiving_memo = %s WHERE po_id = "+str(po_id)+" ;", (psycopg2.Binary(dlr_receiving_memo),))
                conn.commit()
                
                po_status = 'Completed'                
        
        if po_status:
            #checks if theres a receiving memo on db
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT COUNT(po_id)  FROM DELIVERY WHERE po_id = "+str(po_id)+" ;")
            rows = cur.fetchone()
            if rows['count'] == 0:
                #inserts the new goods requisition on the database 
                cur = conn.cursor(cursor_factory=extras.RealDictCursor)
                cur.execute("INSERT INTO DELIVERY (po_id, dlr_status) VALUES ("+str(po_id)+", 'Approved');")
                conn.commit()
        
        #updates the specified purchasing order
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("UPDATE PURCHASING_ORDER SET po_status ='"+po_status+"' WHERE po_id = "+str(po_id)+" ;")
        conn.commit()
        cur.close()
        response_data = {"message": "Success"}
        return jsonify(response_data), 200
    abort(404)
    
#INSERTS THE ITEMS TO INVENTORY
@views.route('/purchasing-order/update/insert-inventory/<int:po_id>', methods=['GET','POST'])
@admin_required
def purchasingOrderUpdateInsertInventory(po_id):
    if request.method == 'POST':
        data = request.json
        dlr_id = None
        
        #checks if theres a quotation on db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT (dlr_id) FROM DELIVERY WHERE dlr_status = 'Completed' AND po_id = "+str(po_id)+" ;")
        rows = cur.fetchone()
        if not rows:
            abort(404)
        else:
            dlr_id = rows['dlr_id']
            
        #checks if the items are already released in db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT COUNT(di_id) FROM DELIVERED_ITEM WHERE dlr_id = "+str(dlr_id)+" ;")
        rows = cur.fetchone()
        if rows['count'] > 0:
            abort(404)
        
        #inserts the received items
        for item in data['items']:
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            if item['item_type'] != 'EQUIPMENT':
                cur.execute("INSERT INTO DELIVERED_ITEM (di_quantity, di_expiry, dlr_id, item_id) VALUES ("+str(item['di_quantity'])+", '"+item['di_expiry']+"', "+str(dlr_id)+", "+str(item['item_id'])+");")
            else:
                cur.execute("INSERT INTO DELIVERED_ITEM (di_quantity, dlr_id, item_id) VALUES ("+str(item['di_quantity'])+",  "+str(dlr_id)+","+str(item['item_id'])+");")
            conn.commit()
            
        cur.close()
        
        response_data = {"message": "Success"}
        return jsonify(response_data), 200
    abort(404)

#GENERATE PURCHASING ORDER
@views.route('/purchasing-order/update/generatePO/<int:po_id>', methods=['GET','POST'])
@admin_required
def purchasingOrderUpdateGeneratePO(po_id):
    if request.method == 'GET':
        all_purchasing_orders = None
        current_date = date.today()
        
        #gets the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM REQUEST LEFT JOIN REQ_ITEM USING (rq_id) LEFT JOIN ITEM USING (item_id) LEFT JOIN UNIT USING(unit_id) LEFT JOIN PURCHASING_ORDER USING(rq_id) LEFT JOIN VENDOR USING(vnd_id) WHERE PURCHASING_ORDER.po_id = "+str(po_id)+" ;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_purchasing_orders = rows 
            
        #gets the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, ITEM.item_id as tb_item_id FROM EMPLOYEE LEFT JOIN REQUEST USING (emp_id) LEFT JOIN REQ_ITEM USING (rq_id) LEFT JOIN ITEM USING (item_id) LEFT JOIN UNIT USING(unit_id) LEFT JOIN PURCHASING_ORDER USING(rq_id) LEFT JOIN DELIVERY USING(po_id) LEFT JOIN VENDOR USING(vnd_id) WHERE PURCHASING_ORDER.po_id = "+str(po_id)+"  ORDER BY(ITEM.item_id);")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_purchasing_orders = rows  
            
        emp_data = get_employee(session['emp_id'])
        return render_template('generated-purchasing-order.html', purchasing_orders = all_purchasing_orders, cur_date = current_date, account = emp_data)
    
    elif request.method == 'POST':
        po_quotaion = None

        #gets the PO quotation from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM PURCHASING_ORDER WHERE po_id = "+str(po_id)+" ;")
        rows = cur.fetchone()
        cur.close()      
        if(rows):
            po_quotaion = rows['po_quotation']
        else:
            abort(404)
        
        pdf_data  = BytesIO(po_quotaion)
        return send_file(pdf_data, as_attachment=True, download_name='PurchasingOrder.pdf', mimetype='application/pdf'), 200
    abort(404)
        

#CREATE RECEIVING MEMO
@views.route('/purchasing-order/update/createRM/<int:po_id>', methods=['GET','POST'])
@admin_required
def purchasingOrderUpdateCreateRM(po_id):
    if request.method == 'GET':
        all_purchasing_orders = None
        current_date = date.today()
        all_delivery = None
        
        #gets the request from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, ITEM.item_id as tb_item_id FROM EMPLOYEE LEFT JOIN REQUEST USING (emp_id) LEFT JOIN REQ_ITEM USING (rq_id) LEFT JOIN ITEM USING (item_id) LEFT JOIN UNIT USING(unit_id) LEFT JOIN PURCHASING_ORDER USING(rq_id) LEFT JOIN DELIVERY USING(po_id) LEFT JOIN VENDOR USING(vnd_id) WHERE PURCHASING_ORDER.po_id = "+str(po_id)+"  ORDER BY(ITEM.item_id);")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_purchasing_orders = rows 
        
        #gets the delivery from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM DELIVERED_ITEM WHERE dlr_id = (SELECT dlr_id FROM DELIVERY WHERE po_id = "+str(po_id)+") ORDER BY(item_id) ;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_delivery = rows 
        emp_data = get_employee(session['emp_id'])
        return render_template('generated-receiving-memo.html', purchasing_orders = all_purchasing_orders, delivery = all_delivery, cur_date = current_date, account = emp_data)

    elif request.method == 'POST':
        dlr_receiving_memo = None
        
        #gets the delivery receipt from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM DELIVERY WHERE po_id = "+str(po_id)+" ;")
        rows = cur.fetchone()
        cur.close()      
        if(rows):
            dlr_receiving_memo = rows['dlr_receiving_memo']
        else:
            abort(404)
        
        pdf_data  = BytesIO(dlr_receiving_memo)
        return send_file(pdf_data, as_attachment=True, download_name='ReceivingMemo.pdf', mimetype='application/pdf'), 200
    abort(404)


#===============================
#           DELIVERY
#===============================

@views.route('/delivery', methods=['GET','POST'])
@admin_required
def delivery():
    if request.method == 'GET':
        all_deliveries = None
        all_deliveries_completed = None
        #gets the deliveries from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, DELIVERY.date_created as delivery_created FROM EMPLOYEE INNER JOIN REQUEST USING(emp_id) INNER JOIN PURCHASING_ORDER USING(rq_id) INNER JOIN DELIVERY USING(po_id) WHERE dlr_status != 'Completed' ORDER BY(DELIVERY.dlr_id) DESC;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_deliveries = rows 
            
        #gets the completed delivery from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, DELIVERY.date_created as delivery_created FROM EMPLOYEE INNER JOIN REQUEST USING(emp_id) INNER JOIN PURCHASING_ORDER USING(rq_id) INNER JOIN DELIVERY USING(po_id) WHERE dlr_status = 'Completed';")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_deliveries_completed = rows 
        emp_data = get_employee(session['emp_id'])
        return render_template('delivery.html', deliveries = all_deliveries, deliveries_completed = all_deliveries_completed, account = emp_data)

@views.route('/delivery/search/<int:searched_id>', methods=['GET','POST'])
@admin_required
def deliverySearch(searched_id):
    if request.method == 'GET':
        all_deliveries = None
        all_deliveries_completed = None
        #gets the deliveries from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, DELIVERY.date_created as delivery_created FROM EMPLOYEE INNER JOIN REQUEST USING(emp_id) INNER JOIN PURCHASING_ORDER USING(rq_id) INNER JOIN DELIVERY USING(po_id) WHERE dlr_status != 'Completed' AND (PURCHASING_ORDER.po_id = "+str(searched_id)+" OR dlr_id = "+str(searched_id)+") ORDER BY(DELIVERY.dlr_id) DESC;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_deliveries = rows 
            
        #gets the completed delivery from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, DELIVERY.date_created as delivery_created FROM EMPLOYEE INNER JOIN REQUEST USING(emp_id) INNER JOIN PURCHASING_ORDER USING(rq_id) INNER JOIN DELIVERY USING(po_id) WHERE dlr_status = 'Completed' AND (PURCHASING_ORDER.po_id = "+str(searched_id)+" OR dlr_id = "+str(searched_id)+");")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_deliveries_completed = rows 
        emp_data = get_employee(session['emp_id'])
        return render_template('delivery.html', deliveries = all_deliveries, deliveries_completed = all_deliveries_completed, account = emp_data)


@views.route('/delivery/update/<int:dlr_id>', methods=['GET','POST'])
@admin_required
def deliveryUpdate(dlr_id):
    if request.method == 'GET':
        all_deliveries = None
        #gets the delivery from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT *, ITEM.item_id as tb_item_id FROM EMPLOYEE LEFT JOIN REQUEST USING(emp_id) LEFT JOIN REQ_ITEM USING (rq_id) LEFT JOIN ITEM USING (item_id) LEFT JOIN UNIT USING(unit_id) LEFT JOIN PURCHASING_ORDER USING(rq_id) LEFT JOIN DELIVERY USING(po_id) LEFT JOIN VENDOR USING(vnd_id) WHERE DELIVERY.dlr_id = "+str(dlr_id)+" ;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_deliveries = rows 
        emp_data = get_employee(session['emp_id'])
        return render_template('delivery-update.html', deliveries = all_deliveries, account = emp_data)
    
    if request.method == 'POST':  
        dlr_status = request.form.get('dlr_status')
        dlr_receipt = None
        
        if request.files.get('dlr_receipt'):
            dlr_receipt = request.files.get('dlr_receipt').read()
            
        if dlr_receipt:
            
            #checks if theres a dlr receipt on db
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT COUNT(dlr_receipt) FROM DELIVERY WHERE dlr_id = "+str(dlr_id)+" ;")
            rows = cur.fetchone()
            if rows['count'] == 0:
                #inserts the new delivery receipt on the database 
                cur = conn.cursor(cursor_factory=extras.RealDictCursor)
                cur.execute("UPDATE DELIVERY SET dlr_receipt = %s WHERE dlr_id = "+str(dlr_id)+" ;", (psycopg2.Binary(dlr_receipt),))
                dlr_status = 'Completed'
                conn.commit()
        
        #updates the specified purchasing order
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("UPDATE DELIVERY SET dlr_status ='"+dlr_status+"' WHERE dlr_id = "+str(dlr_id)+" ;")
        conn.commit()
        cur.close()
        response_data = {"message": "Success"}
        return jsonify(response_data), 200
    abort(404)
    
#GET DELIVERY RECEIPT
@views.route('/delivery/update/delivery-receipt/<int:dlr_id>', methods=['GET','POST'])
@admin_required
def deliveryUpdateViewDeliveryReceipt(dlr_id):
    if request.method == 'POST':
        dlr_receipt = None
        
        #gets the delivery receipt from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM DELIVERY WHERE dlr_id = "+str(dlr_id)+" ;")
        rows = cur.fetchone()
        cur.close()      
        if rows:
            dlr_receipt = rows['dlr_receipt']
        else:
            abort(404)
        
        pdf_data  = BytesIO(dlr_receipt)
        return send_file(pdf_data, as_attachment=True, download_name='DeliveryReceipt.pdf', mimetype='application/pdf'), 200
    abort(404)

#===============================
#           REPORT
#===============================

@views.route('/report', methods=['GET','POST'])
@login_required
def report():
    if request.method == 'GET':
        top_items_list = None
        all_yearly_requisition = None
        year = date.today().year
        list_years = list(range(2000, 2201))
        #gets the total requisition in the current year from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("WITH all_months AS (SELECT generate_series(1, 12) AS month) SELECT am.month AS month, COALESCE(COUNT(ri.date_created), 0) AS item_count FROM all_months am LEFT JOIN REQ_ITEM ri ON EXTRACT(YEAR FROM ri.date_created) = "+str(year)+" AND EXTRACT(MONTH FROM ri.date_created) = am.month GROUP BY am.month ORDER BY am.month;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_yearly_requisition = rows 
        
        #gets the top 5 item requested from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT ITEM.item_id,item_name, COUNT(*) as item_count, item_type FROM REQ_ITEM INNER JOIN ITEM USING (item_id) INNER JOIN UNIT USING(unit_id) GROUP BY ITEM.item_id ORDER BY (item_count) DESC LIMIT 5;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            top_items_list = rows 
        emp_data = get_employee(session['emp_id'])
        return render_template('reports.html', top_items = top_items_list, yearly_requisition = all_yearly_requisition, year_selected = year, years = list_years, account = emp_data)
    
    elif request.method == 'POST':
        current_inventory = None
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM ITEM LEFT JOIN UNIT USING (unit_id) LEFT JOIN DELIVERED_ITEM USING (item_id) ;")
        rows = cur.fetchall()
        if(rows):
            current_inventory = rows
        cur.close()
        response_data = {"message": "Success"}
        return jsonify(response_data), 200
    
@views.route('/report/search/<int:year>', methods=['GET','POST'])
@login_required
def reportSearchYear(year):
    if request.method == 'GET':
        top_items_list = None
        all_yearly_requisition = None
        list_years = list(range(2000, 2201))
        #gets the total requisition in the current year from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("WITH all_months AS (SELECT generate_series(1, 12) AS month) SELECT am.month AS month, COALESCE(COUNT(ri.date_created), 0) AS item_count FROM all_months am LEFT JOIN REQ_ITEM ri ON EXTRACT(YEAR FROM ri.date_created) = "+str(year)+" AND EXTRACT(MONTH FROM ri.date_created) = am.month GROUP BY am.month ORDER BY am.month;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            all_yearly_requisition = rows 
        
        #gets the top 5 item requested from the db
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT ITEM.item_id,item_name, COUNT(*) as item_count, item_type FROM REQ_ITEM INNER JOIN ITEM USING (item_id) INNER JOIN UNIT USING(unit_id) GROUP BY ITEM.item_id ORDER BY (item_count) DESC LIMIT 5;")
        rows = cur.fetchall()
        cur.close()      
        if(rows):
            top_items_list = rows 
        emp_data = get_employee(session['emp_id'])
        return render_template('reports.html', top_items = top_items_list, yearly_requisition = all_yearly_requisition, year_selected = year, years = list_years, account = emp_data)
    
    elif request.method == 'POST':
        current_inventory = None
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM ITEM LEFT JOIN UNIT USING (unit_id) LEFT JOIN DELIVERED_ITEM USING (item_id) ;")
        rows = cur.fetchall()
        if(rows):
            current_inventory = rows
        cur.close()
        response_data = {"message": "Success"}
        return jsonify(response_data), 200

@views.route('/print/inventory', methods=['GET','POST'])
@login_required
def printInventory():
    cur_date = date.today()
    current_inventory = None
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT ITEM.item_id, item_name,(di_quantity - di_deducted) as quantity, unit_name, item_type FROM ITEM LEFT JOIN UNIT USING(unit_id) LEFT JOIN DELIVERED_ITEM ON ITEM.item_id = DELIVERED_ITEM.item_id AND (DELIVERED_ITEM.di_expiry > CURRENT_DATE OR DELIVERED_ITEM.di_expiry IS NULL) AND (DELIVERED_ITEM.di_quantity != DELIVERED_ITEM.di_deducted OR DELIVERED_ITEM.di_quantity IS NULL) ORDER BY(item_type);")
    rows = cur.fetchall()
    if(rows):
        current_inventory = rows
    cur.close()
    emp_data = get_employee(session['emp_id'])
    return render_template('print-inventory.html', inventory = current_inventory, date = cur_date, account = emp_data)


#===============================
#     GET EMPLOYEE DETAILS
#===============================

def get_employee(emp_id):
    #gets the employee name from the db
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM EMPLOYEE WHERE emp_id ="+str(emp_id)+"")
    rows = cur.fetchone()
    cur.close()
    if(rows):
        return rows
    else:
        return None