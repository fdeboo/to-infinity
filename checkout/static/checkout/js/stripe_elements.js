/* 
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here:
    https://stripe.com/docs/stripe-js
*/

const stripePublicKey = $("#id_stripe_public_key").text().slice(1, -1);
const clientSecret = $("#id_client_secret").text().slice(1, -1);
const stripe = Stripe(stripePublicKey);
const elements = stripe.elements();
const style = {
    base: {
        color: "#000",
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: "antialiased",
        fontSize: "16px",
        "::placeholder": {
            color: "#aab7c4",
        },
    },
    invalid: {
        color: "#dc3545",
        iconColor: "#dc3545",
    },
};
const card = elements.create("card", { style: style });
card.mount("#card-element");

// Handle realtime validation errors on the card element
card.addEventListener("change", function (event) {
    const errorDiv = document.getElementById("card-errors");
    if (event.error) {
        const errorDiv = document.getElementById("card-errors");
        const html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>`;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = "";
    }
    });

// Handle form submit
const form = document.getElementById("payment-form");

// When a user clicks the submit button,
// The Event Listener prevents the form from submitting,
// Instead disables the card element
// and triggers the loading-overlay.

form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    card.update({ disabled: true });
    $("#submit-button").attr("disabled", true);
    $("#payment-form").fadeToggle(100);
    $("#loading-overlay").fadeToggle(100);
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        }    
    }).then(function (result) {
        if (result.error) {
            const html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);
            $("#payment-form").fadeToggle(100);
            $("#loading-overlay").fadeToggle(100);
            card.update({ disabled: false });
            $("#submit-button").attr("disabled", false);
        } else {
            if (result.paymentIntent.status === "succeeded") {
                form.submit();
            }
        }
    });
});
