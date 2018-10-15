$(document).ready(function() {
    $('#plot_button').on('click', function() {
        var cell_line = $('#cell_line_select').val();
        console.log(cell_line);

        var cell_lines = $('#cell_line_chart').attr('data-cell-lines').replace(/'/g, '"'); //");
        console.log(cell_lines);
        cell_lines = JSON.parse(cell_lines);
        var plot_data = cell_lines[cell_line];
        console.log(plot_data);
        var genes = $('#cell_line_chart').attr('data-genes').replace(/'/g, '"'); //");
        console.log(genes);
        genes = JSON.parse(genes);
        console.log(genes);
        Highcharts.chart('cell_line_chart', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: 'Fold change values'
            },
            xAxis: {
                title: {
                    enabled: true,
                    text: 'Genes'
                },
                categories: genes,
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
                        headerFormat: '<b>{series.name}</b><br>',
                        pointFormat: '{point.y}'
                    }
                }
            },
            series: [{
                name: cell_line,
                data: plot_data,
            }]
        });
    });
});