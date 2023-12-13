from datetime import datetime

class Employee():
    emp_id = None
    emp_fname = None
    emp_mname = None
    emp_lname = None
    emp_email = None
    emp_password = None
    emp_status = 'Active'
    emp_type = 'EMP'
    date_created = datetime.now()
    date_updated = datetime.now()
    
class Request():
    rq_id = None
    rq_type = None
    rq_desc = None
    rq_status = 'Pending'
    rq_approved_by = None
    date_created = datetime.now()
    date_updated = datetime.now()
    emp_id = None
    
class Req_Job():
    rj_id = None
    rj_desc = None
    date_created = datetime.now()
    date_updated = datetime.now()
    rq_id = None

class Purchasing_Order():
    po_id = None
    po_status = 'Pending'
    po_approved_by = None
    po_qoutation = None
    date_created = datetime.now()
    date_updated = datetime.now()
    rq_id = None
    vnd_id = None
    
class Delivery():
    dlr_id = None
    dlr_status = None
    dlr_receipt = None
    dlr_receiving_memo = None
    date_created = datetime.now()
    date_updated = datetime.now()
    po_id = None
    
class Delivered_Item():
    di_id = None
    di_quantity = None
    di_expiry = None
    date_created = datetime.now()
    date_updated = datetime.now()
    dlr_id = None
    item_id = None

class Vendor():
    vnd_id = None
    vnd_name = None
    vnd_contact = None
    vnd_email = None

class Req_Item():
    ri_id = None
    ri_quantity = None
    date_created = datetime.now()
    date_updated = datetime.now()
    rq_id = None
    item_id = None
    ac_id = None
    
class Acknowledgment():
    ac_id = None
    ac_reciept = None
    date_created = datetime.now()
    date_updated = datetime.now()
    
class Item():
    item_id = None
    item_name = None
    item_type = None
    date_created = datetime.now()
    date_updated = datetime.now()
    unit_id = None

class Unit():
    unit_id = None
    unit_name = None
    

    
    