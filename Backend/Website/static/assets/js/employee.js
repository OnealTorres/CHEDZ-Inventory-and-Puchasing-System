function scrollDiv(direction) {
  var scrollableDiv = document.getElementById("item-table");
  var scrollAmount = 325; // Adjust the scroll amount as needed

  if (direction === "up") {
    scrollableDiv.scrollTop -= scrollAmount;
  } else if (direction === "down") {
    scrollableDiv.scrollTop += scrollAmount;
  }
}
