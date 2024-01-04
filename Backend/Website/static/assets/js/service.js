document.getElementById("btn_new_emp").addEventListener("click", () => {
  window.location.href = "/register";
});
async function POSTHandler(data, url, success, fail, msg_show) {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }

    // Check the content type of the response
    const contentType = response.headers.get("content-type");

    if (contentType && contentType.includes("application/json")) {
      const JSONdata = await response.json();
      if (msg_show) alert(success);
      return JSONdata;
    } else if (contentType && contentType.includes("application/pdf")) {
      // Assuming it's a PDF file, you can handle it as needed
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
      if (msg_show) alert(success);
      return null; // or whatever makes sense for your use case
    } else {
      // Handle other content types if needed
      if (msg_show) alert(fail);
      return null;
    }
  } catch (error) {
    if (msg_show) alert(fail);
    console.error(error);
    return null;
  }
}

/*
==============================
            LOGIN
==============================
*/
async function validateEmp() {
  //emp data
  const email = document.getElementById("inputEmail").value;
  const password = document.getElementById("inputPassword").value;
  if (email == "" || password == "") {
    alert("Please fill up all the fields");
    return;
  }
  const data = {
    emp_email: email,
    emp_password: password,
  };
  url = "/login/authenticate";
  success = "Login Successful!";
  fail = "Account does not exist";
  fetched_data = await POSTHandler(data, url, success, fail, true).then(
    async (fetched_data) => {
      // Code to execute when data is successfully fetched
      if (fetched_data) {
        // Set the session data
        sessionStorage.setItem("emp_data", JSON.stringify(fetched_data));
        console.log(fetched_data);
        // Navigate to the home page
        window.location.href = "/home";
      }
    }
  );
}

/*
==============================
         REGISTRATION
==============================
*/
async function registerEmp() {
  //emp data
  const fname = document.getElementById("firstName").value;
  const mname = document.getElementById("middleName").value;
  const lname = document.getElementById("lastName").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const conpassword = document.getElementById("confirmPassword").value;

  if (password != conpassword) {
    alert("Passwords does not match");
    return;
  } else if (
    fname == "" ||
    mname == "" ||
    lname == "" ||
    email == "" ||
    password == "" ||
    conpassword == ""
  ) {
    alert("Please fill up all the fields.");
    return;
  }
  const data = {
    emp_fname: fname,
    emp_mname: mname,
    emp_lname: lname,
    emp_email: email,
    emp_password: password,
  };
  url = "/register";
  success = "Registration Successful!";
  fail = "Registration Failed.";
  await POSTHandler(data, url, success, fail, true);
}
/*
==============================
          INVENTORY
==============================
*/
async function inventory_add_item() {
  const name = document.getElementById("inventory_add_name").value;
  const reorder = document.getElementById("inventory_add_reorder").value;
  const id = document.getElementById("inventory_add_unit").value;

  var type = "RAW";
  if (document.getElementById("rbtn_add_type_equipment").checked) {
    type = "EQUIPMENT";
  }
  if (name == "" || reorder == "") {
    alert("Please fill up all the fields.");
    return;
  } else {
    const data = {
      item_name: name,
      unit_id: id,
      item_reorder_lvl: reorder,
      item_type: type,
    };
    url = "/inventory/add-item";
    success = "Item successfully added!";
    fail = "Item failed to add.";
    await POSTHandler(data, url, success, fail, true);
    window.location.href = "/inventory";
  }
}

async function inventory_update_item() {
  const name = document.getElementById("inventory_update_item_name").value;
  const reorder = document.getElementById("inventory_update_reorder").value;
  const id = document.getElementById("inventory_update_unit").value;

  var type = "RAW";
  if (document.getElementById("rbtn_update_type_equipment").checked) {
    type = "EQUIPMENT";
  }
  if (name == "") {
    alert("Please fill up all the fields.");
    return;
  } else {
    const data = {
      item_name: name,
      unit_id: id,
      item_reorder_lvl: reorder,
      item_type: type,
    };
    const currentRoute = window.location.pathname;
    url = currentRoute;
    success = "Item successfully updated!";
    fail = "Item failed to update.";
    await POSTHandler(data, url, success, fail, true);
    window.location.href = "/inventory";
  }
}

