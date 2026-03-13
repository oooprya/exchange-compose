document.addEventListener("DOMContentLoaded", function () {

    const typeField = document.querySelector("#id_order_type");
    const rateRow = document.querySelector(".form-row.field-rate");
    const baseRow = document.querySelector(".form-row.field-amount_base");

    function toggleFields() {
        if (!typeField) return;

        if (typeField.value === "in" || typeField.value === "out") {
            if (rateRow) rateRow.style.display = "none";
            if (baseRow) baseRow.style.display = "none";
        } else {
            if (rateRow) rateRow.style.display = "";
            if (baseRow) baseRow.style.display = "";
        }
    }

    if (typeField) {
        toggleFields();
        typeField.addEventListener("change", toggleFields);
    }

});