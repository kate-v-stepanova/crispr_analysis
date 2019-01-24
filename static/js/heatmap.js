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
        var chart = Highcharts.chart('heatmap_chart', {
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
                    [0.3, '#8EBDEA'],
                    [0.5, '#ffffff'],
                    [0.8, '#ec9b97'],
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
                    return '<b>' + this.point.cell_line + '</b><br><b>gene: </b>' +
                    '<b>' + this.point.gene_id + '</b><br><b>FC: </b>' + this.point.value +
                        '<br><b>p value: </b>' + this.point.pval + '<br><b>increased essentiality: </b>' + this.point.inc_ess;
                }
            },


            plotOptions: {
                series: {
                    events: {
                        click: renderBoxplot
                    }
                }
            },
            series: [{
                name: 'Fold Changes',
                borderWidth: 1,
                data: PLOT_SERIES,
                pointStart: 0,
                pointInterval: 1,
                turboThreshold: 7000,
                dataLabels: {
                    enabled: true,
                    color: '#000000'
                }
            }]

        });
    }

    function renderBoxplot(e) {
        var gene = e.point.gene_id;
        var cell_lines = $('#multiple_cell_lines').val();
        $('#boxplot_data').removeClass('col-sm-0').addClass('col-sm-4');
        $('#boxplot_data').removeClass('d-none');
        $('#heatmap_chart').removeClass('col-sm-12').addClass('col-sm-8');
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
                        type: 'boxplot',
                        height: '500',
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

    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    // resize cell_line_chart when hide counts
    $('#hide_counts').on('click', function() {
        $('#hide_counts').addClass('d-none');
        $('#boxplot_data').addClass('d-none');
        $('#boxplot_data').removeClass('col-sm-4').addClass('col-sm-0');
        $('#heatmap_chart').removeClass('col-sm-0').addClass('col-sm-12');
        var chart_width = $('#cell_line_chart').width();
        var chart_height = chart.height;
        chart.setSize(chart_width, chart_height, doAnimation=true);
    });

});