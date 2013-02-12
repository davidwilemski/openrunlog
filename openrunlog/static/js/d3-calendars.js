var Calendar = {
    year: function(user_id) {
        var today = new Date()
        var day = today.getDate()
        var month = today.getMonth()
        var year = today.getFullYear()
    
        var width = 700
        var pw = 20
        var box_side = ~~((width-pw*2)/53)
        var ph = box_side >> 1
        var height = ph + box_side * 8
    
        var day_range = d3.range(0,360);
        var vis = d3.select("#run-calendar")
            .append("svg:svg")
            .attr("height", height + ph * 2)
            .attr("width", width)
    
        d3.json("/data/" + user_id + "/runs/year", function (json) {
            var format = d3.time.format("%Y-%m-%d")
            var today_dow = json[json.length-1][1]
            var this_year_x_offset = (52 - today_dow ) * box_side
            var last_year_x_offset = -1 * box_side * today_dow
            var week = function(d) { return d[1] }
            var _year = function(d) { return format.parse(d[0]).getFullYear() }
            var dow = function(d) { return format.parse(d[0]).getDay() }
            var _date = function(d) { return format.parse(d[0]).getDate() }
            var month = function(d) { return format.parse(d[0]).getMonth() }
            var color = d3.scale.linear().domain([0,10]).range(["hsl(250, 50%, 50%)", "hsl(350, 100%, 50%)"]).interpolate(d3.interpolateHsl)
            
            vis.selectAll("rect")
                .data(json)
                .enter().append("svg:rect")
                .attr("x", function(d) { var x = week(d) * box_side + pw; 
                                         if (dow(d) == 0) x += box_side;
                                         if (month(d) == 11 && _date(d) == 31) {
                                            x += box_side * 52;
                                         }
                                         if (_year(d) == year) {
                                            return x + this_year_x_offset;
                                         } else {
                                            return x + last_year_x_offset; 
                                         } })
                .attr("y", function(d) { return ph + (1 + dow(d)) * box_side})
                .attr("data-date", function(d) { return d[0] })
                .attr("data-dow", function(d) { return dow(d) })
                .attr("data-woy", function(d) { return d[1] })
                .attr("data-month", function(d) { return month(d); })
                .attr("stroke-width", "0.8px")
                .attr("stroke", "#ccc")
                .attr("fill", function(d) { if (d[2] == 0) { return "#eee"; } else { return "#1e6823"; } })
                .attr("fill-opacity", .5)
                .attr("visibility", "visible")
                .attr("width", box_side)
                .attr("height", box_side)
            
            vis.selectAll("text.month")
                .data(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
                .enter().append("svg:text")
                .attr("class", "month")
                .attr("x", function(d, i) { return (box_side - 2 + parseInt($(d3.select('rect[data-dow="0"][data-month="' + i + '"]')[0][0]).attr("x"))); })
                .attr("y", box_side)
                .attr("text-anchor", "middle")
                .attr("fill", "#ccc")
                .attr("style", "font-size:" + box_side + "px;")
                .text(String)
    
            vis.selectAll("text.dow")
                .data(["S", "M", "T", "W", "T", "F", "S"])
                .enter().append("svg:text")
                .attr("class", "dow")
                .attr("x", box_side-2)
                .attr("y", function(d, i) { return ph + (i + 2) * box_side - 1; })
                .attr("text-anchor", "middle")
                .attr("fill", "#ccc")
                .attr("style", function(d, i) { if (i % 2 == 0) return "display:none;";
                                                else return "font-size:" + (box_side) + "px;";
                                                })
                .text(String)
    
        });
    },

    month: function(element) {
        var element = $(element)
        if (!element || element === '') {
            console.log('Calendar needs element')
            return false
        }
        var url = element.attr('data-url')
        if (!url || url === '') {
            console.log('Calendar needs data-url')
            return false
        }

        var today = new Date()
        var day = today.getDate()
        var month = today.getMonth()
        var year = today.getFullYear()
    
        var width = 250
        var pw = 20
        var box_side = ~~((width-pw*2)/7)
        var ph = box_side >> 1
        var height = ph + box_side * 6
    
        var day_range = d3.range(0,31);
        var vis = d3.select("#run-calendar")
            .append("svg:svg")
            .attr("height", height + ph * 2)
            .attr("width", width)
    
        d3.json(url, function (json) {
            var _counter_week = 1;
            var format = d3.time.format("%Y-%m-%d")
            var today_dow = json[json.length-1][1]
            var _week = function(d) { return d[1] }
            var _year = function(d) { return format.parse(d[0]).getFullYear() }
            var _dow = function(d) { return format.parse(d[0]).getDay() }
            var _date = function(d) { return format.parse(d[0]).getDate() }
            var _month = function(d) { return format.parse(d[0]).getMonth() }
            var _color = d3.scale.linear().domain([0,3]).range(["hsl(124, 20%, 93%)", "hsl(124, 55%, 26%)"]).interpolate(d3.interpolateHsl)
            
            vis.selectAll("rect")
                .data(json)
                .enter().append("svg:rect")
                .attr("x", function(d) { return _dow(d) * box_side + pw })
                .attr("y", function(d, i) { if (_dow(d) == 0 && i != 0) {
                                                _counter_week += 1
                                            }
                                            return ph + _counter_week * box_side })
                .attr("data-date", function(d) { return d[0] })
                .attr("data-dow", function(d) { return _dow(d) })
                .attr("data-woy", function(d) { return d[1] })
                .attr("data-month", function(d) { return _month(d); })
                .attr("stroke-width", "1.0px")
                .attr("stroke", "#fff")
                .attr("fill", function(d) { return _color(d[2]) })
                .attr("fill-opacity", .5)
                .attr("visibility", "visible")
                .attr("width", box_side)
                .attr("height", box_side)
            
            _counter_week = 1;
            vis.selectAll("text.date")
                .data(json)
                .enter().append("svg:text")
                .attr("class", "date")
                .attr("x", function(d, i) { return 15 + _dow(d) * box_side + pw })
                .attr("y", function(d, i) { if (_dow(d) == 0 && i != 0) {
                                                _counter_week += 1
                                            }
                                            return 20 + ph + _counter_week * box_side })
                .attr("text-anchor", "middle")
                .attr("fill", "#000")
                .attr("style", "font-size:15px;")
                .text(function(d) { return _date(d) })
    
            vis.selectAll("text.dow")
                .data(["S", "M", "T", "W", "T", "F", "S"])
                .enter().append("svg:text")
                .attr("class", "dow")
                .attr("x", function(d, i) { return i * box_side + pw + 15 })
                .attr("y", function() { return box_side })
                .attr("text-anchor", "middle")
                .attr("fill", "#ccc")
                .attr("style", function(d, i) { return "font-size:15px;" })
                .text(function(s) { return s })
    
        });
    }
}
