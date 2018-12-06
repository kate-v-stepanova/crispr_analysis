$(document).ready(function() {
    // prettify multiselect
    var choices = new Choices('#multiple_cell_lines', {
        allowSearch: true,
        removeItemButton: true
    });

    // initializing constants and removing attributes from html elements
    var PLOT_SERIES = $('#heatmap_chart').attr('data-plot-series').replace(/'/g, '"'); //");
    if (PLOT_SERIES.length != 0) {
        PLOT_SERIES = JSON.parse(PLOT_SERIES);
    }

    var GENES = $('#heatmap_chart').attr('data-genes').replace(/'/g, '"'); //");
    if (GENES.length != 0) {
        GENES = JSON.parse(GENES);
    }

    var CELL_LINES = $('#heatmap_chart').attr('data-cell-lines').replace(/'/g, '"'); //");
    if (CELL_LINES.length != 0) {
        CELL_LINES = JSON.parse(CELL_LINES);
    }
    // removing attributes
    $('#heatmap_chart').removeAttr('data-genes');
    $('#heatmap_chart').removeAttr('data-plot-series');
    $('#heatmap_chart').removeAttr('data-cell-lines');

    if (PLOT_SERIES.length != 0) {
        var chart_height = GENES.length * 25;
        Highcharts.chart('heatmap_chart', {
            chart: {
                type: 'heatmap',
                marginTop: 40,
                marginBottom: 80,
                height: chart_height,

            },
            title: {
                text: 'Fold change values for selected genes vs cell lines',
                y: 3
            },

            xAxis: {
                categories: CELL_LINES,
                opposite: true,
            },

            yAxis: {
                categories: GENES,
                title: null
            },

            colorAxis: {
                stops: [
                    [0.2, '#4575b5'],
                    [0.8, '#ffffff'],
                    [1.2, '#d73028'],
                ],
                min: 0.2,
                max: 1.2,
            },

            legend: {
                align: 'right',
                layout: 'vertical',
                margin: 0,
                verticalAlign: 'top',
                y: 25,
                symbolHeight: 280
            },

            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.xAxis.categories[this.point.x] + '</b><br><b>gene: </b>' +
                        this.series.yAxis.categories[this.point.y] + '</b><br><b>FC: </b>' + this.point.value +
                        '<br><b>p value: </b>' + this.point.pval + '<br><b>increased essentiality: </b>' + this.point.inc_ess;
                }
            },

            series: [{
                name: 'Fold Changes',
                borderWidth: 1,
                data: PLOT_SERIES,
                pointStart: 0,
                pointInterval: 1,
                dataLabels: {
                    enabled: true,
                    color: '#000000'
                }
            }]

        });
    }
});