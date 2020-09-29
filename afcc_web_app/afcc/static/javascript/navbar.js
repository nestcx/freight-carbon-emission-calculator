"use strict";

function hamburgerMenu() {

  var navbar = document.getElementsByClassName("navbar")[0];
  var hamburgerButtonLines = document.getElementsByClassName("button-hamburger--line");

  navbar.classList.toggle("--hidden-on-mobile");
  document.addEventListener('click', clickedOutOfNavbar);

  for (var i = 0; i < hamburgerButtonLines.length; i++) {
    hamburgerButtonLines[i].classList.toggle("--toggled-on");
  }
}

function dropdownMenu() {
  var accountDropdown = document.getElementById("accountDropdown");
  accountDropdown.classList.toggle("--show-content");
}

/**
 * Check to see if a user has clicked outside of the navbar. This function
 * will only be called by the eventlistener that is created when the hamburger
 * button is clicked.
 * @param {event} e The event that was fired 
 */
function clickedOutOfNavbar(e) {
  var navbar = document.getElementsByClassName("navbar")[0];
  var hamburgerButton = document.getElementsByClassName("button-hamburger")[0];

  // If the user clicked outside of the hamburger button or navbar menu,
  // they probably want it to close.
  if (!(navbar.contains(e.target) || hamburgerButton.contains(e.target))) {
    //console.log('the clicked target is OUTSIDE navbar or hamburger button');

    // The navbar will always be open if this code is reached, since the eventlistener
    // only exists when the navbar is open. Therefore, toggle is effectively the same
    // as remove class name
    navbar.classList.toggle("--hidden-on-mobile");
    
    // Delete the event listener that fired this function.
    document.removeEventListener('click', clickedOutOfNavbar);
    
    var hamburgerButtonLines = document.getElementsByClassName("button-hamburger--line");
    for (var i = 0; i < hamburgerButtonLines.length; i++) {
      hamburgerButtonLines[i].classList.toggle("--toggled-on");
    }
  }

}

window.onclick = function(e) {
  // Get the parent element, so that we can check if the user clicked anywhere within
  // the drop down menu or user icons
  var accountDropdownParent = document.getElementById("user-account-links-container");

  // If user clicked outside of the dropdown menu buttons
  if (!accountDropdownParent.contains(e.target)) {
    var accountDropdown = document.getElementById("accountDropdown");
    if (accountDropdown.classList.contains('--show-content')) {
      accountDropdown.classList.remove('--show-content');
    }
  }


}
