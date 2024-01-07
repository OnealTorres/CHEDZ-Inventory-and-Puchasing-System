from datetime import datetime
import os

#Login Page
def emp_login(emp_email, emp_password):
    if len(emp_email) > 50 or len(emp_email) <= 0:
        return False
    elif len(emp_password) > 50 or len(emp_password) <= 0:
        return False
    return True

#Registration
def emp_register(emp_fname, emp_mname, emp_lname, emp_email, emp_password):
    if len(emp_fname) > 20 or len(emp_fname) <= 0:
        return False
    elif len(emp_mname) > 20 or len(emp_mname) <= 0:
        return False
    elif len(emp_lname) > 20 or len(emp_lname) <= 0:
        return False
    elif '@' not in emp_email or '.' not in emp_email or not (0 < len(emp_email) <= 50):
        return False
    elif emp_email.find('@') == -1 or emp_email.find('.') == -1 or len(emp_email) > 50 or len(emp_email) <= 0:
        return False
    elif len(emp_password) > 50 or len(emp_password) <= 0:
        return False
    return True
    
#Add Item
def add_item(item_name):
    if len(item_name) > 50 or len(item_name) <=0:
        return False
    return True

# Update Item
def update_item(item_name):
    if len(item_name) > 50:
        return False
    return True

# Add Job Requisition 
def add_job(rq_desc):
    if len(rq_desc) > 150 or len(rq_desc) <=0 :
        return False
    return True

# Job View Requisition 
def view_job(rq_desc):
    if len(rq_desc) > 150:
        return False
    return True


# List Goods Request
def goods_rq(rq_desc):
    if len(rq_desc) > 150 or len(rq_desc) <=0 :
        return False
    return True

# Add Goods/Item Requisition
def add_goods_rq(ri_quantity):
    if ri_quantity is not int:
        return False
    return True

# View Goods/Item Requisition
def ac_FileType(ac_receipt):
    valid_types = {'.pdf'}
    is_valid_type = False
    max_size = 5 * 1024  # 5 MB in KB
    min_size = 0.5 * 1024  # 0.5 MB in KB
   
    if not os.path.exists(ac_receipt):
        return False
    
    extension = os.path.splitext(ac_receipt)[1].lower()
    filesize = os.stat(ac_receipt).st_size/1024
   
    for file_type in valid_types:
        if extension == file_type:
            is_valid_type = True
            break

    return is_valid_type and min_size < filesize < max_size

def view_goods_rq(rq_desc):
    if len(rq_desc) > 150  :
        return False
    return True

# Add Vendor
def add_vendor(vnd_name, vnd_contact, vnd_email):
    if len(vnd_name) > 50 or len(vnd_name) <=0:
        return False
    elif len(vnd_contact) != 11 or not vnd_contact.startswith('09'):
        return False
    elif vnd_email.find('@') == -1 or vnd_email.find('.') == -1 or len(vnd_email) > 50 or len(vnd_email) <= 0:
        return False
    return True

# Update Vendor
def update_vendor(vnd_name, vnd_contact, vnd_email):
    if len(vnd_name) > 50 or len(vnd_name) <=0 :
        return False
    elif len(vnd_contact) != 11 and not vnd_contact.startswith('09'):
        return False
    elif not vnd_email.find('@') and not vnd_email.find('.') or len(vnd_email) > 50 or len(vnd_email) <= 0:
        return False
    return True

# Update Purchasing Order
def po_FileType(po_quotation):
    valid_types = {'.pdf'}
    is_valid_type = False
    max_size = 5 * 1024  # 5 MB in KB
    min_size = 0.5 * 1024  # 0.5 MB in KB

    if not os.path.exists(po_quotation):
        return False

    extension = os.path.splitext(po_quotation)[1].lower()
    filesize = os.stat(po_quotation).st_size / 1024

    for file_type in valid_types:
        if extension == file_type:
            is_valid_type = True
            break

    return is_valid_type and min_size < filesize < max_size

  

def dlr_FileType(dlr_receipt):
    valid_types = {'pdf'}
    is_valid_type = False
    max_size = 5 * 1024  # 5 MB in KB
    min_size = 0.1 * 1024  # 0.5 MB in KB
    
    extension = os.path.splitext(dlr_receipt)[1].lower()
    filesize = os.stat(dlr_receipt).st_size/1024
   
    for file_type in valid_types:
        if extension == file_type:
            is_valid_type = True
            break
    print(is_valid_type and min_size < filesize < max_size)
    return is_valid_type and min_size < filesize < max_size

def expiry_date(input_date):
    try:
        # Convert input string to a datetime object
        date_object = datetime.strptime(input_date, '%Y-%m-%d')
        
        # Get current date
        current_date = datetime.now().date()
        
        # Compare the input date with the current date
        if date_object <= current_date:
            return False, 
        else:
            return True, 
    except ValueError:
        return False, "Error: Please enter a valid date in YYYY-MM-DD format."


# Receiving Memo

def memo_date(input_date):
    try:
        # Convert input string to a datetime object
        date_object = datetime.strptime(input_date, '%Y-%m-%d')
        
        # Get current date
        current_date = datetime.now().date()
        
        # Compare the input date with the current date
        if date_object < current_date:
            return False, 
        else:
            return True, 
    except ValueError:
        return False, "Error: Please enter a valid date in YYYY-MM-DD format."

 
# Delivery Update
def dlr_receipt_FileType(po_quotation):
    valid_types = {'.pdf'}
    is_valid_type = False
    max_size = 5 * 1024  # 5 MB in KB
    min_size = 0.5 * 1024  # 0.5 MB in KB

    if not os.path.exists(po_quotation):
        return False

    extension = os.path.splitext(po_quotation)[1].lower()
    filesize = os.stat(po_quotation).st_size / 1024

    for file_type in valid_types:
        if extension == file_type:
            is_valid_type = True
            break

    return is_valid_type and min_size < filesize < max_size


# Reports
def from_date(input_date):
    try:
        # Convert input string to a datetime object
        date_object = datetime.strptime(input_date, '%Y-%m-%d')
        
        # Get current date
        current_date = datetime.now().date()
        
        # Compare the input date with the current date
        if date_object < current_date:
            return False, 
        else:
            return True, 
    except ValueError:
        return False, "Error: Please enter a valid date in YYYY-MM-DD format."

def to_date(input_date):
    try:
        # Convert input string to a datetime object
        date_object = datetime.strptime(input_date, '%Y-%m-%d')
        
        # Get current date
        current_date = datetime.now().date()
        
        # Compare the input date with the current date
        if date_object <= current_date:
            return False, 
        else:
            return True, 
    except ValueError:
        return False, "Error: Please enter a valid date in YYYY-MM-DD format."
