function back_to_tools() {
    window.location.href = '/tools'
}

function myFunction(shipment_no) {

    // get string from textbox
    input = document.getElementById("shipment" + shipment_no).value
    if (input == "") {
        document.querySelectorAll('.search_result').forEach(e => e.classList.add("hide"));
        return;
    }
    axios.get('/tools/compare/search?q=' + input)
    .then((response) => {
        shipments = response.data
        useInfo(response.data, shipment_no)
    })
    .catch((error) => {
        console.log(error)
    })
    
}

Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

function useInfo(shipments, shipment_no) {
    var size = Object.size(shipments)

    document.querySelectorAll('.search_result').forEach(e => e.remove());

    // create elements.
    for (i = 0; i < size; i++) {
        let element = document.createElement("div")

        if (shipments[i].shipment_name) {
            element.innerText = shipments[i].shipment_id + " - " + shipments[i].shipment_name
        } else {
            element.innerText = shipments[i].shipment_id;
        }
        element.classList.add("search_result")
        element.classList.add(shipment_no + "_result")
        element.id = shipments[i].shipment_id;

        element.onclick = function() { populate(element, shipment_no)}

        let searchbox = document.getElementById("shipment" + shipment_no)
        searchbox.insertAdjacentElement('afterend', element)
        console.log(shipments[i])
    }
}

function populate(id, shipment_no) {
    var shipment

    // get shipment data
    axios.get('/tools/compare/shipment_information?id=' + id.id)
    .then((response) => {
        shipment = response.data
        console.log(shipment)
        populate_again(shipment, shipment_no)
    })

    document.querySelectorAll('.search_result').forEach(e => e.classList.add("hide"));
    
}

function secondsToHms(d) {
    d = Number(d);
    var h = Math.floor(d / 3600);
    var m = Math.floor(d % 3600 / 60);
    var s = Math.floor(d % 3600 % 60);

    var hDisplay = h > 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
    var mDisplay = m > 0 ? m + (m == 1 ? " minute, " : " minutes, ") : "";
    var sDisplay = s > 0 ? s + (s == 1 ? " second" : " seconds") : "";
    return hDisplay + mDisplay + sDisplay; 
}

function populate_again(shipment, shipment_no) {

    // get shipment data here for visualisations.

    var weight;

    if (shipment.load_weight_unit == 'tonne') {
        weight = shipment.load_weight * 1000;
    } else { 
        weight = shipment.load_weight;
    }

    timestr = secondsToHms(shipment.trip_duration)

    document.getElementById("shipment" + shipment_no).value = shipment.shipment_id
    document.getElementById("name_" + shipment_no).innerText = shipment.name
    document.getElementById("origin_" + shipment_no).innerText = shipment.start_address
    document.getElementById("destination_" + shipment_no).innerText = shipment.end_address
    document.getElementById("distance_" + shipment_no).innerText = shipment.trip_distance.toFixed(1) + " km"
    document.getElementById("load_weight_" + shipment_no).innerText = weight + " kg"
    document.getElementById("duration_" + shipment_no).innerText = timestr
    document.getElementById("truck_type_" + shipment_no).innerText = shipment.truck_id
}

function myOtherFunction() {
}