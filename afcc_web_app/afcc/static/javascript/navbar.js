"use strict";

function hamburgerMenu() {

  console.log("test");  
  var navbar = document.getElementsByClassName("navbar")[0];
  var hamburgerButtonLines = document.getElementsByClassName("button-hamburger--line");

  navbar.classList.toggle("--hidden-on-mobile");

  for (var i = 0; i < hamburgerButtonLines.length; i++) {
    hamburgerButtonLines[i].classList.toggle("--toggled-on");
  }
}

function dropdownMenu() {
  var accountDropdown = document.getElementById("accountDropdown");

  accountDropdown.classList.toggle("show")
}

window.onclick = function(e) {
  if (!e.target.matches('.dropbtn')) {
  var accountDropdown = document.getElementById("accountDropdown");
    if (accountDropdown.classList.contains('show')) {
      accountDropdown.classList.remove('show');
    }
  }
}
