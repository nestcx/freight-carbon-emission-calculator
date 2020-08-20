/**
 * This script is used to send asynchronous requests to the web server and to suggest 
 * addresses to the user based on what they've already typed
 */

var startLocInput = document.getElementById("input-pick-up");
var endLocInput = document.getElementById("input-drop-off");

startLocInput.addEventListener("input", searchPossibleAddresses);
endLocInput.addEventListener("input", searchPossibleAddresses);

var selectedAddress = null;

var mapOfAddresses;

/**
 * Search all the possible addresses so far based on what the user has inputted.
 * @param {Event} e The fired event that called this function
 */
function searchPossibleAddresses(e) {
  inputField = e.target;

  /**
   * Only bother trying to autosuggest if the user has entered more than 4 characters,
   * otherwise the search space is too large to provide a likely guess of what address the
   * user is looking for
   */
  if (inputField.value.length > 4) {
    
    /**
     * Send an asychronous request to the server, adding the user's input so far as an argument.
     * See if the server responds, and if so, have that data processed
     */
    axios.get("/search/address", {
      params: {
        input: inputField.value
      }
    })
    .then(function (response) { // Successfully responded
      allAddresses = filterAddressData(response.data);
      createAutoSuggestTextBox(allAddresses, inputField);
    })
    .catch(function (error) {
      console.log(error);
      // TODO: Handle error here
    })
    .then(function () { // always executed
      // Nothing for now
    }); 
  } else if (inputField.value.length == 0) { // The user has removed all the input, therefore destroy the autosuggest box
    closeAutoSuggest();
  }
}


/**
 * Pull all the addresses and coordinates from the JSON data and place them in a Map data structure.
 * @param {JSON} json The raw JSON data that will be parsed 
 * @returns {Map} A Map data structure which stores addresses and coordinates in {key, value} pairs
 */
function filterAddressData(json) {
  /**
   * Use a Map data structure, as a Map in JS is similar to a dictionary data structure.
   * Use it to store coordinates and addresses in {key, value} pairs
   */
  mapOfAddresses = new Map(); 

  /**
   * Limit how many addresses will be shown to the user. This is to avoid showing too many
   * addresses, which will clutter the screen. The user in response will continue typing
   * until the search is more refined. In this case, don't show more than 6 addresses,
   * which seems to be the standard amount to show to a user.
   */
  for (var i = 0; i < json["features"].length; i++) {

    if (i == 6) break;

    var long = json["features"][i]["geometry"]["coordinates"][0];
    var lat = json["features"][i]["geometry"]["coordinates"][1];
    var coords =  [long, lat];

    var addressString = json["features"][i]["properties"]["label"];

    /**
     * The name of the address is set as the key so that we can retrieve the coordinates
     * by passing in an address name
     */
    mapOfAddresses.set(addressString, coords);
  }

  return mapOfAddresses;
}


/**
 * Create the autosuggest box underneath the input field via DOM manipulation.
 * @param {map} addresses The map data structure that stores addresses and their coordinates
 * @param {element} inputField The inputfield that the autosuggest box element should be created under
 */
function createAutoSuggestTextBox(addresses, inputField) {

  // Get the parent div element so that the autosuggestbox can be appended to it
  var parentDiv = document.getElementsByClassName("container--location-inputs")[0];

  // Check if a suggestionbox already exists, and if so, delete it so it can be replaced with a new one
  if (document.getElementById("autosuggestBox")) {
    closeAutoSuggest();
  }

  // Create the autosuggest element
  var autoSuggest = document.createElement("div");
  autoSuggest.classList.add("autosuggestbox"); // Add this class so that it is styled according to the SCSS file
  autoSuggest.id = "autosuggestBox";

  /**
   * Get the rectangle bounds of the input field so that the width of the autosuggest element 
   * will match that of the input field.
   */
  var inputFieldRect = inputField.getBoundingClientRect();
  autoSuggest.style.width = inputFieldRect.width + "px"; // Make autosuggest element's width the same as the input field
  autoSuggest.style.maxWidth = inputFieldRect.width + "px";

  // Insert the autosuggestbox just after the input field in the DOM
  parentDiv.insertBefore(autoSuggest, inputField.nextSibling)

  // Populate the autosuggest element with all the addresses found. They key is
  // the address name, which will be inserted as a text node
  addresses.forEach(function(value, key) {
    var text = document.createElement("p");
    text.classList.add("autosuggest__address");
    address = document.createTextNode(key);
    text.appendChild(address);
    autoSuggest.appendChild(text);
  });

  addAutoSuggestNavigation(autoSuggest);
}


function addAutoSuggestNavigation(autoSuggest) {
  document.addEventListener("keydown", handleKeyNavigation);
  autoSuggest.addEventListener("mouseover", handleHover);
  document.addEventListener("mousedown", handleClicks);
}


