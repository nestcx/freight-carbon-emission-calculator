/**
 * This script is used to display an interactive map to the user
 */

/**
 * By default have the map centred on Melbourne by passing in Melbourne's coordinates.
 * Note that unlike the OpenRouteService API, this API orders the coordinates in [latitude, longitude] order.
 */

var interactiveMap = L.map('mapid').setView([-37.8136, 144.9631], 13);

// DO NOT REMOVE THE ATTRIBUTION. We are required to credit OpenStreetMap as per their copyright license
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',    
  maxZoom: 19
}).addTo(interactiveMap);

var startMarker = null;
var endMarker = null;

function addMarkerToMap(lat, long, startingAddress) {
  
  if (startingAddress === true) {

    // If a starting marker was already placed, and the user entered a new starting
    // address, remove the old one
    if (startMarker !== undefined && startMarker !== null) {
      interactiveMap.removeLayer(startMarker);
    }
    startMarker = L.marker([lat, long]).addTo(interactiveMap);

  } else if (startingAddress === false) {

    // If a destination marker was already placed, and the user entered a new destination
    // address, remove the old one
    if (endMarker !== undefined && endMarker !== null) {
      interactiveMap.removeLayer(endMarker);
    }
    endMarker = L.marker([lat, long]).addTo(interactiveMap);
  }
  
  interactiveMap.panTo([lat, long]);


  // If the user has added a start and end location, get the route
  // by calling our own API
  if (startMarker !== null && endMarker !== null) {

    /**
     * Get the coordinate data from the marker objects and store it as a string so it can easily
     * be passed in as parameters as part of the GET request. Note that OpenRouteService and therefore our own
     * API accepts coordinates in [long, lat] form, while Leaflet uses [lat, long] form. 
     * Therefore, flip the latitude and longitude around to [long, lat] since we're calling OpenRouteService's API now.
     */  
    var startMarkerCoords = startMarker._latlng["lng"] + "," + startMarker._latlng["lat"];
    var endMarkerCoords = endMarker._latlng["lng"] + "," + endMarker._latlng["lat"];

    /**
     * Send an asychronous request to the server, passing in the coordinates as arguments
     */
    axios.get("/maproutes/route", {
      params: {
        startCoords: startMarkerCoords,
        endCoords: endMarkerCoords
      }
    })
    .then(function (response) { // Successfully responded
      console.log(response.data);
      displayRouteOnMap(response.data);
    })
    .catch(function (error) {
      console.log(error);
      // TODO: Handle error here
    })
    .then(function () { // always executed
      // Nothing for now
    });
  }
}

/*
 * Global variable to store the currently displayed route. This is done so that
 * if a user enters start and destination addresses, and then reenters a new 
 * address to any of the fields, the old route can be found and removed from the map
 */
var currentlyDisplayedRoute = null;

function displayRouteOnMap(geoJSON) {
  interactiveMap.invalidateSize();

  // If a route is already on the map, remove it so it can get replaced
  if (currentlyDisplayedRoute !== null && currentlyDisplayedRoute !== undefined) {
    interactiveMap.removeLayer(currentlyDisplayedRoute);
  } 

  currentlyDisplayedRoute = L.geoJSON(geoJSON).addTo(interactiveMap);

  interactiveMap.fitBounds([
    [geoJSON["bbox"][1], geoJSON["bbox"][0]],
    [geoJSON["bbox"][3], geoJSON["bbox"][2]]
  ])
}
