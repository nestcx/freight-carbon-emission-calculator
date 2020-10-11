"use strict";

function init(){    
    
    var win = window,
    doc = document,
    docElem = doc.documentElement,
    body = doc.getElementsByTagName('body')[0],
    x = win.innerWidth || docElem.clientWidth || body.clientWidth,
    y = win.innerHeight|| docElem.clientHeight|| body.clientHeight;
    
    
    draw_coins(x,y);
    costClickHandler("table--pricing");
    emissionClickHandler("table--emissions");
    calculateTotal();
    calculateCost("AU");

}

function expandinfo() {
    var tablerows = document.getElementsByClassName("shipment-row");
    var i;
    for (i = 0; i < tablerows.length; i++) {
        tablerows[i].classList.toggle("--hidden");
    }
}

//calculates total emission from emission table data and fills html element with value
function calculateTotal() {
    //getting table and row elements from DOM
    var table = document.getElementById("table--emissions");
    var rows = table.getElementsByTagName("tr");
    var i;
    var total = 0;
    //iterates through emission table and adds data value to running total
    for (i = 0; i < rows.length; i++) {
        var currentRow = table.rows[i];
        var emission = parseFloat(currentRow.getElementsByTagName("td")[1].innerHTML);
        total = total + emission;
    }
    //sets total emission element to total value
    document.getElementById("emissionsTotal").innerHTML = total + " tCO2e";
}

function calculateCost(currency) {
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
            text = "This is how much your shipment would cost under the United Nations recommended pricing to keep global temperature increase to below 1.5 degrees"
        break;
        default:
            price = 24.15;
            unit = "&#36 "  //ASCII code for dollar symbol
            text = "This is how much your shipment would cost based on the repealed 2014 Australian carbon tax";
    }
    //calculates 
    var emissions = document.getElementById("emissionsTotal").innerHTML;
    var cost = price * emissions;
    document.getElementById("calculatedPrice").innerHTML = unit + cost;
    document.getElementById("priceDescription").innerHTML = text;

}

function calculateTrees() {

}

//opens and closes edit and delete button options
function modify() {
    document.getElementsByClassName("btn-edit")[0].classList.toggle("--hidden");
    document.getElementsByClassName("btn-delete")[0].classList.toggle("--hidden");
}


//click handlers for table rows, creates onClick event based on table row data
function costClickHandler(tableId) {
    var table = document.getElementById(tableId);
    var rows = table.getElementsByTagName("tr");
    var i;
    for (i = 0; i < rows.length; i++) {
        var id = rows[i].id;
        var currentRow = table.rows[i];
        var createClickHandler = function(id, tableId) {
            return function() {
                makeSelected(id, tableId);
                calculateCost(id);
            };
        };
        currentRow.onclick = createClickHandler(id, tableId);
    }
}

function emissionClickHandler(tableId) {
    var table = document.getElementById(tableId);
    var rows = table.getElementsByTagName("tr");
    var i;
    for (i = 0; i < rows.length; i++) {
        var id = rows[i].id;
        var currentRow = table.rows[i];
        var createClickHandler = function(id, tableId) {
            return function() {
                makeSelected(id, tableId);
            };
        };
        currentRow.onclick = createClickHandler(id, tableId);
    }
}

//adds "--selected" to class list of given row within given table
function makeSelected(rowId, tableId) {
    //Deselect all rows
    var table = document.getElementById(tableId);
    var elements = table.getElementsByTagName("tr");
    var i;
    for (i = 0; i < elements.length; i++) {
        elements[i].classList.remove("--selected");
    }
    //Make clicked row selected
    document.getElementById(rowId).classList.add("--selected");
}

window.onload = init;