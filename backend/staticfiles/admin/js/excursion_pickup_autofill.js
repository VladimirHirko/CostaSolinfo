document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("select[name$='pickup_reference']").forEach(function (selectEl) {
        selectEl.addEventListener("change", function () {
            const pickupId = this.value;
            if (!pickupId) return;

            fetch(`/pickup-point/${pickupId}/`)
                .then((response) => response.json())
                .then((data) => {
                    const row = this.closest("tr");
                    if (!row) return;

                    row.querySelector("input[name$='pickup_point_name']").value = data.pickup_point_name || "";
                    row.querySelector("input[name$='latitude']").value = data.latitude || "";
                    row.querySelector("input[name$='longitude']").value = data.longitude || "";
                    row.querySelector("input[name$='pickup_time']").value = data.pickup_time || "";
                })
                .catch((err) => console.error("Ошибка загрузки PickupPoint:", err));
        });
    });
});
