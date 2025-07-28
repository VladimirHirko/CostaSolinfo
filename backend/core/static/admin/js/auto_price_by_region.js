document.addEventListener("DOMContentLoaded", function () {
    const excursionSelect = document.getElementById("id_excursion");
    const hotelSelect = document.getElementById("id_hotel");
    const priceAdultInput = document.getElementById("id_price_adult");
    const priceChildInput = document.getElementById("id_price_child");

    async function updatePrices() {
        if (!excursionSelect || !hotelSelect) return;
        const excursionId = excursionSelect.value;
        const hotelId = hotelSelect.value;
        if (!excursionId || !hotelId) return;

        try {
            const response = await fetch(`/api/get-excursion-price/?excursion=${excursionId}&hotel=${hotelId}`);
            if (response.ok) {
                const data = await response.json();
                priceAdultInput.value = data.price_adult || "";
                priceChildInput.value = data.price_child || "";
            }
        } catch (e) {
            console.error("Ошибка загрузки цен:", e);
        }
    }

    if (excursionSelect) excursionSelect.addEventListener("change", updatePrices);
    if (hotelSelect) hotelSelect.addEventListener("change", updatePrices);
});
