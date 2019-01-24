$(document).ready(function() {
    // prettify multiselect
    var choices = new Choices('#multiple_cell_lines', {
        allowSearch: true,
        removeItemButton: true
    });

    // they all have to be of the same length
    var chart_containers = [];
    var titles = [];
    var y_axis_text = [];
    var plot_series = [];

    // for single_plot
    if ($('#cell_line_chart').length != 0) {
        // initializing constants and removing attributes from html elements
        var PLOT_SERIES = $('#cell_line_chart').attr('data-plot-series').replace(/'/g, '"'); //");
        if (PLOT_SERIES.length != 0) {
            PLOT_SERIES = JSON.parse(PLOT_SERIES);
            // removing attributes
            $('#cell_line_chart').removeAttr('data-plot-series');

            var x_axis = $('#first_cell_line').val();
            var y_axis = $('#multiple_cell_lines').val();

            chart_containers.push('cell_line_chart');
            titles.push('Fold change values selected cell lines:<b>' + x_axis + '</b> and <b>' + y_axis + '</b>');
            y_axis_text.push('Fold Change for ' + y_axis);
            plot_series.push(PLOT_SERIES);
        }
    } else { // for multiple plots
        var how_to_plot = $('input:radio:checked').val();
        if (how_to_plot == 'multiple_plots') {
            var x_axis = $('#first_cell_line').val();
            var y_axis = $('#multiple_cell_lines').val();
            for (i=0; i<y_axis.length; i++) {
                var cell_line = y_axis[i].trim();
                var PLOT_SERIES = $('#' + cell_line + '_chart').attr('data-plot-series').replace(/'/g, '"'); //");
                if (PLOT_SERIES.length != 0) {
                    PLOT_SERIES = JSON.parse(PLOT_SERIES);
                    // removing attributes
                    $('#' + cell_line + '_chart').removeAttr('data-plot-series');
                    chart_containers.push(cell_line + '_chart');
                    titles.push('Fold change values selected cell lines:<b>' + x_axis + '</b> and <b>' + cell_line + '</b>');
                    y_axis_text.push('Fold Change for ' + cell_line);
                    plot_series.push(PLOT_SERIES);
                }
            }
        }
    }

    for(i=0; i<chart_containers.length; i++) {
        // initializing plot(s)
        var chart = Highcharts.chart(chart_containers[i], {
            chart: {
                type: 'scatter',
                zoomType: 'xy',
                height: 600,
            },
            title: {
                text: titles[i]
            },
            xAxis: {
                title: {
                    text: 'Fold Change for ' + x_axis
                },
            },
            yAxis: {
                title: {
                    text: y_axis_text[i],
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
                        pointFormat: '<b>gene:</b> {point.gene_id}<br><b>' + x_axis + ' fc:</b> {point.x:.3f}<br><b>' +
                                    '<br><b>' + x_axis + ' p value: </b> {point.x_pval:.3f}' +
                                    '<br><b>{series.name} fc:</b> {point.y:.3f}' +
                                    '<br><b>{series.name} p value: </b> {point.y_pval:.3f}',
                    }
                }
            },
            series: plot_series[i],
            exporting: {
                fallbackToExportServer: false,
            }
        });
    }

    $(document).on('change', '#apply_filters', function() {
        if(this.checked) {
          $('#data_filters').removeClass('d-none');
        } else {
            $('#data_filters').addClass('d-none');
        }
    });

    $(document).on('change', '#first_cell_line', function() {
        var cell_line = $('#first_cell_line').val();
        console.log(cell_line);
        if (cell_line != 'select_cell_line') {
            $('#x_axis_filter').find('h2').text('X Axis Filter: ' + cell_line);
        }
    });
    $(document).on('change', '#multiple_cell_lines', function() {
        var cell_line = $('#multiple_cell_lines').val();
        if (cell_line != 'select_cell_line') {
            $('#y_axis_filter').find('h2').text('Y Axis Filter: ' + cell_line);
        }
    });

    // export data table
    var data_table = $('#data_table');
    if (data_table.length != 0) {
        var table_data = $(data_table).attr('table-csv-data');
        $(data_table).removeAttr('table-csv-data');
        $('#export_button').on('click', function() {
            var cell_lines = $('#multiple_cell_lines').val() + ',' + $('#first_cell_line').val();
            cell_lines = cell_lines.replace(/\,/g, '_');
            var blob = new Blob([table_data], {type: "text/plain;charset=utf-8"});
            saveAs(blob, cell_lines + "_comparison.csv");
        });
    }

    function renderBoxplot(e) {
        var gene = this.gene_id;
        var cell_lines = $('#multiple_cell_lines').val()+',' + $('#first_cell_line').val();
        cell_lines = cell_lines.split(',');
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

});