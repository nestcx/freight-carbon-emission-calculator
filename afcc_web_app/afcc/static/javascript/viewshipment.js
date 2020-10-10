"use strict";

function init(){    
    
    var win = window,
    doc = document,
    docElem = doc.documentElement,
    body = doc.getElementsByTagName('body')[0],
    x = win.innerWidth || docElem.clientWidth || body.clientWidth,
    y = win.innerHeight|| docElem.clientHeight|| body.clientHeight;
    
    draw_trees(x,y);
    draw_coins(x,y);
    draw_emissions();
    rowClickHandler("table--pricing");
}

function expandinfo() {
    var tablerows = document.getElementsByClassName("shipment-row");
    var i;
    for (i = 0; i < tablerows.length; i++) {
        tablerows[i].classList.toggle("--hidden");
    }
}

function calculateTotal() {

}

function calculateCost() {

}

function calculateTrees() {

}

function modify() {
    document.getElementsByClassName("btn-edit")[0].classList.toggle("--hidden");
    document.getElementsByClassName("btn-delete")[0].classList.toggle("--hidden");
}

function priceClickHandler(tableId) {
    var table = document.getElementById(tableId);
    var rows = table.getElementsByTagName("tr");
    var i;
    for (i = 0; i < rows.length; i++) {
        var currentRow = table.rows[i];
        var createClickHandler = function(row) {
            return function() {
                var cell = row.getElementsByTagName("td")[0];
                var id = cell.innerHTML;
                alert(id);
            };
        };
        currentRow.onclick = createClickHandler(currentRow);
    }
}

function rowClick() {
    alert("test");
}

window.onload = init;