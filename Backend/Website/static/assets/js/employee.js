document.addEventListener("DOMContentLoaded", function () {
  const navbar = document.getElementById("navbar");

  // Select the list items you want to hide
  var itemsToHide = navbar.querySelectorAll(
    "li:nth-child(3), li:nth-child(5), li:nth-child(6), li:nth-child(7)"
  );

  emp_type = JSON.parse(sessionStorage.getItem("emp_data"))["emp_type"];

  if (emp_type === "EMP") {
    // Hide the selected list items
    itemsToHide.forEach(function (item) {
      item.style.display = "none";

      if (document.getElementById("btnInvaddItem"))
        document.getElementById("btnInvaddItem").style.display = "none";

      if (document.getElementById("btnJOBUPDATE"))
        document.getElementById("btnJOBUPDATE").style.display = "none";

      if (document.getElementById("btnCreatePO"))
        document.getElementById("btnCreatePO").style.display = "none";

      if (document.getElementById("btnRelease"))
        document.getElementById("btnRelease").style.display = "none";

      if (document.getElementById("requisition_update_goods_status"))
        document.getElementById(
          "requisition_update_goods_status"
        ).disabled = true;
      if (document.getElementById("requisition_update_job_status"))
        document.getElementById(
          "requisition_update_job_status"
        ).disabled = true;
    });
  }
});