async function inventory_search_item() {
  const searched_data = document.getElementById("inventory_search_name").value;
  if (searched_data == "") {
    window.location.href = "/inventory";
  } else {
    const data = {
      searched_data: searched_data,
    };
    window.location.href = "/inventory/search/" + searched_data;
  }
}
/*
==============================
          EMPLOYEE
==============================
*/
async function employee_search() {
  const searched_data = document.getElementById("employee_search_data").value;
  if (searched_data == "") {
    window.location.href = "/employee";
  } else {
    const data = {
      searched_data: searched_data,
    };
    window.location.href = "/employee/search/" + searched_data;
  }
}

async function create_emp() {
  //emp data
  const fname = document.getElementById("firstName").value;
  const mname = document.getElementById("middleName").value;
  const lname = document.getElementById("lastName").value;
  const email = document.getElementById("email").value;
  const type = document.getElementById("employee_add_type").value;
  const password = document.getElementById("password").value;
  const conpassword = document.getElementById("confirmPassword").value;

  if (password != conpassword) {
    alert("Passwords does not match");
    return;
  } else if (
    fname == "" ||
    mname == "" ||
    lname == "" ||
    email == "" ||
    password == "" ||
    conpassword == ""
  ) {
    alert("Please fill up all the fields.");
    return;
  }
  const data = {
    emp_fname: fname,
    emp_mname: mname,
    emp_lname: lname,
    emp_email: email,
    emp_password: password,
    emp_type: type,
  };
  url = "/employee/add-employee";
  success = "Employee successfully created!";
  fail = "Employee failed to create.";
  await POSTHandler(data, url, success, fail, true);
  window.location.href = "/employee";
}

async function update_emp() {
  //emp data
  const fname = document.getElementById("firstName").value;
  const mname = document.getElementById("middleName").value;
  const lname = document.getElementById("lastName").value;
  const email = document.getElementById("email").value;
  const type = document.getElementById("employee_update_position").value;
  const status = document.getElementById("employee_update_status").value;
  const password = document.getElementById("password").value;
  const conpassword = document.getElementById("confirmPassword").value;

  if (password != conpassword) {
    alert("Passwords does not match");
    return;
  } else if (
    fname == "" ||
    mname == "" ||
    lname == "" ||
    email == "" ||
    password == "" ||
    conpassword == ""
  ) {
    alert("Please fill up all the fields.");
    return;
  }
  const data = {
    emp_fname: fname,
    emp_mname: mname,
    emp_lname: lname,
    emp_email: email,
    emp_status: status,
    emp_password: password,
    emp_type: type,
  };
  const currentRoute = window.location.pathname;
  url = currentRoute;
  success = "Employee successfully updated!";
  fail = "Employee failed to update.";
  await POSTHandler(data, url, success, fail, true);
  window.location.href = "/employee";
}

/*
==============================
            VENDOR
==============================
*/
async function create_vendor() {
  //vendor data
  const name = document.getElementById("newVendorName").value;
  const contact = document.getElementById("newVendorContact").value;
  const email = document.getElementById("newVendorEmail").value;

  if (name == "" || contact == "" || email == "") {
    alert("Please fill up all the fields.");
    return;
  }
  const data = {
    vnd_name: name,
    vnd_contact: contact,
    vnd_email: email,
  };

  url = "/vendors/add";
  success = "Vendor successfully added!";
  fail = "Vendor failed to add.";
  await POSTHandler(data, url, success, fail, true);
  window.location.href = "/vendors";
}

