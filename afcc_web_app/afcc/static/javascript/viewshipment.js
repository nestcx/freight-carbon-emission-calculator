"use strict";

function expandinfo() {
    var tablerows = document.getElementsByClassName("shipment-row");
    var i;
    for (i = 0; i < tablerows.length; i++) {
        tablerows[i].classList.toggle("--hidden");
    }
}

function calculateCost() {
    
}