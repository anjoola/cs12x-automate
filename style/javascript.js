/**
 * Called on when the user selects a different student's graded output.
 *
 * @param student The student to change to.
 */
function changeStudent(student) {
  document.getElementById("name").innerHTML = student;
  var graded = document.getElementById("iframe-middle");
  var raw = document.getElementById("iframe-right");
  var assignment = document.getElementById("assignment").value;
  var file = document.getElementsByClassName("label-active")[0].innerHTML;
  graded.src = "files/" + student + "-" + file + ".html";
  raw.src = "../students/" + student + "-" + assignment + "/" + file;
}

/**
 * Change the raw file displayed.
 *
 * @param elem The button that was clicked on (needed in order to change color).
 * @param file The file to change to.
 */
function changeRawFile(elem, file) {
  var student = document.getElementById("name").innerHTML;
  var raw = document.getElementById("iframe-right");
  var assignment = document.getElementById("assignment").value;
  raw.src = "../students/" + student + "-" + assignment + "/" + file;

  // Change the active label to inactive.
  var active = document.getElementById("right")
                       .getElementsByClassName("label-active");
  for (var i = 0; i < active.length; i++) {
    active[i].className = "label";
  }

  // Change the inactive label to active.
  elem.className = "label-active label";
}

/**
 * Change the graded file displayed.
 *
 * @param elem The button that was clicked on (needed in order to change color).
 * @param file The file to change to.
 */
function changeGradedFile(elem, file) {
  var student = document.getElementById("name").innerHTML;
  var graded = document.getElementById("iframe-middle");
  graded.src = "files/" + student + "-" + file + ".html";

  // Change the active label to inactive.
  var active = document.getElementById("middle")
                       .getElementsByClassName("label-active");
  for (var i = 0; i < active.length; i++) {
    active[i].className = "label";
  }

  // Change the inactive label to active.
  elem.className = "label-active label";
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