async function update_vendor() {
  //vendor data
  const name = document.getElementById("vendor_update_name").value;
  const contact = document.getElementById("vendor_update_contact").value;
  const email = document.getElementById("vendor_update_email").value;

  if (name == "" || contact == "" || email == "") {
    alert("Please fill up all the fields.");
    return;
  }
  const data = {
    vnd_name: name,
    vnd_contact: contact,
    vnd_email: email,
  };
  const currentRoute = window.location.pathname;
  url = currentRoute;
  success = "Vendor successfully updated!";
  fail = "Vendor failed to update.";
  await POSTHandler(data, url, success, fail, true);
  window.location.href = "/vendors";
}
/*
==============================
          REQUISITION
==============================
*/
async function requisition_search() {
  const searched_data = document.getElementById(
    "requisition_search_data"
  ).value;
  if (isNaN(searched_data)) {
    alert("Please enter a valid requisition id.");
  } else if (searched_data == "") {
    window.location.href = "/requisitions/all";
  } else {
    const data = {
      searched_data: searched_data,
    };
    window.location.href = "/requisitions/all/search/" + searched_data;
  }
}

async function create_job_requisition() {
  //job req data
  const desc = document.getElementById("requisition_new_job_desc").value;

  if (desc == "") {
    alert("Please fill up all the fields.");
    return;
  }
  const data = {
    rq_type: "JOB",
    rq_desc: desc,
  };

  url = "/requisitions/new-requisition/job";
  success = "Request successfully added!";
  fail = "Request failed to create.";
  await POSTHandler(data, url, success, fail, true);
  window.location.href = "/requisitions";
}

async function create_goods_requisition() {
  //goods req data
  const desc = document.getElementById("requisition_new_goods_desc").value;

  var items = [];

  // Assuming your table has an id "hometable"
  var table = document.getElementById("hometable");

  // Assuming the first row contains the header and actual data starts from the second row
  for (var i = 1, row; (row = table.rows[i]); i++) {
    var item_id = row.cells[0].innerHTML;
    var item_quantity = row.cells[2].innerHTML;

    // Add the data to the items array
    items.push({
      item_id: item_id,
      item_quantity: item_quantity,
    });
  }

  if (desc == "") {
    alert("Please fill up all the fields.");
    return;
  } else if (items.length === 0) {
    alert("Please input some items.");
    return;
  }
  const data = {
    rq_desc: desc,
    items: items,
  };

  url = "/requisitions/new-requisition/goods";
  success = "Request successfully added!";
  fail = "Request failed to create.";
  await POSTHandler(data, url, success, fail, true);
  window.location.href = "/requisitions";
}

async function update_job_requisition() {
  //job req data
  const desc = document.getElementById("requisition_update_job_desc").value;
  const status = document.getElementById("requisition_update_job_status").value;

  if (desc == "") {
    alert("Please fill up all the fields.");
    return;
  }
  const data = {
    rq_status: status,
    rq_desc: desc,
  };

  const currentRoute = window.location.pathname;
  url = currentRoute;
  success = "Request successfully updated!";
  fail = "Request failed to be updated.";
  await POSTHandler(data, url, success, fail, true);
  window.location.href = "/requisitions";
}

