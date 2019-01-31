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

    // close error message
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    // initializing constants and removing attributes from html elements
    var PLOT_SERIES = $('#cluster_plot').attr('data-plot-series').replace(/'/g, '"'); //");
    if (PLOT_SERIES.length != 0) {
        PLOT_SERIES = JSON.parse(PLOT_SERIES);
    }
    var GENES = $('#cluster_plot').attr('data-genes').replace(/'/g, '"'); //");
    if (GENES.length != 0) {
        GENES = JSON.parse(GENES);
    }
    var CELL_LINES = $('#cluster_plot').attr('data-cell-lines').replace(/'/g, '"'); //");
    if (CELL_LINES.length != 0) {
        CELL_LINES = JSON.parse(CELL_LINES);
    }
    // removing attributes
    $('#cluster_plot').removeAttr('data-genes');
    $('#cluster_plot').removeAttr('data-plot-series');
    $('#cluster_plot').removeAttr('data-cell-lines');


    if (GENES.length != 0) {
        // initializing plot
        var chart = Highcharts.chart('cluster_plot', {
            chart: {
                type: 'scatter',
                zoomType: 'xy',
            },
            title: {
                text: 'Clustered genes from cell lines: <b>' + CELL_LINES + '</b>'
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
                        headerFormat: '',
                        pointFormat: '<b>Cluster {point.cluster} ({point.cluster_size} genes)<br></b><b>gene:</b> {point.gene_id}<br><b>cell line:</b> {point.cell_line}<br>' +
                                    '<b>fc value:</b> {point.y}<br><b>p value:</b> {point.pval}' +
                                    '<br>(click to see norm. counts)',
                    }
                }
            },
            series: PLOT_SERIES,
            legend: {
                enabled: false,
            }
        });

        // initializing plot
        var chart = Highcharts.chart('cluster_plot_small', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            legend: {
                align: 'right',
                verticalAlign: 'top',
                layout: 'vertical',
                x: 0,
                y: 100
            },
            title: {
                text: 'Clustered genes from cell lines: <b>' + CELL_LINES + '</b>'
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
                        headerFormat: '',
                        pointFormat: '<b>Cluster {point.cluster} ({point.cluster_size} genes)<br></b><b>gene:</b> {point.gene_id}<br><b>cell line:</b> {point.cell_line}<br>' +
                                    '<b>fc value:</b> {point.y}<br><b>p value:</b> {point.pval}' +
                                    '<br>(click to see norm. counts)',
                    }
                }
            },
            series: PLOT_SERIES,
        });
    }

    // resize cell_line_chart when hide counts
    $('#hide_counts').on('click', function() {
        $('#hide_counts').addClass('d-none');
        $('#plot_with_counts').addClass('d-none');
        $('#cluster_plot').removeClass('d-none');
    });

    function renderBoxplot(e) {
        var gene = this.gene_id;
        var cell_lines = $('#multiple_cell_lines').val();
        $('#plot_with_counts').removeClass('d-none');
        $('#cluster_plot').addClass('d-none');
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

                    xAxis: {
                        categories: CELL_LINES,
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


    var data_table = $('#data_table');
    if (data_table.length != 0) {
        var table_data = $(data_table).attr('table-csv-data');
        $(data_table).removeAttr('table-csv-data');
        $('#export_button').on('click', function() {
            var blob = new Blob([table_data], {type: "text/plain;charset=utf-8"});
            saveAs(blob, CELL_LINES.join('_') + "_clusters.csv");
        });
    }
});