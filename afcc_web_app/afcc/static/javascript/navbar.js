"use strict";

function dropdownMenu() {
  var navbar = document.getElementsByClassName("navbar")[0];
  var hamburgerButtonLines = document.getElementsByClassName("button-hamburger--line");

  navbar.classList.toggle("--hidden");

  for (var i = 0; i < hamburgerButtonLines.length; i++) {
    hamburgerButtonLines[i].classList.toggle("--toggled-on");
  }
}
