"use strict";
function uploadshipments(resultem){
    console.log(resultem)    
}

function shipmentdata(){
    
    /**
     * This function is called when the new shipment is added or 'Get your results' button is clicked.
     * This function will store all the data needed for the calculation and store it in data variable.
     * Then it will send the data to the back-end side of the server using axios post request. The 
     * response received by it contains the emission information which the can be used by us.
     */
    var load = document.getElementById('input-weight').value
    var startloc = document.getElementById('input-pick-up').value
    var endloc =document.getElementById('input-drop-off').value

    var data = JSON.stringify({
      weight : load,
      pickuploc : startloc,
      dropoffloc : endloc
    });

    //This is important as with the header, it wont let us contact back-end server due to CORS-policy,
    //and proxy added means that the website used will be http://127.0.0.1:5000/dashboard.
    var config = {
      headers: {'Access-Control-Allow-Origin': '*'},
      headers:{"Content-Type" : "application/json"},
      proxy: { host: '127.0.0.1',  port: 5000 }
    };

    axios.post("http://127.0.0.1:5000/shipments", 
             data , config              
          )
          .then(function (response) {
            console.log(response);
            //Emission information could be accessed from here.
          })
          .catch(function (error) {
            console.log(error);            
          });
    
    
    
    goToScreen('screen-data-page')
}



