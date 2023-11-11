from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return '<script>alert("hello auth")</script>'


#===============================
#           INVENTORY
#===============================

@views.route('/inventory')
def inventory():
    return '<script>alert("hello auth")</script>'

@views.route('/inventory/near-expiry')
def inventoryExpiry():
    return '<script>alert("hello auth")</script>'

@views.route('/inventory/add-item')
def inventoryAddItem():
    return '<script>alert("hello auth")</script>'

@views.route('/inventory/add-item-save')
def inventoryAddItemSave():
    return '<script>alert("hello auth")</script>'

@views.route('/inventory/update-item')
def inventoryUpdateItemSave():
    return '<script>alert("hello auth")</script>'

@views.route('/inventory/update-item-save')
def inventoryUpdateItemSave():
    return '<script>alert("hello auth")</script>'


#===============================
#           EMPLOYEE
#===============================

@views.route('/employee')
def employee():
    return '<script>alert("hello auth")</script>'

@views.route('/employee/employee-add')
def employeeAdd():
    return '<script>alert("hello auth")</script>'

@views.route('/employee/employee-add-confirm')
def employeeAddSave():
    return '<script>alert("hello auth")</script>'

@views.route('/employee/employee-update')
def employeeUpdate():
    return '<script>alert("hello auth")</script>'

@views.route('/employee/employee-update-save')
def employee():
    return '<script>alert("hello auth")</script>'