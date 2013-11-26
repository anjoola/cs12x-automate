function changeStudent(student) {
  document.getElementById("name").innerHTML = student;
  var graded = document.getElementById("iframe-middle");
  var raw = document.getElementById("iframe-right");
  var assignment = document.getElementById("assignment").value;
  var file = document.getElementsByClassName("label-active")[0].innerHTML;
  graded.src = student + "-" + file + ".html";
  raw.src = "../" + student + "-" + assignment + "/" + file;
}


function changeRawFile(elem, file) {
  var student = document.getElementById("name").innerHTML;
  var raw = document.getElementById("iframe-right");
  var assignment = document.getElementById("assignment").value;
  raw.src = "../" + student + "-" + assignment + "/" + file;
  
  // Change the active label to inactive.
  var active = document.getElementById("right").getElementsByClassName("label-active");
  for (var i = 0; i < active.length; i++) {
    active[i].className = "label";
  }

  elem.className = "label-active label";
}

function changeGradedFile(elem, file) {
  var student = document.getElementById("name").innerHTML;
  var graded = document.getElementById("iframe-middle");
  graded.src = student + "-" + file + ".html";

  // Change the active label to inactive.
  var active = document.getElementById("middle").getElementsByClassName("label-active");
  for (var i = 0; i < active.length; i++) {
    active[i].className = "label";
  }

  elem.className = "label-active label";
}

function toggle(id) {
  var div = document.getElementById(id);
  if (div.style.display == "none")
    div.style.display = "block";
  else
    div.style.display = "none";
}