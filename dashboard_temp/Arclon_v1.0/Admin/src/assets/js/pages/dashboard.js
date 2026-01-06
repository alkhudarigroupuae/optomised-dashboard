/**
 * Theme: Arclon - Responsive Bootstrap 5 Admin Dashboard
 * Author: Coderthemes
 * Module/App: Dashboard
 */

//
// REVENUE AREA CHART
//
///
var colors = ["#5b69bc", "#30cf46", "#fa5c7c", "#faae37"];
var dataColors = $("#revenue-chart").data('colors');
if (dataColors) {
    colors = dataColors.split(",");
}

var options = {
    series: [
        {
            name: 'Total Revenue',
            type: 'area',
            data: [21, 21, 21, 35, 35, 35, 44, 44, 44, 54, 54, 54, 48, 48, 76, 76, 95, 95, 76, 76, 32, 32, 46, 48, 48]
        }, {
            name: 'Orders',
            type: 'line',
            data: [40, 40, 40, 50, 50, 35, 27, 27, 27, 15, 15, 27, 27, 36, 36, 33, 33, 34, 35, 33, 50, 50, 55, 55, 55]
        },
        { 
            name: "Total Expenses", 
            type: 'bar',
            data: [55, 52, 58, 60, 45, 85, 75, 78, 65, 40, 42, 25, 50, 42, 78, 70, 65, 60, 55, 48, 69, 75, 86, 49, 81]
        }
    ],
    plotOptions: {
        bar: {
            columnWidth: "45%",
            barHeight: "90%",
            borderRadius: 3,
        },
    },
    stroke: {
        width: [3, 3, 0],
        curve: 'smooth',
        dashArray: [0, 8, 0],
    },
    chart: {
        height: 299,
        type: 'line',
        zoom: {
            enabled: false
        },
        toolbar: { show: false }
    },
    dataLabels: {
        enabled: false
    },
    colors: colors,
    tooltip: {
        shared: true,
        y: [{
            formatter: function (y) {
                if (typeof y !== "undefined") {
                    return "$" + y.toFixed(2) + "k";
                }
                return y;
            },
        },
        {
            formatter: function (y) {
                if (typeof y !== "undefined") {
                    return "$" + y.toFixed(2) + "k";
                }
                return y;
            },
        },
        {
            formatter: function (y) {
                if (typeof y !== "undefined") {
                    return "$" + y.toFixed(2) + "k";
                }
                return y;
            },
        }

        ],
    },
    fill: {
        opacity: [1, 0.5],
        type: ['gradient', 'solid'],
        gradient: {
            type: "vertical",
            //   shadeIntensity: 1,
            inverseColors: false,
            opacityFrom: 0.5,
            opacityTo: 0,
            stops: [0, 70]
        },
    },
}

var chart = new ApexCharts(
    document.querySelector("#revenue-chart"),
    options
);

chart.render();

//
// data-visits- CHART
//
var colors = ["#5b69bc", "#4bbee1", "#30cf46", "#fa5c7c", "#e3eaef"];
var dataColors = $("#data-visits-chart").data('colors');
if (dataColors) {
    colors = dataColors.split(",");
}

var options = {
    chart: {
        height: 277,
        type: 'donut',
    },
    series: [65, 14, 10, 45],
    legend: {
        show: true,
        position: 'bottom',
        horizontalAlign: 'center',
        verticalAlign: 'middle',
        floating: false,
        fontSize: '14px',
        offsetX: 0,
        offsetY: 7
    },
    labels: ["Direct","Social", "Marketing", "Affiliates"], // Age groups
    colors: colors,
    stroke: {
        show: false
    }
};

var chart = new ApexCharts(
    document.querySelector("#data-visits-chart"),
    options
);

chart.render();
