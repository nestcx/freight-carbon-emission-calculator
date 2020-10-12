"use strict";

function draw_trees(carbon_emission,methane_emission,nitrousoxide_emission){
    var emission_amount=carbon_emission;
    var trees=emission_amount/0.066;

    console.log(carbon_emission);
    console.log(trees);
    
    var xaxis=0;
    var yaxis=0;

    var w=1000, h=300;
    var tree_w=100, tree_h=100;

    var svg = d3.select('#trees')
        .append('svg')
        .attr('width', w)
        .attr('height', h)
        .append("g");
    
    var total_trees=Math.round(trees);
    var max_tree=w/tree_w;

    console.log(total_trees);

    var text=total_trees-20
    
    var loopcount=total_trees

    if(total_trees>(max_tree*2)){
        loopcount=(max_tree*2)
    }
    console.log(loopcount);
    for(var i = 0; i<loopcount;i++){
                            
        svg.append('svg:image')
        .attr("xlink:href","/static/images/tree.png")
        .attr('x', xaxis)
        .attr('y', yaxis)
        .attr('width', tree_w)
        .attr('height', tree_h);

        console.log(xaxis);
        console.log(yaxis);
        console.log(i);

        if(xaxis<w-100){
            xaxis=xaxis+100;
        }
        else if(yaxis<tree_h+10) {
            yaxis+=tree_h+10;
            xaxis=0;
        }
        /*if(total_trees>max_tree){
            svg.append("text")
                .attr("x", 930)
                .attr("y", 150)
                .attr("dy", ".75em")
                .style("font-size", "34px")
                .text("+"+);
            
            
        }*/
        var remaining_trees=(total_trees-(max_tree*2-1));
        
    }
}

