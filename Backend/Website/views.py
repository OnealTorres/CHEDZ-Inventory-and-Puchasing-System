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

@views.route('/inventory/add-item/save')
def inventoryAddItemSave():
    return '<script>alert("hello auth")</script>'

@views.route('/inventory/update-item')
def inventoryUpdateItemSave():
    return '<script>alert("hello auth")</script>'

@views.route('/inventory/update-item/save')
def inventoryUpdateItemSave():
    return '<script>alert("hello auth")</script>'


#===============================
#           EMPLOYEE
#===============================

@views.route('/employee')
def employee():
    return '<script>alert("hello auth")</script>'

@views.route('/employee/add-employee')
def employeeAdd():
    return '<script>alert("hello auth")</script>'

@views.route('/employee/add-employee/save')
def employeeAddSave():
    return '<script>alert("hello auth")</script>'

@views.route('/employee/update-employee')
def employeeUpdate():
    return '<script>alert("hello auth")</script>'

@views.route('/employee/update-employee/save')
def employeeUpdateSave():
    return '<script>alert("hello auth")</script>'

#===============================
#         REQUISITIONS
#===============================

@views.route('/requisitions')
def requisitions():
    return '<script>alert("hello auth")</script>'

@views.route('/requisitions/new-requisition')
def requisitionsNew():
    return '<script>alert("hello auth")</script>'

@views.route('/requisitions/new-requisition/job')
def requisitionsNewJob():
    return '<script>alert("hello auth")</script>'

@views.route('/requisitions/new-requisition/job/save')
def requisitionsNewJobSave():
    return '<script>alert("hello auth")</script>'

@views.route('/requisitions/update-requisition/job')
def requisitionsNewJob():
    return '<script>alert("hello auth")</script>'

@views.route('/requisitions/update-requisition/job-save')
def requisitionsNewJob():
    return '<script>alert("hello auth")</script>'

@views.route('/requisitions/new-requisition/goods')
def requisitionsNewGoods():
    return '<script>alert("hello auth")</script>'

@views.route('/requisitions/new-requisition/goods/save')
def requisitionsNewGoodsSave():
    return '<script>alert("hello auth")</script>'

@views.route('/requisitions/update-requisition/goods')
def requisitionsNewGoods():
    return '<script>alert("hello auth")</script>'

@views.route('/requisitions/update-requisition/goods/save')
def requisitionsNewGoods():
    return '<script>alert("hello auth")</script>'