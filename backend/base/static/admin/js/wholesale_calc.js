document.addEventListener("DOMContentLoaded", function() {

    function recalc() {
        let amount = document.getElementById("id_amount");
        let rate = document.getElementById("id_rate");
        let total = document.getElementById("id_uah_total");

        if (!amount || !rate || !total) return;

        let a = parseFloat(amount.value || 0);
        let r = parseFloat(rate.value || 0);

        total.value = (a * r).toFixed(2);
    }

    document.body.addEventListener("input", recalc);
});