/**
 * Handle clicks on 
 * @param {} e The eventlistener that fired 
 */
function handleClicks(e) {
  // If the user clicked on an address within the autosuggest element, automatically
  // change the input field's value to that
  if (e.target.classList.contains("autosuggest__address")) {
    selectedAddress = e.target;
    var inputField = e.target.parentElement.previousSibling;
    inputField.value = selectedAddress.innerHTML;
    
    // Get the coordinate of that particular address, so that it can be fed to the Leafleft ap API
    var coordOfAddress = mapOfAddresses.get(selectedAddress.innerHTML);

    // Check if the current selected input field is the starting address. This is done so that
    // the interactivemap.js script can understand whether its the starting address or not
    var startingAddress = false;
    if (inputField.id == "input-pick-up") {
      startingAddress = true;
    };
    
    // coordofAddress[0] is the longitude, while [1] is the latitude - the order that OpenRouteService uses.
    // Leaflet handles coordinates in [lat, long] order so pass in the arguments as so.
    addMarkerToMap(coordOfAddress[1], coordOfAddress[0], startingAddress);


    closeAutoSuggest();
  }
  else { // The user clicked outside of the autosuggest element, therefore remove the autosuggest box
    closeAutoSuggest();
  }

}

/**
 * Handle when a user hovers over an address. This is used just to provide the user
 * with visual feedback.
 * @param {*} e The eventlistener that fired. 
 */
function handleHover(e) {
  if (e.target.classList.contains("autosuggest__address")) {
    selectedAddress = e.target;
    highlightAddress(selectedAddress);
  }
}


/**
 * For accessibility reasons, allow the user to choose an address using the keyboard
 * by handling key presses
 * @param {*} e 
 */
function handleKeyNavigation(e) {
  var autoSuggest = document.getElementById("autosuggestBox");

  // Allow the user to escape by hitting the escape button
  if (e.key == "Escape") {
    closeAutoSuggest();
    return;
  }
  else if (e.key == "ArrowDown") { // Down key  
    if (selectedAddress == null) {
      // No address is currently highlighted, therefore make highlight the top-most address.
      selectedAddress = autoSuggest.childNodes[0];
    } else if (selectedAddress.nextSibling === undefined || selectedAddress.nextSibling === null) { 
      /**
       * The current highlighted address is the bottom-most address in the autosuggest box,
       * therefore move back up to the top of the list and highlight the first address.
       */
      selectedAddress = autoSuggest.childNodes[0]; // Go back to the top
    } else {
      selectedAddress = selectedAddress.nextSibling; // Move one down
    }

    highlightAddress(selectedAddress);
  }
  else if (e.key == "ArrowUp") {
    if (selectedAddress == null) {
      selectedAddress = autoSuggest.childNodes[autoSuggest.childNodes.length - 1];
    } else if (selectedAddress.previousSibling === undefined || selectedAddress.previousSibling === null) { 
      /**
       * The current highlighted address is the top-most address in the autosuggest box,
       * therefore move back down to the bottom of the list and highlight the last address.
       */
      selectedAddress = autoSuggest.childNodes[autoSuggest.childNodes.length - 1]; // Go back to the top
    } else {
      selectedAddress = selectedAddress.previousSibling; // Move one down
    }

    highlightAddress(selectedAddress);
  }
  else if (e.key == "Enter") {
    /**
     * If a user hits enter, that means they want to select the address that is currently highlighted
     */
    if (selectedAddress != null) {
      e.target.value = selectedAddress.innerHTML;
      closeAutoSuggest();
    }
  }
}


/**
 * Highlight an address to provide visual feedback to the user as they press the down or up keys.
 * @param {DOM Element} newAddress The address in the autosuggest box that will be highlighted 
 */
function highlightAddress(newAddress) {

  // First remove highlighting on all addresses by removing the --active class name, then proceed.
  var listOfAutosuggestedAddress = document.getElementsByClassName("autosuggest__address");
  
  for (var i = 0; i < listOfAutosuggestedAddress.length; i++) {
    if (listOfAutosuggestedAddress[i].classList.contains("autosuggestbox--active")) {
      listOfAutosuggestedAddress[i].classList.remove("autosuggestbox--active");
    }
  }
  
  // Add the --active class name, which will then style the address according to the CSS rules 
  newAddress.classList.add("autosuggestbox--active");
}


/**
 * Remove the Autosuggest element from the DOM, as well removing the eventlisteners
 */
function closeAutoSuggest() {
  if (document.getElementById("autosuggestBox")) {
    
    document.addEventListener("keydown", handleKeyNavigation);
    document.getElementById("autosuggestBox").removeEventListener("mouseover", handleHover);
    document.removeEventListener("mousedown", handleClicks);

    var parentDiv = document.getElementsByClassName("container--location-inputs")[0];
    parentDiv.removeChild(document.getElementById("autosuggestBox"));
  }

  selectedAddress = null;
}

