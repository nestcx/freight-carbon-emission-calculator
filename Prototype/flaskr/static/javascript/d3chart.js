function init(){

    var w=400;
    var h=400;
  
    var dataset1=[12,24,18,20];
  
    var outerRadius = 150;
    var innerRadius = 0;
  
    var arc= d3.arc()
                .outerRadius(outerRadius)
                .innerRadius(innerRadius+80);
  
    var pie = d3.pie();
  
    var svg = d3.select("#d3charts")
                .append("svg")
                .attr("width",w)
                .attr("height",h);
  
    var arcs = svg.selectAll("g.arc")
                  .data(pie(dataset1))
                  .enter()
                  .append("g")
                  .attr("class","arc")
                  .attr("transform","translate("+ outerRadius +","+ outerRadius +")");

    var arcOver=d3.arc()
                .outerRadius(outerRadius+50)
                .innerRadius(innerRadius+130);
  
    var color = d3.scaleOrdinal(['#fef0d9','#fdcc8a','#fc8d59','#e34a33','#b30000']);
  
    arcs.append("path")
        .attr("fill", function(d,i){
            return color(i);
        })
        .attr("d", function(d,i){
            return arc(d,i);
        });
    
    arcs.on("mouseover",function(d){
        
        d3.select(this)
        .attr("stroke","white")
        .transition()
        .duration(200)
        .attr("d", function(d,i){
            return arcOver(d,i);
        })
        .attr("stroke-width",10);
        
        /*svg.append("text")
        .text(function(d){
            return this.value;
        })
        .attr("transform", function(d){
            return "translate("+ arc.centroid(d)+")"
        });*/
    })
    .on("mouseleave", function(d){
        d3.select(this)
        .transition()
        .duration(200)
        .attr("d", arc)
        .attr("stroke","none");
    });
  
    /*arcs.append("text")
        .text(function(d){
            return d.value;
        })
        .attr("transform", function(d){
            return "translate("+ arc.centroid(d)+")"
        });*/
  
  
  
  }
  
  
  
  window.onload = init;
  