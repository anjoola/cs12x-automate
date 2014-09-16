/**
 * Called on when the user selects a different student's graded output.
 *
 * @param student The student to change to.
 */
function changeStudent(student) {
  document.getElementById("name").innerHTML = student;
  var graded = document.getElementById("iframe-graded");
  var raw = document.getElementById("iframe-raw");
  var assignment = document.getElementById("assignment").value;
  var file = document.getElementsByClassName("label-active")[0].innerHTML;
  graded.src = "files/" + student + "-" + file + ".html";
  raw.src = "../students/" + student + "-" + assignment + "/" + file + ".html";
}

/**
 * Change graded file displayed.
 *
 * @param elem The button that was clicked on (needed in order to change color).
 * @param file The file to change to.
 */
function changeFile(elem, file) {
  var student = document.getElementById("name").innerHTML;
  var graded = document.getElementById("iframe-graded");
  graded.src = "files/" + student + "-" + file + ".html";

  var assignment = document.getElementById("assignment").value;
  var raw = document.getElementById("iframe-raw");
  raw.src = "../students/" + student + "-" + assignment + "/" + file + ".html";

  // Change the active label to inactive.
  var active = document.getElementById("title")
                       .getElementsByClassName("label-active");
  for (var i = 0; i < active.length; i++) {
    active[i].className = "label";
  }

  // Change the inactive label to active.
  elem.className = "label-active label";
}

/**
 * Hide raw files.
 */
function hideRaw() {
  var toggle = document.getElementById("hide-raw");
  toggle.style.display = "none";

  toggle = document.getElementById("show-raw");
  toggle.style.display = "block";

  raw = document.getElementById("raw");
  raw.style.display = "none";

  graded = document.getElementById("graded");
  graded.style.width = "100%";
}

/**
 * Show raw files.
 */
function showRaw() {
  var toggle = document.getElementById("show-raw");
  toggle.style.display = "none";

  toggle = document.getElementById("hide-raw");
  toggle.style.display = "block";

  raw = document.getElementById("raw");
  raw.style.display = "block";

  graded = document.getElementById("graded");
  graded.style.width = "";
}

/**                                                                                         
 * Toggle the graded problem results.
 *
 * @param id The ID of the div displaying the results.
 */
function toggle(id) {
  var div = document.getElementById(id);
  if (div.style.display == "none")
    div.style.display = "block";
  else
    div.style.display = "none";
}
