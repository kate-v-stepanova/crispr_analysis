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

        Highcharts.chart('cell_line_chart', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: 'Fold change against p value for selected cell line:<b>' + cell_line + '</b>'
            },
            xAxis: {
                title: {
                    text: 'log2(fc)'
                },
            },
            yAxis: {
                title: {
                    text: '-log10(pval)'
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
                        headerFormat: '<b>cell line: {point.series.name}</b><br>',
                        pointFormat: '<b>gene: {point.gene_id}</b><br>' +
                                '<b>log2(pval):</b> {point.y}<br><b>-log10(fc):</b> {point.x}<br>' +
                                    '<b>p value:</b> {point.pval}<br><b>fc:</b> {point.fc}',
                    }
                }
            },
            series: PLOT_SERIES,
        });
    }
});