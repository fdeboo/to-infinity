let selectedLabel;
let selectedTab;

$(document).ready(function () {
    selectedTab = $("input[type='radio']:checked").attr("id");
    selectedLabel = $("input[type='radio']:checked + label");
    const selectedIconSrc = $(selectedLabel).children("img").attr("src");
    const selectedSrc = selectedIconSrc.slice(0, -8) + ".png";
    $(selectedLabel).children("img").attr("src", selectedSrc);

    const selectDivId = "#div-" + selectedTab;
    $(selectDivId).addClass("d-block");
});


$("input[type='radio']").change(function () {
    const unselectedIconSrc = $(selectedLabel).children("img").attr("src");
    const unselectedTab = selectedTab;
    const unselectedSrc = unselectedIconSrc.slice(0, -4) + "_fff.png";
    $(selectedLabel).children("img").attr("src", unselectedSrc);

    selectedTab = $("input[type='radio']:checked").attr("id");
    selectedLabel = $("input[type='radio']:checked + label");

    const selectedIconSrc = $(selectedLabel).children("img").attr("src");
    const selectedSrc = selectedIconSrc.slice(0, -8) + ".png";
    $(selectedLabel).children("img").attr("src", selectedSrc);
    
    const selectDivId = "#div-" + selectedTab;
    $(selectDivId).addClass("d-block");
    const unselectDivId = "#div-" + unselectedTab;
    $(unselectDivId).removeClass("d-block");
    
    
    

    



});


$(".toggle-form").click(function () {
    $(".search-trips-form").toggleClass("position-translate");
});