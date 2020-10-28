var emission_array=[0,0];
var emi1=0,emi2=0;

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

    var emission_total=shipment.carbon_dioxide;
    var trees=calculateTrees(emission_total);
    
    var selectedcurrency="";
    var currency=document.getElementsByName('price');
    for(var i=0;i<currency.length;i++){
        if(currency[i].checked==true){
            selectedcurrency=currency.value;
        }
    }
    var cost=calculateCost("AU",emission_total);

    var selectedemitype="";
    var emission_type=document.getElementsByName('emission');
    for(var i=0;i<emission_type.length;i++){
        if(emission_type[i].checked==true){
            selectedcurrency=emission_type.value;
        }
    }
    
    if(shipment_no==1){
        emi1=emission_total;
        comparetool_drawtrees(trees,"shipment1_trees");
        comparetool_drawcoins(cost,"shipment1_coins");
        emission_array[0]=shipment.carbon_dioxide;
    }
    else if(shipment_no==2){
        emi2=emission_total;
        comparetool_drawtrees(trees,"shipment2_trees");
        comparetool_drawcoins(cost,"shipment2_coins");
        emission_array[1]=shipment.carbon_dioxide;
        
    }
    //For changes in Emission type radio buttons the code is below. 
    //There is another code near the end of this code.
    if(selectedemitype=="average_emission")
    {
        var dist1=parseInt(document.getElementById('distance_1').innerHTML);
        var dist2=parseInt(document.getElementById('distance_2').innerHTML);
        draw_emissionbar([100*emission_array[0]/dist1,100*emission_array[1]/dist2]);
    }
    else{
        draw_emissionbar(emission_array);
    }
    
}

function myOtherFunction() {
}


function calculateTrees(total_emissions) {
    var treeFactor = 15;
    var treeValue = parseFloat(total_emissions) * treeFactor;
    var treeValueText = Math.ceil(treeValue.toFixed(2));

    return treeValueText;

    
}
function calculateCost(currency,total_emissions) {
    var price;
    var text;
    var unit;
    switch (currency) {
        case "AU":
            price = 24.15;
            unit = "&#36 "  //ASCII code for dollar symbol
            text = "This is how much your shipment would cost based on the repealed 2014 Australian carbon tax";
            break;
        case "CAL":
            price = 15;
            unit = "&#36 "       //ASCII code for dollar symbol
            text = "This is how much your shipment would cost under the Californian carbon trading scheme"
            break;
        case "GB":
            price = 25;
            unit = "&#163 " //ASCII code for pound symbol
            text = "This is how much your shipment would cost under Great Britains current Cap and Trade policy"
            break;
        case "UN":
            price = 135;
            unit = "&#36 "  //ASCII code for dollar symbol
            text = "This is how much your shipment would cost under the United Nations recommended pricing scheme"
            break;
        default:
            price = 24.15;
            unit = "&#36 "  //ASCII code for dollar symbol
            text = "This is how much your shipment would cost based on the repealed 2014 Australian carbon tax";
    }
    //calculates 
    var cost = price * parseFloat(total_emissions);
    
    return cost;
}

window.onload = function(){
    var currencyAU=document.getElementById('currencyAU');
    var currencyCAL=document.getElementById('currencyCAL');
    var currencyGB=document.getElementById('currencyGB');
    var currencyUN=document.getElementById('currencyUN');

    currencyAU.onclick = function(){
        var cost1=calculateCost("AU",emi1);
        comparetool_drawcoins(cost1,"shipment1_coins");
        var cost2=calculateCost("AU",emi2);
        comparetool_drawcoins(cost2,"shipment2_coins");
    };
    currencyCAL.onclick  = function(){
        var cost1=calculateCost("CAL",emi1);
        comparetool_drawcoins(cost1,"shipment1_coins");
        var cost2=calculateCost("CAL",emi2);
        comparetool_drawcoins(cost2,"shipment2_coins");
    };
    currencyGB.onclick = function(){
        var cost1=calculateCost("GB",emi1);
        comparetool_drawcoins(cost1,"shipment1_coins");
        var cost2=calculateCost("GB",emi2);
        comparetool_drawcoins(cost2,"shipment2_coins");
    };
    currencyUN.onclick = function(){
        var cost1=calculateCost("UN",emi1);
        comparetool_drawcoins(cost1,"shipment1_coins");
        var cost2=calculateCost("UN",emi2);
        comparetool_drawcoins(cost2,"shipment2_coins");
    };


    var total_emission=document.getElementById('total_emission');
    var average_emission=document.getElementById('average_emission');

    //For changes in Emission type radio buttons the code is below. 

    total_emission.onclick=function(){
        draw_emissionbar(emission_array);
    }
    average_emission.onclick=function(){
        var dist1=parseInt(document.getElementById('distance_1').innerHTML);
        var dist2=parseInt(document.getElementById('distance_2').innerHTML);
        draw_emissionbar([100*emission_array[0]/dist1,100*emission_array[1]/dist2]);
        console.log(emi1);
        console.log(emi2);
        console.log(dist1);
        console.log(dist2);
        console.log(emission_array[0]/dist1);
        console.log(emission_array[0]/dist1);
    }

}
function handler(){
    
}