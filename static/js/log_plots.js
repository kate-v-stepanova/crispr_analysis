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
        var left = $('#cell_line_chart').attr('data-left-line');
        var right = $('#cell_line_chart').attr('data-right-line');
        var bottom = $('#cell_line_chart').attr('data-bottom-line');
        var chart = Highcharts.chart('cell_line_chart', {
            chart: {
                type: 'scatter',
                zoomType: 'xy',
                height: 600,
            },
            legend: {
                enabled: false
            },
            title: {
                text: 'Fold change against p value for selected cell line:<b>' + cell_line + '</b>'
            },
            xAxis: {
                title: {
                    text: 'log2(fc)'
                },
                plotLines: [{
                    color: 'black',
                    dashStyle: 'dash',
                    value: right,
                    width: 1,
                    label: {
                        text: 'log2(fc)=' + right,
                    }
                },
                {
                    color: 'black',
                    dashStyle: 'dash',
                    value: left,
                    width: 1,
                    label: {
                        text: 'log2(fc)=' + left,
                    }
                }]
            },
            yAxis: {
                title: {
                    text: '-log10(pval)'
                },
                plotLines: [{
                    color: 'black',
                    dashStyle: 'dash',
                    value: bottom,
                    width: 1,
                    label: {
                        text: '-log10(pval)=' + bottom,
                    }
                }]
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
                        headerFormat: '<b>cell line: ' + cell_line +'</b><br>',
                        pointFormatter: function() {
                            var log_10;
                            if (this.infinity == true) {
                                log_10 = 'plus infinity'
                            } else {
                                log_10 = this.y
                            }
                            return '<b>gene: ' + this.gene_id + '</b><br>' +
                            '<b>log2(pval):</b>' + this.x + '<br><b>-log10(fc):</b> ' + log_10 +'<br>' +
                                '<b>p value:</b>' + this.pval + '<br><b>fc:</b> ' + this.fc;
                        },
                    }
                }
            },
            series: PLOT_SERIES,
        });
        Highcharts.chart('cell_line_chart_small', {
            chart: {
                type: 'scatter',
                zoomType: 'xy',
                height: 600,
            },
            legend: {
                enabled: false
            },
            title: {
                text: 'Fold change against p value for selected cell line:<b>' + cell_line + '</b>'
            },
            xAxis: {
                title: {
                    text: 'log2(fc)'
                },
                plotLines: [{
                    color: 'black',
                    dashStyle: 'dash',
                    value: right,
                    width: 1,
                    label: {
                        text: 'log2(fc)=' + right,
                    }
                },
                {
                    color: 'black',
                    dashStyle: 'dash',
                    value: left,
                    width: 1,
                    label: {
                        text: 'log2(fc)=' + left,
                    }
                }]
            },
            yAxis: {
                title: {
                    text: '-log10(pval)'
                },
                plotLines: [{
                    color: 'black',
                    dashStyle: 'dash',
                    value: bottom,
                    width: 1,
                    label: {
                        text: '-log10(pval)=' + bottom,
                    }
                }]
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
                        headerFormat: '<b>cell line: ' + cell_line +'</b><br>',
                        pointFormatter: function() {
                            var log_10;
                            if (this.infinity == true) {
                                log_10 = 'plus infinity'
                            } else {
                                log_10 = this.y
                            }
                            return '<b>gene: ' + this.gene_id + '</b><br>' +
                            '<b>log2(pval):</b>' + this.x + '<br><b>-log10(fc):</b> ' + log_10 +'<br>' +
                                '<b>p value:</b>' + this.pval + '<br><b>fc:</b> ' + this.fc;
                        },
                    }
                }
            },
            series: PLOT_SERIES,
        });
    }

    // resize cell_line_chart when hide counts
    $('#hide_counts').on('click', function() {
        $('#plot_with_counts').addClass('d-none');
        $('#cell_line_chart').removeClass('d-none');
    });

    function renderBoxplot(e) {
        var gene = this.gene_id;
        var cell_line = $('#cell_line_select').val();
        $('#plot_with_counts').removeClass('d-none');
        $('#cell_line_chart').addClass('d-none');
        $('#hide_counts').removeClass('d-none');
        $.post('/get_norm_counts/' + gene + "/" + cell_line, function(data, status) {
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
                        categories: [cell_line],
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
});