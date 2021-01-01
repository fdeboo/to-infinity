$(document).ready(function () {
    // Provides markup to input options

    let price;
    let priceTotal;

    // credit: https://stackoverflow.com/a/26549774/2342815
    // Renders a formatted price with no floating decimals unless necessary      
    String.prototype.insert = function () {            
        if (this.substr(-3) === '.00') {
            priceInt = this.slice(0, -3); // Removes trailing zeros
            return priceInt.substring(0, (priceInt.length - 3)) +
            ',' + priceInt.substr(-3); // Formats with a thousands separator ','
        } else {
            priceFloat = this;
            return priceFloat.substring(0, (priceFloat.length - 3)) + ',' +
            priceFloat.substr(-3);
        }
    };
        
    $('.date-option').each(function (index) {
        // Applies html markup and css to data passed in the input labels
        const text = $(this).text();
        const text_array = text.split(" ");
        const dayHtml = '<span class="day">' + text_array[0] + '</span>';
        const date = text_array[1] + " " + text_array[2] + " " + text_array[3];
        const price = text_array[4]
        const priceHtml = '<span class="price">' + price.insert() + '</span>';
        const htmlString = dayHtml + " " + date + " " + priceHtml;
        $(this).html(htmlString);
    });
    $('.date-option').addClass('formatted-label');
    $('.day').addClass('formatted-day');
    $('.price').addClass('formatted-price');
});

$('#confirm-btn').click(function() {
    // Calculates the booking total using data values from context and applies result to modal
    if (typeof price == 'undefined') {
        const quantity = Number($('#quantity').text());
        const strPrice = $('#cost').text();
        const numPrice = Number(strPrice);
        const math = String(quantity * numPrice);
        priceTotal = math.insert();
        price = strPrice.insert();
    }       
    $('#total').text("Total: £" +  priceTotal);
    $('#cost').text(price);

    $("input[type='radio']:checked").each(function() {
        // Populates modal with date selected in form and converts to d/m/y
        const radioId = $(this).attr("id");
        const labelText = $("label[for='"+ radioId + "']").text();
        const arrayText = labelText.split(" ");
        const dateString = arrayText[0] + " " + arrayText[1] + " " + arrayText[2] + " " + arrayText[3];
        const dateChoice = new Date(dateString);
        const day = dateChoice.getDate();
        const month = dateChoice.getMonth() + 1;
        const year = dateChoice.getFullYear();

        $('#date-choice').text(day + "/" + month + "/" + year);
        
    })
})