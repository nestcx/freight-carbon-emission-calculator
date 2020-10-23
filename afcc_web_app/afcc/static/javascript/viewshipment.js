"use strict";

function init() {

    var win = window,
        doc = document,
        docElem = doc.documentElement,
        body = doc.getElementsByTagName('body')[0],
        x = win.innerWidth || docElem.clientWidth || body.clientWidth,
        y = win.innerHeight || docElem.clientHeight || body.clientHeight;

    var emissions = document.getElementById("calculatedEmission").innerHTML;
    roundEmissions();
    draw_trees(emissions);
    draw_coins(x, y);
    costClickHandler("table--pricing");
    emissionClickHandler("table--emissions");
    calculateTotal();
    calculateCost("AU");
    calculateTrees();
}

function expandinfo() {
    var tablerows = document.getElementsByClassName("shipment-row");
    var i;
    const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0)
    console.log(vw);
    if (vw <= 760) {
        for (i = 0; i < tablerows.length; i++) {
            tablerows[i].classList.toggle("--show");
        }
    }
    if (vw <= 760) {
        document.getElementById("arrowIconRight").classList.toggle("--hidden");
        document.getElementById("arrowIconDown").classList.toggle("--hidden");
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
    document.getElementById("calculatedEmission").innerHTML = total + " tCO2e";
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
            text = "This is how much your shipment would cost under the United Nations recommended pricing scheme"
            break;
        default:
            price = 24.15;
            unit = "&#36 "  //ASCII code for dollar symbol
            text = "This is how much your shipment would cost based on the repealed 2014 Australian carbon tax";
    }
    //calculates 
    var emissions = document.getElementById("calculatedEmission").innerHTML;
    var cost = price * parseFloat(emissions);
    document.getElementById("calculatedPrice").innerHTML = unit + cost.toFixed(2);
    document.getElementById("priceDescription").innerHTML = text;

}

function calculateTrees() {
    var treeFactor = 15;
    var emissions = document.getElementById("calculatedEmission").innerHTML;
    var treeValue = parseFloat(emissions) * treeFactor;
    var treeValueText = treeValue.toFixed(2);
    document.getElementById("calculatedTree").innerHTML = treeValueText + " Trees";
    document.getElementById("treeDesc").innerHTML = "You would need to plant " + treeValueText + " trees to remove your shipments produced carbon from the atmosphere";
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
    for (i = 1; i < rows.length; i++) {
        var id = rows[i].id;
        var currentRow = table.rows[i];
        var createClickHandler = function (id, tableId) {
            return function () {
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
        var createClickHandler = function (id, tableId) {
            return function () {
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

function roundEmissions() {
    //get values
    var emissions = document.getElementById("table--emissions");
    var gasses = emissions.getElementsByTagName("tr");
    var carbon = gasses[0].getElementsByTagName("td");
    var nitrous = gasses[1].getElementsByTagName("td");
    var methane = gasses[2].getElementsByTagName("td");

    var carbonval = carbon[1].innerHTML;
    var nitval = nitrous[1].innerHTML;
    var methval = methane[1].innerHTML;

    //round values
    var carbonrounded = parseFloat(carbonval).toFixed(7);
    var nitrounded = parseFloat(nitval).toFixed(7);
    var methrounded = parseFloat(methval).toFixed(7);

    //resetting rounded values
    carbon[1].innerHTML = carbonrounded + " TCO2e";
    nitrous[1].innerHTML = nitrounded + " TCO2e";
    methane[1].innerHTML = methrounded + " TCO2e";

}

function deleteShipment() {
    //get shipment id
    var idToDelete = document.getElementById("shipId").innerHTML;
    console.log(idToDelete);

    var result = confirm("Delete this shipment?");
    if (result) {
        
    }
}


window.onload = init;