async function update_goods_requisition() {
  //goods req data
  const status = document.getElementById(
    "requisition_update_goods_status"
  ).value;
  const fileInput = document.getElementById(
    "requisition_update_goods_ac_receipt"
  );
  var file = fileInput.files[0];

  // Check if the selected file is a PDF
  if (file && file.type !== "application/pdf") {
    alert("Selected file is not a PDF.");
    return;
  } else if (!file) {
    file = null;
  }

  const data = {
    rq_status: status,
    ac_receipt: file,
  };

  const formData = new FormData();
  formData.append("rq_status", status);
  formData.append("ac_receipt", file);

  const currentRoute = window.location.pathname;
  const url = currentRoute;
  const success = "Request successfully updated!";
  const fail = "Request failed to be updated.";
  fetch(url, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((result) => {
      alert(success);
      window.location.href = "/requisitions";
    })
    .catch((error) => {
      alert(fail);
      window.location.href = "/requisitions";
    });
}

async function create_purchasing_order(rq_id) {
  //goods req data
  const vendor = document.getElementById(
    "update_requisition_goods_create_vendor"
  ).value;

  const data = {
    vnd_id: vendor,
  };

  url = "/requisitions/update-requisition/goods/create-po/" + rq_id;
  success = "PO successfully created!";
  fail = "PO failed to be created.";
  await POSTHandler(data, url, success, fail, true);
  window.location.href = "/requisitions";
}

async function release_items(rq_id) {
  const data = {};

  url = "/requisitions/update-requisition/goods/release/" + rq_id;
  success = "Items successfully Released!";
  fail = "Not enough items in inventory.";
  await POSTHandler(data, url, success, fail, true);
  window.location.href = "/requisitions";
}

async function download_ac_receipt(rq_id) {
  const data = {};
  url =
    "/requisitions/update-requisition/goods/acknowledgement-receipt/" + rq_id;
  success = "";
  fail = "";
  await POSTHandler(data, url, success, fail, false);
}

/*
==============================
       PURCHASING ORDER
==============================
*/

async function purchasing_order_search_item() {
  const searched_data = document.getElementById("inventory_search_po_id").value;
  if (searched_data == "") {
    window.location.href = "/purchasing-order";
    return;
  } else if (isNaN(searched_data)) {
    alert("Please enter a valid purchasing order id.");
    return;
  } else {
    const data = {
      searched_data: searched_data,
    };
    window.location.href = "/purchasing-order/search/" + searched_data;
  }
}

async function insert_items_to_inventory(po_id) {
  var items = [];

  // Assuming your table has an id "hometable"
  var table = document.getElementById("hometable");

  // Assuming the first row contains the header and actual data starts from the second row
  for (var i = 1, row; (row = table.rows[i]); i++) {
    if (row.cells[6].innerHTML && row.cells[7].innerHTML) {
      var item_id = row.cells[1].innerHTML;
      console.log(item_id);
      var item_type = row.cells[5].innerHTML;
      var di_expiry = row.cells[6].innerHTML;
      var di_quantity = row.cells[7].innerHTML;
    } else {
      alert(
        "Please enter the expiry date and received quantity for all items."
      );
      return;
    }

    // Add the data to the items array
    items.push({
      di_expiry: di_expiry,
      di_quantity: di_quantity,
      item_id: item_id,
      item_type: item_type,
    });
  }

  const data = {
    items: items,
  };

  url = "/purchasing-order/update/insert-inventory/" + po_id;
  success = "Items successfully inserted!";
  fail = "Items failed to insert.";
  await POSTHandler(data, url, success, fail, true);
  window.location.href = "/purchasing-order";
}

async function purchasing_order_update_delivery() {
  const status = document.getElementById("requisition_update_po_status").value;
  const fileInput1 = document.getElementById("purchasing_order_po_quotation");
  const fileInput2 = document.getElementById("inputfileRM");
  var file1 = fileInput1.files[0];
  var file2 = fileInput2.files[0];

  // Check if the selected file is a PDF
  if (file1 && file1.type !== "application/pdf") {
    alert("Selected file is not a PDF.");
    return;
  } else if (!file1) {
    file1 = null;
  }

  // Check if the selected file is a PDF
  if (file2 && file2.type !== "application/pdf") {
    alert("Selected file is not a PDF.");
    return;
  } else if (!file2) {
    file2 = null;
  }

  const data = {
    po_status: status,
    po_quotation: file1,
    dlr_receiving_memo: file2,
  };

  const formData = new FormData();
  formData.append("po_status", status);
  formData.append("po_quotation", file1);
  formData.append("dlr_receiving_memo", file2);

  const currentRoute = window.location.pathname;
  const url = currentRoute;
  const success = "PO successfully updated!";
  const fail = "PO failed to be updated.";

  fetch(url, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((result) => {
      alert(success);
      console.log(result);
      window.location.href = "/purchasing-order";
    })
    .catch((error) => {
      alert(fail);
      window.location.href = "/purchasing-order";
    });
}

async function download_po_quotation(po_id) {
  const data = {};
  url = "/purchasing-order/update/generatePO/" + po_id;
  success = "";
  fail = "";
  await POSTHandler(data, url, success, fail, false);
}

async function download_receiving_memo(po_id) {
  const data = {};
  url = "/purchasing-order/update/createRM/" + po_id;
  success = "";
  fail = "";
  await POSTHandler(data, url, success, fail, false);
}

function addItemQuantityReceived(
  tbItemId,
  itemName,
  diExpiry,
  diQuantity,
  rowID
) {
  const rowIndex = parseInt(rowID, 10);
  document.getElementById("itemID").value = tbItemId;
  document.getElementById("itemName").value = itemName;
  document.getElementById("itemExpiryDate").value = diExpiry;
  document.getElementById("diQuantity").value = parseInt(diQuantity);
  document.getElementById("rowID").value = rowIndex;
}

function updateTableRow() {
  // Get values from the modal
  const itemID = document.getElementById("itemID").value;
  const rowIndex = document.getElementById("rowID").value;
  const diExpiry = document.getElementById("itemExpiryDate").value;
  const diQuantity = document.getElementById("diQuantity").value;

  const inputDate = new Date(diExpiry);
  const currentDate = new Date();

  if (!diExpiry || !diQuantity) {
    alert("Please fill out all of the fields.");
    return;
  } else if (diQuantity < 0) {
    alert("Invalid item quantity.");
    return;
  } else if (inputDate < currentDate) {
    alert("The inputted date is in the past.");
    return;
  } else if (inputDate.toDateString() === currentDate.toDateString()) {
    alert("The inputted date is today.");
    return;
  }

  // Find the corresponding row in the table by its ID
  const tableRow = document.getElementById(rowIndex);

  if (tableRow) {
    // Update the values in the specific row
    const columns = tableRow.getElementsByTagName("th");

    // Assuming the 6th and 7th columns are for diExpiry and diQuantity respectively
    columns[6].innerText = diExpiry;
    columns[7].innerText = diQuantity;
  }
}

/*
==============================
          DELIVERY
==============================
*/

async function delivery_search() {
  const searched_data = document.getElementById("delivery_search_data").value;
  if (isNaN(searched_data)) {
    alert("Please enter a valid requisition id.");
  } else if (searched_data == "") {
    window.location.href = "/delivery";
  } else {
    window.location.href = "/delivery/search/" + searched_data;
  }
}

async function delivery_update() {
  const status = document.getElementById("delivery_update_dlr_status").value;
  const fileInput = document.getElementById("delivery_dlr_receipt");
  var file = fileInput.files[0];

  // Check if the selected file is a PDF
  if (file && file.type !== "application/pdf") {
    alert("Selected file is not a PDF.");
    return;
  } else if (!file) {
    file = null;
  }

  const data = {
    dlr_status: status,
    dlr_receipt: file,
  };
  const formData = new FormData();
  formData.append("dlr_status", status);
  formData.append("dlr_receipt", file);
  console.log(status);
  const currentRoute = window.location.pathname;
  const url = currentRoute;
  const success = "Delivery successfully updated!";
  const fail = "Delivery failed to be updated.";

  fetch(url, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((result) => {
      alert(success);
      console.log(result);
      window.location.href = "/delivery";
    })
    .catch((error) => {
      alert(fail);
      console.log(error);
      window.location.href = "/delivery";
    });
}

async function download_delivery_receipt(dlr_id) {
  const data = {};
  url = "/delivery/update/delivery-receipt/" + dlr_id;
  success = "";
  fail = "";
  await POSTHandler(data, url, success, fail, false);
  window.location.href = "/delivery";
}

/*
==============================
            REPORT
==============================
*/

async function report_search_year() {
  const searched_data = document.getElementById("year_picker").value;
  window.location.href = "/report/search/" + searched_data;
}

function logout() {
  sessionStorage.clear();
}
