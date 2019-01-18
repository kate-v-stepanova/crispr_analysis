$(document).ready(function() {
    // prettify multiselect
    var choices = new Choices('#multiple_cell_lines', {
        allowSearch: true,
        removeItemButton: true
    });


    $(document).on('change', '#apply_filters', function() {
        if(this.checked) {
          $('#data_filters').removeClass('d-none');
        } else {
            $('#data_filters').addClass('d-none');
        }
    });

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
        var cell_lines = $('#multiple_cell_lines').val();
        var chart = Highcharts.chart('cell_line_chart', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: 'Fold change values for <b>' + cell_lines + '</b>'
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
            legend: {
                labelFormatter: function () {
                    return this.name + ': ' + this.options.series_length +' genes <i>(click to hide)</i>';
                }
            },
            plotOptions: {
                scatter: {
                    point: {
                        events: {
                            click: renderBoxplot
                        }
                    },
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
    function renderBoxplot(e) {
        var gene = this.name;
        var cell_lines = $('#multiple_cell_lines').val();
        $('#boxplot_data').removeClass('col-sm-0').addClass('col-sm-4');
        $('#boxplot_data').removeClass('d-none');
        $('#cell_line_chart').removeClass('col-sm-12').addClass('col-sm-8');
        var chart_width = $('#cell_line_chart').width();
        var chart_height = $('#cell_line_chart').height();
        chart.setSize(chart_width, chart_height, doAnimation=true);
        $('#hide_counts').removeClass('d-none');
        $.post('/get_norm_counts/' + gene + "/" + cell_lines, function(data, status) {
            if (status == 'success' && data.length != 0) {
                if (data['errors'].length != 0) {
                    $('#error_messages').html("");
                    for (i=0; i<data['errors'].length; i++) {
                        $('#error_messages').append("<p>"+data['errors'][i] + "</p>")
                    }

                    $('#error_div').removeClass('d-none');
                }
                Highcharts.chart('boxplot_data', {
                    chart: {
                        type: 'boxplot'
                    },
                    title: {
                        text: 'Normalized Counts for gene: ' + gene
                    },

                    legend: {
                        enabled: true
                    },

                    xAxis: {
                        categories: cell_lines,
                        title: {
                            text: 'Cell Line'
                        }
                    },

                    yAxis: {
                        title: {
                            text: 'Normalized counts'
                        },
                    },

                    legend: {
                        labelFormatter: function() {
                            if (this.name == 'Outliers') {
                                return 'click to hide outliers';
                            } else {
                                return this.name;
                            }
                        }
                    },
                    series: data['data'],
                });
            } else {
                $('#boxplot_data').html('No data found for the gene <b>' + gene + "</b>");
            }
        });
    }

    // resize cell_line_chart when hide counts
    $('#hide_counts').on('click', function() {
        $('#hide_counts').addClass('d-none');
        $('#boxplot_data').addClass('d-none');
        $('#boxplot_data').removeClass('col-sm-4').addClass('col-sm-0');
        $('#cell_line_chart').removeClass('col-sm-0').addClass('col-sm-12');
        var chart_width = $('#cell_line_chart').width();
        var chart_height = chart.height;
        chart.setSize(chart_width, chart_height, doAnimation=true);
    });

    var data_table = $('#data_table');
    if (data_table.length != 0) {
        var table_data = $(data_table).attr('table-csv-data');
        $(data_table).removeAttr('table-csv-data');
        $('#export_button').on('click', function() {
            var blob = new Blob([table_data], {type: "text/plain;charset=utf-8"});
            saveAs(blob, cell_lines.join('_') + "_comparison.csv");
        });
    }


    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });
});