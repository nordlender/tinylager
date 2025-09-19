// scripts.js

function updateCounter(item, stock) {
    let input = document.getElementById("count-" + item);
    let info = document.getElementById("info-" + item);
    let val = parseInt(input.value) || 0;

    if (val >= 1) {
        info.classList.add("bg-brand", "text-white");
    } else {
        info.classList.remove("bg-brand", "text-white");
    }

    if (val < 0) input.value = 0;
    if (val > stock) input.value = stock;

    updateBarState();
}

function filterItems() {
    let filter = document.getElementById("category-filter").value;
    let items = document.querySelectorAll(".item-wrapper");
    items.forEach(item => {
        if (filter === "all" || item.dataset.category === filter) {
            item.style.display = "flex";
        } else {
            item.style.display = "none";
        }
    });
}

function updateBarState() {
    let inputs = document.querySelectorAll('input[type="number"]');
    let total = 0;
    inputs.forEach(input => total += parseInt(input.value) || 0);

    let bar = document.getElementById("bottom-bar");
    let count = document.getElementById("bag-count");

    if (total > 0) {
        bar.classList.remove("opacity-50");
        bar.classList.add("opacity-100");
    } else {
        bar.classList.remove("opacity-100");
        bar.classList.add("opacity-50");
    }

    count.textContent = total;
}

// Reset all counters and highlights on page load
window.addEventListener("DOMContentLoaded", () => {
    let inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.value = 0;

        // Remove highlight from the item info panel
        let key = input.id.replace("count-", "");
        let info = document.getElementById("info-" + key);
        info.classList.remove("bg-brand", "text-white");
    });

		document.getElementById("category-filter").value = "all";

    updateBarState();
});
