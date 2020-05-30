function init(){

    var w=400;
    var h=350;
  
    var dataset1={ "Carbon":24, "Methane": 28, "Nitrousoxide": 15 };
  
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

    var svg = d3.select("#d3charts")
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
  
  
  
  window.onload = init;
  