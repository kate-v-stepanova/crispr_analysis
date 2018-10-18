$(document).ready(function() {
    // initializing constants and removing attributes from html elements
    var PLOT_SERIES = $('#cell_line_chart').attr('data-plot-series').replace(/'/g, '"'); //");
    if (PLOT_SERIES.length != 0) {
        PLOT_SERIES = JSON.parse(PLOT_SERIES);
    }
    var GENES = $('#cell_line_chart').attr('data-genes').replace(/'/g, '"'); //");
    if (GENES.length != 0) {
        GENES = JSON.parse(GENES);
    }

    // removing attributes
    $('#cell_line_chart').removeAttr('data-genes');
    $('#cell_line_chart').removeAttr('data-plot-series');

    if (GENES.length != 0) {
        // initializing plot
        var cell_line = $('#cell_line_select').val();
        // setting up the max number of points
        var turbo_threshold = GENES.length;

        var p_values = $('input:radio:checked').val();
        console.log(p_values);

        Highcharts.chart('cell_line_chart', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: 'Fold change values for cell line <b>' + cell_line + '</b>'
            },
            xAxis: {
                title: {
                    enabled: true,
                    text: 'Genes'
                },
                categories: GENES,
                startOnTick: true,
                endOnTick: true,
                showLastLabel: true
            },
            yAxis: {
                title: {
                    text: 'Fold change'
                }
            },
            plotOptions: {
                scatter: {
                    marker: {
                        radius: 5,
                        states: {
                            hover: {
                                enabled: true,
                                lineColor: 'rgb(100,100,100)'
                            }
                        }
                    },
                    states: {
                        hover: {
                            marker: {
                                enabled: false
                            }
                        }
                    },
                    tooltip: {
                        headerFormat: '<b>gene: {point.x}</b><br>',
                        pointFormat: '<b>fc value:</b> {point.y}<br><b>p value:</b> {point.p_value}',
//                        pointFormat: '<b>fc value:</b> {point.y:.3f}<br><b>p value:</b> {point.value:.3f}',
                        formatter: function() {
                          return 'pvalue: <b>' + this.point.p_value + '</b>';
                        },
                    }
                }
            },
            series: [{
                name: cell_line,
                data: PLOT_SERIES,
                turboThreshold: turbo_threshold,
            }]
        });
    }
});