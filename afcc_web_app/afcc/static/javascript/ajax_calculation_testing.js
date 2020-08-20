var startCoords_input = document.getElementById("startCoords");
var endCoords_input = document.getElementById("endCoords");
var loadWeight_input = document.getElementById("loadWeight");

// set default values in form
startCoords_input.value = '10 smith street collingwood';
endCoords_input.value = 'Preston';
loadWeight_input.value = '2.9';

function getFormData(){
    var formData = new Object();
    formData.startCoords = startCoords_input.value;
    formData.endCoords = endCoords_input.value;
    formData.loadWeight = parseFloat(loadWeight_input.value);
    return formData;
}

function postData() {
    var start_time = new Date().getTime();

    var formData = getFormData();

    axios.post('/calculation/address', {
        startAddress: formData.startCoords,
        endAddress: formData.endCoords,
        loadWeight: formData.loadWeight
    })
    .then((response) => {
        render_response(response.data)
        
        var request_time = (new Date().getTime() - start_time) / 1000;
        rtt_html = `<span class="info">RTT: </span><span class="monospace rtt">${request_time} seconds</span>`
        rtt_span = document.getElementsByClassName("rtt")[0];
        rtt_span.innerHTML = rtt_html;
    })
    .catch((error) => {
        console.log(error)
    })
}


let button = document.getElementById("submit");
button.addEventListener('click', postData);

function render_response(response){

    co2 = response.emissions.carbon_dioxide_emission;
    ch4 = response.emissions.methane_emission;
    n2o = response.emissions.nitrous_oxide_emission;

    distance = response.distance;
    fuel_consumption = response.fuel_consumption;
    adjusted_fuel_economy = response.adjusted_fuel_economy;
    duration = response.duration;

    start_address = response.location.start_location.address;
    end_address = response.location.end_location.address;

    start_coordinates = response.location.start_location.coordinate;
    end_coordinates = response.location.end_location.coordinate;

    /* create html template */

    template = `
    <table class="location">
        <tr>
            <td class="blank"></td>
            <td class="tt">Found Address</td>
            <td class="tt">Co-ordinates</td>
        </tr>
        <tr>
            <td class="tt">Start Address</td>
            <td class="api_data">${start_address}</td>
            <td class="api_data">${start_coordinates}</td>
        </tr>
        <tr>
            <td class="tt">End Address</td>
            <td class="api_data">${end_address}</td>
            <td class="api_data">${end_coordinates}</td>
        </tr>
    </table>

    <table class="emissions">
        <tr>
            <td class="tt">Gas Type</td>
            <td class="tt">Emission Value</td>
            <td class="tt">unit</td>
        </tr>
        <tr>
            <td class="tt">co2</td>
            <td class="api_data">${co2}</td>
            <td class="unit">kg</td>
        </tr>
        <tr>
            <td class="tt">n2o</td>
            <td class="api_data">${n2o}</td>
            <td class="unit">kg</td>
        </tr>
        <tr>
            <td class="tt">ch4</td>
            <td class="api_data">${ch4}</td>
            <td class="unit">kg</td>
        </tr>
    </table>

    <table class="additional_information">
        <tr>
            <td class="blank"></td>
            <td class="tt">Result</td>
            <td class="tt">unit</td>
        </tr>
        <tr>
            <td class="tt">Distance</td>
            <td class="api_data">${distance}</td>
            <td class="unit">km</td>
        </tr>
        <tr>
            <td class="tt">Adjusted Fuel Economy</td>
            <td class="api_data">${adjusted_fuel_economy}</td>
            <td class="unit">l/100km</td>
        </tr>
        <tr>
            <td class="tt">Fuel Consumption</td>
            <td class="api_data">${fuel_consumption}</td>
            <td class="unit">litres</td>
        </tr>
        <tr>
            <td class="tt">Trip Duration</td>
            <td class="api_data">${duration}</td>
            <td class="unit">HH:MM:SS</td>
        </tr>
    </table>
    `
    
    let response_div = document.getElementsByClassName("response")[0];
    response_div.innerHTML = template;

}