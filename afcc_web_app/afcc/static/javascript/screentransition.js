"use strict";

/**
 * Change screen to the screen passed in as an argument. Add a little
 * transition effect
 * @param {element} outScreen The Id of screen div that's being transitioned out of
 * @param {element} inScreen The Id of div element of the screen to transition to 
 */
function changeScreen(outScreen, inScreen) {
  console.log(inScreen);

  var currentScreen = document.getElementById(outScreen);
  var nextScreen = document.getElementById(inScreen);
  
  //var datascreencharts = document.getElementById('screen-data-page-charts');
  //var allscreencharts= document.getElementById('all-screen-charts');

  currentScreen.classList.add("--screen-inactive");
  nextScreen.classList.remove("--screen-inactive");


  // Now change which link is highlighted in the sidebar to reflect which page the user is on
  var linkToHighlight = "sidebarlink-" + nextScreen.id;
  document.getElementById(linkToHighlight).classList.add("--active");

  var linkToNormalise = "sidebarlink-" + currentScreen.id;
  document.getElementById(linkToNormalise).classList.remove("--active");

  // Get the first input element in the screen, if one exists, and put the element
  // in focus. This way the user doesn't have to waste time click on the first input
  var firstInputField = document.querySelector("#" + nextScreen.id + " input");
  if (firstInputField != null && firstInputField != undefined) {
    firstInputField.focus();
  }

  // Scroll to the top of any scrollable divs - for better usability.
  var pageModules = nextScreen.getElementsByClassName('module--container');
  [].forEach.call(pageModules, function(pageModule, index) {
    pageModule.scrollTop = 0;
  });
}


/**
 * Go to the screen passed in as an argument. This function is called when
 * the previous screen's id isn't known.
 * @param {element} nextScreenId The Id of div element of the screen to transition to 
 */
function goToScreen(nextScreenId) {
  
  var idOfActiveScreen;
  
  // Iterate through all screens aka pages to find which one is currently active
  [].forEach.call(document.getElementsByClassName('dashboard--page'), function(screen, index) {

    // Find the screen that is currently active     
    if (!(screen.classList.contains('--screen-inactive'))) {
      idOfActiveScreen = screen.id;
    }
  });

  
  changeScreen(idOfActiveScreen, nextScreenId);
}