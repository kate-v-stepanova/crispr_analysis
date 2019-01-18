$(document).ready(function() {
    // prettify multiselect
    var choices = new Choices('#multiple_cell_lines', {
        allowSearch: true,
        removeItemButton: true
    });

    // show filters on selected
    $(document).on('change', '#filter_data', function() {
        if(this.value == "by_list_of_genes") {
          $('#filter_by_genes').removeClass('d-none');
          $('#filter_by_thresholds').addClass('d-none');
        } else if (this.value == "by_thresholds") {
          $('#filter_by_genes').addClass('d-none');
          $('#filter_by_thresholds').removeClass('d-none');
        } else if (this.value == "do_not_filter") {
          $('#filter_by_genes').addClass('d-none');
          $('#filter_by_thresholds').addClass('d-none');
        }
    });


    // initializing constants and removing attributes from html elements
    var PLOT_SERIES = $('#cluster_plot').attr('data-plot-series').replace(/'/g, '"'); //");
    console.log(PLOT_SERIES);
    if (PLOT_SERIES.length != 0) {
        PLOT_SERIES = JSON.parse(PLOT_SERIES);
    }
    var GENES = $('#cluster_plot').attr('data-genes').replace(/'/g, '"'); //");
    console.log(GENES);
    if (GENES.length != 0) {
        GENES = JSON.parse(GENES);
    }
//    var CELL_LINES = $('#cluster_plot').attr('data-cell-lines').replace(/'/g, '"'); //");
    // removing attributes
    $('#cluster_plot').removeAttr('data-genes');
    $('#cluster_plot').removeAttr('data-plot-series');
//    $('#cluster_plot').removeAttr('data-cell-lines');

    if (GENES.length != 0) {
        // initializing plot
        var cell_lines = $('#multiple_cell_lines').val();
        var chart = Highcharts.chart('cluster_plot', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: 'Gene clusters for selected cell lines: <b>' + cell_lines + '</b>'
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
                    text: 'Fold change of ' + cell_lines[0]
                }
            },
    //        legend: {
    //            labelFormatter: function () {
    //                return this.name + ': ' + this.options.series_length +' genes <i>(click to hide)</i>';
    //            }
    //        },
            plotOptions: {
                scatter: {
    //                point: {
    //                    events: {
    //                        click: renderBoxplot
    //                    }
    //                },
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
                        headerFormat: '<b>gene: {point.x}</b><br><b>cell line: {series.name}<br></b>',
                        pointFormat: '<b>fc value:</b> {point.y}<br><b>p value:</b> {point.pval}' +
                                    '<br><b>increased Essentiality:</b> {point.inc_ess}<br>(click to see norm. counts)',
                    }
                }
            },
            series: PLOT_SERIES
        });
    }
});