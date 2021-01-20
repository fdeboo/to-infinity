let price;
let priceTotal;

// credit: https://stackoverflow.com/a/26549774/2342815
// Renders a formatted price with no floating decimals unless necessary
String.prototype.insert = function () {
  if (this.substr(-3) === ".00") {
    priceInt = this.slice(0, -3); // Removes trailing zeros
    return (
      priceInt.substring(0, priceInt.length - 3) + "," + priceInt.substr(-3)
    ); // Formats with a thousands separator ','
  } else {
    priceFloat = this;
    return (
      priceFloat.substring(0, priceFloat.length - 3) +
      "," +
      priceFloat.substr(-3)
    );
  }
};

$(document).ready(function () {
  // Provides markup to input options

  const selected = $("input[type='radio']:checked");
  $(selected).siblings(".block").css("background-color", "#99B821");
  $(selected).siblings().children(".block").css("background-color", "#99B821");

  $(".date-option").each(function (index) {
    // Applies html markup and css to data passed in the input labels
    const text = $(this).text();
    const text_array = text.split(" ");
    const dayHtml =
      '<h2 class="day"><i class="fas fa-check fa-lg mb-2 d-block"></i>' +
      text_array[0] +
      "</h2>";
    const date = text_array[1] + " " + text_array[2] + " " + text_array[3];
    const price = text_array[4];
    const priceHtml =
      '<p class="price mt-2">' +
      '<i class="fas fa-user pr-1 text-right"></i> x ' +
      price.insert() +
      "</p>";
    const htmlString = dayHtml + " " + date + " " + priceHtml;
    $(this).html(htmlString);
  });
  $(".date-option").addClass("formatted-label");
  $(".day").addClass("formatted-day");
  $(".price").addClass("formatted-price");
});

$("input[type='radio']").change(function () {
  const selected = $("input[type='radio']:checked");
  const unselected = $("input[type='radio']:not(':checked')");

  $(selected).siblings(".block").css("background-color", "#99B821");
  $(selected).siblings().children(".block").css("background-color", "#99B821");
  $(unselected).siblings(".block").css("background-color", "#0D3638");
  $(unselected)
    .siblings()
    .children(".block")
    .css("background-color", "#0D3638");
});

$("input[type='radio']").mouseover(function () {
  console.log("hovered");
  $(this).siblings(".block").css("background-color", "#2AB1B7");
  $(this).siblings().children(".block").css("background-color", "#2AB1B7");
  $(this).css("border", "1px solid #2AB1B7");
});

$("#confirm-btn").click(function () {
  // Calculates the booking total using data values from context and applies result to modal
  if (typeof price == "undefined") {
    const quantity = Number($("#quantity").text());
    const strPrice = $("#cost").text();
    const numPrice = Number(strPrice);
    const math = String(quantity * numPrice);
    priceTotal = math.insert();
    price = strPrice.insert();
  }
  $("#total").text("Total: £" + priceTotal);
  $("#cost").text(price);

  $("input[type='radio']:checked").each(function () {
    // Populates modal with date selected in form and converts to d/m/y
    const radioId = $(this).attr("id");
    const labelText = $("label[for='" + radioId + "']").text();
    const arrayText = labelText.split(" ");
    const dateString =
      arrayText[0] +
      " " +
      arrayText[1] +
      " " +
      arrayText[2] +
      " " +
      arrayText[3];
    const dateChoice = new Date(dateString);
    const day = dateChoice.getDate();
    const month = dateChoice.getMonth() + 1;
    const year = dateChoice.getFullYear();

    $("#date-choice").text(day + "/" + month + "/" + year);
  });
});

$("#update-btn").click(function () {
  /* 
  Updates the booking summary in the passenger details template,
  to include any checked items.
  */

  // Delete any existing markup in case any previous updates.
  $(".addon-row").remove();

  // Define a new empty array.
  let addOns = [];
  $("input:checked").each(function () {
    const htmlStr = $(this).siblings(".addon-item").find(".mb-0").html();
    const index = htmlStr.indexOf("<s");
    const addonName = htmlStr.substr(0, index).trim();
    const addonPrice = $(this)
      .siblings(".addon-item")
      .find(".mb-0")
      .children("span")
      .html();
    const addonImage = $(this)
      .siblings(".addon-item")
      .find(".addon-image")
      .children("img")
      .addClass("w-100")
      .removeClass("addon-image")
      .parent()
      .html();

    // Get index of object in the array if it already exists, or -1.
    let arrayIndex = addOns.findIndex((addon) => addon.name === addonName);

    // If returned value was -1, Create object and add to array.
    if (arrayIndex === -1) {
      addOn = {
        name: addonName,
        price: addonPrice,
        image: addonImage,
        qty: 1,
      };
      addOns.push(addOn);
    } else {
      // Increment the quantity value for the existitng object
      addOns[arrayIndex]["qty"] += 1;
    }
  });

  let strTotal = $("#booking-total").text().slice(0, -3).split(",");
  bookingTotal = Number(strTotal[0] + strTotal[1]);

  // Construct html for summary and append to existing html
  for (i = 0; i < addOns.length; i++) {
    let imgDiv, nameP, qtyP, priceP, detailDiv, priceDiv, row, total;

    total = parseFloat(addOns[i]["price"].slice(1) * addOns[i]["qty"]);
    nameP = "<p class='my-0'><strong>" + addOns[i]["name"] + "</strong></p>";
    qtyP = "<p class='my-0 small text-muted'>Travellers: " + addOns[i]["qty"] + "</p>";
    priceP = "<p class='my-0 small text-muted'>" + total.toFixed(2) + "</p>";
    detailDiv = "<div class='col-6'>" + nameP + qtyP + "</div>";
    priceDiv = "<div class='col-4 mb-1 text-right'>" + priceP + "</div>";
    imgDiv = "<div class='col-2 mb-1'>" + addOns[i]["image"] + "</div>";
    row =
      "<div class='addon-row row'>" + imgDiv + detailDiv + priceDiv + "</div>";

    bookingTotal += total;
    let formattedTotal = String(bookingTotal).insert();
    console.log(formattedTotal);
    $("#booking-total").text(formattedTotal + ".00");
    $("#summary").append(row);
  }
});
