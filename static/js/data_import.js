$(document).ready(function() {
    $(document).on('click', 'span.close', function() {
        $(this).closest('div.alert').addClass('d-none');
    });

    $(document).on('submit', '#import_form', function() {
        alert('Please, note that data import might take between 30 minutes and 2 hours (in average). DO NOT CLOSE the browser, DO NOT RELOAD the page, DO NOT click any buttons. Just get some tea and wait till you see a green message upon success or red message upon a failed import');
    });

    $(document).on('click', '.download_example', function() {
        var filename = $(this).attr('id');
        $.post('/download/' + filename, function(data, status) {
            var blob = new Blob([data], {type: "text/plain;charset=utf-8"});
            saveAs(blob, filename + '.csv');
        });
    });
});