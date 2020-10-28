startAddress = document.getElementById('start_location').innerText
endAddress = document.getElementById('end_location').innerText
console.log(startAddress)
console.log(endAddress)

axios.get("/maproutes/search/address", {
  params: {
    input: startAddress
  }
})
.then(function (response) { // Successfully responded
  console.log(response.data)
  json = response.data
  var long = json["features"][0]["geometry"]["coordinates"][0];
  var lat = json["features"][0]["geometry"]["coordinates"][1];
  var coords =  [long, lat];
  console.log(coords)

  addMarkerToMap(lat, long, true)
})
.catch(function (error) {
  console.log(error)
  // TODO: Handle error here
})


axios.get("/maproutes/search/address", {
  params: {
    input: endAddress
  }
})
.then(function (response) { // Successfully responded
  console.log(response.data)
  json = response.data
  var long = json["features"][0]["geometry"]["coordinates"][0];
  var lat = json["features"][0]["geometry"]["coordinates"][1];

  addMarkerToMap(lat, long, false)
})
.catch(function (error) {
  console.log(error)
  // TODO: Handle error here
})

