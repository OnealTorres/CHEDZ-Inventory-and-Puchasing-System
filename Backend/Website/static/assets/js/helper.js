function requisition_change_drp() {
  const raw_is_checked = document.getElementById(
    "requisition_type_equipment"
  ).checked;

  if (raw_is_checked) {
    document.getElementById("drp_equipment").style.display = "block";
    document.getElementById("drp_raw").style.display = "none";
    requisition_change_drp_unit();
  } else {
    document.getElementById("drp_equipment").style.display = "none";
    document.getElementById("drp_raw").style.display = "block";
    requisition_change_drp_unit();
  }
}
function new_goods_insert_table() {
  if (document.getElementById("requisition_quantity").value == "") {
    alert("Please fill out all the fields.");
    return;
  }

  const raw_is_checked = document.getElementById(
    "requisition_type_equipment"
  ).checked;
  var item = null;
  var item_id = null;
  var item_name = null;
  var unit_name = null;
  var type = "RAW";
  var quantity = document.getElementById("requisition_quantity").value;

  if (raw_is_checked) {
    item = document.getElementById("drp_equipment_item").value;
    var dropdown = document.getElementById("drp_equipment_item");
    item_name = dropdown.options[dropdown.selectedIndex].text;
    item_id = item.split(",")[0].replace("(", "").replace(" ", "");
    type = "EQUIPMENT";
    unit_name = item
      .split(",")[1]
      .replace(")", "")
      .replace(" ", "")
      .replaceAll("'", "");
  } else {
    item = document.getElementById("drp_raw_item").value;
    item_id = item.split(",")[0].replace("(", "").replace(" ", "");
    var dropdown = document.getElementById("drp_raw_item");
    item_name = dropdown.options[dropdown.selectedIndex].text;
    type = "RAW";
    unit_name = item
      .split(",")[1]
      .replace(")", "")
      .replace(" ", "")
      .replaceAll("'", "");
  }

  table = document.getElementById("hometable");
  // Create a new row
  var newRow = table.insertRow();

  // Insert cells into the new row
  var cell1 = newRow.insertCell(0);
  var cell2 = newRow.insertCell(1);
  var cell3 = newRow.insertCell(2);
  var cell4 = newRow.insertCell(3);
  var cell5 = newRow.insertCell(4);

  // Set class name for each cell
  cell1.className = "tb-row";
  cell2.className = "tb-row";
  cell3.className = "tb-row";
  cell4.className = "tb-row";
  cell5.className = "tb-row";

  // Set content for each cell (you can modify this based on your needs)
  cell1.innerHTML = item_id;
  cell2.innerHTML = item_name;
  cell3.innerHTML = quantity;
  cell4.innerHTML = unit_name;
  cell5.innerHTML = type;
}

function requisition_change_drp_unit() {
  const raw_is_checked = document.getElementById(
    "requisition_type_equipment"
  ).checked;
  var item = null;
  var item_id = null;
  var item_name = null;
  var unit_name = null;

  if (raw_is_checked) {
    item = document.getElementById("drp_equipment_item").value;
    var dropdown = document.getElementById("drp_equipment_item");
    item_name = dropdown.options[dropdown.selectedIndex].text;
    item_id = item.split(",")[0].replace("(", "").replace(" ", "");
    unit_name = item
      .split(",")[1]
      .replace(")", "")
      .replace(" ", "")
      .replaceAll("'", "");
    document.getElementById("requisition_unit_name").value = unit_name;
  } else {
    item = document.getElementById("drp_raw_item").value;
    var dropdown = document.getElementById("drp_equipment_item");
    item_name = dropdown.options[dropdown.selectedIndex].text;
    item_id = item.split(",")[0].replace("(", "").replace(" ", "");
    unit_name = item
      .split(",")[1]
      .replace(")", "")
      .replace(" ", "")
      .replaceAll("'", "");

    document.getElementById("requisition_unit_name").value = unit_name;
  }
}

function captureAndConvertToPDF(element_id, file_name) {
  const element = document.querySelector("#" + element_id);
  const button = (document.getElementById("btn_capture").style.display =
    "none");

  const options = {
    filename: file_name + ".pdf",
    margin: 0,
    image: { type: "jpeg", quality: 0.98 }, // Adjust quality as needed
    html2canvas: {
      scale: 2, // Adjust scale as needed
      width: 830, // Use the width of the element
      dpi: 800,
    },

    jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
  };

  html2pdf().set(options).from(element).save();
}

// Get the select element
var yearSelect = document.getElementById("year_picker");

// Check if the element exists before populating the dropdown
if (yearSelect) {
  // gets the current year
  var currentTime = new Date();
  var month = currentTime.getMonth() + 1;
  var day = currentTime.getDate();
  var cur_year = currentTime.getFullYear();

  // Populate the dropdown with years from 2000 to 2500
  for (var year = 2000; year <= 2500; year++) {
    var option = document.createElement("option");
    if (year == cur_year) {
      option.selected = true;
    }
    option.value = year;
    option.text = year;
    yearSelect.add(option);
  }
}
