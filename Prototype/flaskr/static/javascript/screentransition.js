"use strict";

/**
 * Change screen to the screen passed in as an argument. Add a little
 * transition effect
 * @param {element} outScreen The Id of screen div that's being transitioned out of
 * @param {element} inScreen The Id of div element of the screen to transition to 
 */
function changeScreen(outScreen, inScreen) {

  var currentScreen = document.getElementById(outScreen);
  var nextScreen = document.getElementById(inScreen);
  
  currentScreen.classList.add("--screen-inactive");
  nextScreen.classList.remove("--screen-inactive");

  // Get the first input element in the screen, if one exists, and put the element
  // in focus. This way the user doesn't have to waste time click on the first input
  var firstInputField = document.querySelector("#" + nextScreen.id + " input");
  if (firstInputField != null && firstInputField != undefined) {
    firstInputField.focus();
  }
}