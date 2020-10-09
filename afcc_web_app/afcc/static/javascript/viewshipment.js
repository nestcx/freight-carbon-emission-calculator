"use strict";

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

function rowClickHandlers(tableId) {
    var table = document.getElementById(tableId);
    var rows = table.getElementsByTagName("tr");
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

document.onload = loadFunction() {
    rowClickHandlers("table--emissions");
    rowClickHandlers("tablers--emissions");
}