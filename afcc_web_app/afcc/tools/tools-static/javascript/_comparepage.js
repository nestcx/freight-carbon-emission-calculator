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
    document.getElementById("truck_type_" + shipment_no).innerText = shipment.truck_id

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



"use strict";

function draw_emissionbar(vEmissiondata){

    var w=530; // Make the SVG extend the width of the container
    var h=200;

    var parentdiv=document.getElementById("emi_visual");
    w=parentdiv.offsetWidth;

    var dataset=[
        vEmissiondata[0],
        vEmissiondata[1],
    ]

    

    d3.select("#emissionbargraph").select("svg").remove();

    var xScale=d3.scaleBand()
                .domain(d3.range(dataset.length))
                .rangeRound([w/4,(3*w)/4])
                .paddingInner(0.05);

    var yScale=d3.scaleLinear()
                .domain([0,d3.max(dataset,function(d){
                  return d;
                })])
                .range([0,h-40]); // Give more room for the text to breathe
    
    var svg=d3.select("#emissionbargraph")
            .append("svg")
            .attr("width",w)
            .attr("height",h)
            .append("g");

    var colorflag=0;

    svg.selectAll("g")
            .data(dataset)
            .enter()
            .append("rect")
            .attr("x",function(d,i){
                
                var space=0;
                if(i%2==0){
                    space=0;
                }
                else{
                    space=0;
                }
              return xScale(i)+space;
            })
            .attr("y",function(d){
              return h-yScale(d);
            })
            .attr("width",xScale.bandwidth()/2)
            .attr("height",function(d){
              return yScale(d);
            })
            .attr("fill","#206a5d")
            .on("mouseover",function(d){
                infoBox(d)
            });

        var textbox=svg.append("g")
                        .attr("id","infoboxrect");
       
        textbox.append("text")
                    .attr("id","infotextname")
                    .attr("x", 10)
                    .attr("y", 20 )
                    .text("Please hover over the bar to display the info.")
                    .attr("fill","black");

    
    var rectangle;
    function infoBox(data){
        d3.selectAll("#infoboxrect").remove();
        

        rectangle=svg.append("g")
                  .attr("id","infoboxrect");

        var rectangle_x = w-125;

        rectangle.append("rect")
                  .attr("x", rectangle_x)
                  .attr("y", 10)
                  .attr("width", 105)
                  .attr("height", 55)
                  .attr("fill","white")
                  .attr("stroke","#206a5d")
                  .attr("stroke-width","3");
        var canvas = document.createElement('canvas'), context = canvas.getContext('2d');
        var valuetextWidth=context.measureText((data).toFixed(3)).width;
        var valuetextplacementx=Math.round((100-valuetextWidth)/2);

        rectangle.append("text")
                  .attr("id","infotextname")
                              .attr("x", rectangle_x+valuetextplacementx)
                              .attr("y", 30 )
                              .text(data.toFixed(3))
                  .attr("fill","black");

        var tonnestr="tonne e-"
        var canvas = document.createElement('canvas'), context = canvas.getContext('2d');
        var valuetextWidth=context.measureText(tonnestr).width;
        var valuetextplacementx=Math.round((100-valuetextWidth)/2);

        rectangle.append("text")
                  .attr("id","infotextstr")
                              .attr("x", rectangle_x+25)
                              .attr("y", 50 )
                              .text(tonnestr)
                  .attr("fill","black");
    }
    
}

function comparetool_drawtrees(trees,tree_id){
    console.log('drawtrees');
    console.log(trees);
    
    var xaxis=10;
    var yaxis=10;

    var w=250,h=90;

    var parentdiv=document.getElementById("tree_visual");
    w=parentdiv.offsetWidth/2;

    var tree_w=30, tree_h=30;

    d3.select("#"+tree_id).select("svg").remove();

    var svg = d3.select("#"+tree_id)
        .append('svg')
        .attr('width', w)
        .attr('height', h)
        .append("g");
    
    var total_trees=Math.ceil(trees);
    var max_tree=w/tree_w;

    console.log(total_trees);
    
    var loopcount=total_trees

    if(total_trees>(max_tree*2)){ 

        if((max_tree*2)>16){
            loopcount=16
        }
        else{
            loopcount=(max_tree*2)
        }
    }
    console.log(loopcount);
    for(var i = 0; i<loopcount;i++){
                            
        svg.append('svg:image')
        .attr("xlink:href","/static/images/tree.png")
        .attr('x', xaxis)
        .attr('y', yaxis)
        .attr('width', tree_w)
        .attr('height', tree_h);


        if(xaxis<w-40){
            xaxis=xaxis+30;
        }
        else if(yaxis<tree_h+10) {
            yaxis+=tree_h+10;
            xaxis=10;
        }
        
    }

}
function comparetool_drawcoins(cost,coin_id){
    var carbon_cost=cost, coin_price=1, coins=carbon_cost/coin_price;

    var xaxis=50;
    var yaxis=50;
    
    var w=250,h=90;
    
    var parentdiv=document.getElementById("price_visual");
    w=parentdiv.offsetWidth/2;

    var coin_w=50, coin_h=50;

    var maxcoinx=10;
    var maxcoiny=8;
    var total_coins=Math.round(coins);

    var loopcount=total_coins
    var remaining_coins=0;
    
    if(w<450){
        maxcoiny=6;
    }

    
    if(total_coins>(maxcoinx*maxcoiny)){
        loopcount=(maxcoinx*maxcoiny)
        remaining_coins=total_coins-(maxcoinx*maxcoiny);
        
    }

    d3.select('#'+coin_id).select("svg").remove();
    
    var svg = d3.select('#'+coin_id)
        .append('svg')
        .attr('width', w)
        .attr('height', h)
        .append('g');

    var coin_stacks=1;
    for(var i = 0; i<loopcount;i++){

        if(yaxis==0 && coin_stacks<=3)
        {
            yaxis=50;
            xaxis+=40;
            coin_stacks++;

            if(xaxis+50>w){
                break;
            }
        }
        else if(yaxis==0 && coin_stacks==4)
        {
            break;
        }
        

        svg.append('svg:image')
        .attr("xlink:href","/static/images/singlecoin.png")
        .attr('x', xaxis)
        .attr('y', yaxis)
        .attr('width', coin_w)
        .attr('height', coin_h);

        yaxis-=5;
        

        
    }
}
  