document.addEventListener("DOMContentLoaded", function() {

    const currency = document.getElementById("id_currency");
    const rate = document.getElementById("id_rate");

    function loadRate() {
        // Тут можно потом сделать ajax к API
        console.log("Можно подгружать курс");
    }

    if (currency) {
        currency.addEventListener("change", loadRate);
    }
});