"use strict";

function getData(){
    var startcoords=document.getElementById("input-pick-up");
    var endcoords=document.getElementById("input-drop-off");
    
    var load=document.getElementById("input-weight");

    var entry={
        startc: startcoords.value,
        endc: endcoords.value,
        load: load.value
    };

    fetch(`${window.origin}/getemissionresult`,{
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache:"no-cache",
        headers: new Headers({
            "content-type" : "application/json"
        })

    })
    .then(function(response){
       
        if(response.status !== 200){
            console.log(`Response status was not 200 : ${response.status}`);

        }
        response.json().then(function(data){
           
            console.log(data);
          
        })
    })

    console.log(entry);
}