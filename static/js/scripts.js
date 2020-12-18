
    $(document).ready(function () {
        if ($('#selected-trip').val() == '') {
            $('#passengers-max').prop("disabled", true);
        }
        else {
            let maxNm = $('#selected-trip option:selected').data('maxNum');
        $('#passengers-max').attr("max", maxNm).prop("disabled", false);
        }
    });
    
    $('#selected-trip').change(function() {
        if ($('#selected-trip').val() == '') {
            $('#passengers-max').prop("disabled", true);
        }
        else {
            let maxNm = $('#selected-trip option:selected').data('maxNum');         
            $('#passengers-max').attr("max", maxNm).prop("disabled", false);
        }
    });

    $('.toggle-form').click(function(){
        $(".search-trips-form").toggleClass("position-translate");
    });
        