function draw_coins(ww,wh){
    var carbon_cost=100, coin_price=1, coins=carbon_cost/coin_price;

    var xaxis=50;
    var yaxis=100;

    var w=1000, h=300;
    var coin_w=100, coin_h=100;

    var maxcoinx=10;
    var maxcoiny=8;
    var total_coins=Math.round(coins);

    var loopcount=total_coins
    var remaining_coins=0;

    if(total_coins>(maxcoinx*maxcoiny)){
        loopcount=(maxcoinx*maxcoiny)
        remaining_coins=total_coins-(maxcoinx*maxcoiny);
        
    }
    
    var svg = d3.select('#coins')
        .append('svg')
        .attr('width', w)
        .attr('height', h)
        .append('g');

    var coin_stacks=1;
    for(var i = 0; i<loopcount;i++){

        if(yaxis==40 && coin_stacks>=5){
            
            yaxis=140;
            xaxis+=80;
            coin_stacks++;
        }
        else if(yaxis==0 && coin_stacks<=3)
        {
            yaxis=100;
            xaxis+=80;
            coin_stacks++;
        }
        else if(yaxis==0 && coin_stacks==4)
        {
            yaxis=140;
            xaxis=0;
            coin_stacks++;
        }
        

        svg.append('svg:image')
        .attr("xlink:href","/static/images/singlecoin.png")
        .attr('x', xaxis)
        .attr('y', yaxis)
        .attr('width', coin_w)
        .attr('height', coin_h);

        yaxis-=10;
        

        
    }
}
function draw_emissions(carbon_emission,methane_emission,nitrousoxide_emission){
    
    var w=400;
    var h=350;
  
    var dataset1={ "Carbon": carbon_emission, "Methane": 84*methane_emission, "Nitrousoxide": 298*nitrousoxide_emission };
  
    var outerRadius = 100;
    var innerRadius = 0;
  
    var arc= d3.arc()
                .outerRadius(outerRadius)
                .innerRadius(innerRadius+40);
    var arcOver=d3.arc()
                    .outerRadius(outerRadius+10)
                    .innerRadius(innerRadius+50);
  
  
    var pie = d3.pie();
    
    var dataset=d3.values(dataset1);

    var svg = d3.select("#emission")
                .append("svg")
                .attr("width",w)
                .attr("height",h);
  
    var arcs = svg.selectAll("g.arc")
                  .data(pie(dataset))
                  .enter()
                  .append("g")
                  .attr("class","arc")
                  .attr("transform","translate("+ 120 +","+ 150 +")");
    
   
    var color = d3.scaleOrdinal()
                    .domain(dataset1)
                    .range(['#96C5F7','#6DC0D5','#C2EFEB']);
  
    svg.append("rect")
        .attr("x", 275)
        .attr("y", 100)
        .attr("width", 15)
        .attr("height", 15)
        .attr("fill","#96C5F7")
        .attr("id","co2_square");
    
    svg.append("text")
        .attr("x",300)
        .attr("y",112)
        .text("CO2 content")
        .attr("id","co2_text");
    
    svg.append("rect")
        .attr("x", 275)
        .attr("y", 130)
        .attr("width", 15)
        .attr("height", 15)
        .attr("fill","#6DC0D5")
        .attr("id","ch4_square");

    svg.append("text")
        .attr("x",300)
        .attr("y",142)
        .text("CH4 content")
        .attr("id","ch4_text");
    
    svg.append("rect")
        .attr("x", 275)
        .attr("y", 160)
        .attr("width", 15)
        .attr("height", 15)
        .attr("fill","#C2EFEB")
        .attr("id","n2o_square");
    
    svg.append("text")
        .attr("x",300)
        .attr("y",172)
        .text("N2O Content")
        .attr("id","n2o_text");

    svg.append("text")
        .attr("x",20)
        .attr("y",320)
        .attr("id","result_text")
        .style("visibility","hidden");

    arcs.append("path")
        .attr("fill", function(d,i){
            return color(i);
        })
        .attr("d", function(d,i){
            return arc(d,i);
        })
        .on("mouseover",function(d){
           
            d3.select(this)
            .attr("stroke","white")
            .transition()
            .duration(200)
            .attr("d", arcOver)
            .attr("stroke-width",1);
            
            d3.select("#result_text")
                .style("visibility","visible")
                .text(d.value+" -e tonnes")
                .attr("font-weight","600")
                .attr("font-size","36");
            
           
            
            for(var i=0;i<3;i++)
            {   
                if(dataset1["Carbon"]==d.value){     
                    d3.select("#co2_square")
                        .attr("stroke","rgb(0,0,0)")
                        .attr("stroke-width","1");
                    
                    d3.select("#co2_text")
                        .attr("font-weight","600");                
                }
                else if(dataset1["Methane"]==d.value){ 
                    d3.select("#ch4_square")
                        .attr("stroke","rgb(0,0,0)")
                        .attr("stroke-width","1");

                    d3.select("#ch4_text")
                        .attr("font-weight","600");                
                }
                else if(dataset1["Nitrousoxide"]==d.value){ 
                    d3.select("#n2o_square")
                        .attr("stroke","rgb(0,0,0)")
                        .attr("stroke-width","1");                       
                    d3.select("#n2o_text")
                        .attr("font-weight","600");                
                }
            }   


        })
        .on("mouseleave", function(d){
            d3.select(this)
            .transition()
            .duration(200)
            .attr("d", arc)
            .attr("stroke","none");

            d3.select("#result_text")
                .style("visibility","hidden");

                if(dataset1["Carbon"]==d.value){     
                    d3.select("#co2_square")
                        .attr("stroke-width","0");
                    
                    d3.select("#co2_text")
                        .attr("font-weight","100");                
                }
                else if(dataset1["Methane"]==d.value){ 
                    d3.select("#ch4_square")
                        .attr("stroke-width","0");

                    d3.select("#ch4_text")
                        .attr("font-weight","100");                
                }
                else if(dataset1["Nitrousoxide"]==d.value){ 
                    d3.select("#n2o_square")
                        .attr("stroke-width","0");                       
                    d3.select("#n2o_text")
                        .attr("font-weight","100");                
                }
        });
  
}
  