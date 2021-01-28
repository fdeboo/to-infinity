$(".toggle-form").click(function () {
    $(".search-trips-form").toggleClass("position-translate", 1000);
    $(this).toggleClass("bottom-translate", 1000);
});