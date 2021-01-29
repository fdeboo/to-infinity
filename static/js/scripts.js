$(document).ready(function () {
    // Overrides the browser default styling for invalid input of required fields
    $("input, select").on({
        invalid: (e) => $(e.target).addClass("invalid"),
        input: (e) => $(e.target).removeClass("invalid", e.target.validity.valid),
    });

    if ($('#selected-trip').val() == '') {
        $('#passengers-max').prop("disabled", true);
    }
    else {
        let maxNm = $('#selected-trip option:selected').data('maxNum');
    $('#passengers-max').attr("max", maxNm).prop("disabled", false);
    }
});

$('#selected-trip').change(function() {
    console.log('changed');
    if ($('#selected-trip').val() == '') {
        $('#passengers-max').prop("disabled", true);
    }
    else {
        let maxNm = $('#selected-trip option:selected').data('maxNum');         
        $('#passengers-max').attr("max", maxNm).prop("disabled", false);
    }
});

$(".toggle-form").click(function () {
    $(".search-trips-form").toggleClass("position-translate", 1000);
    $(this).toggleClass("bottom-translate", 1000);
});