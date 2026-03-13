document.addEventListener("DOMContentLoaded", function () {
    const dropdown = document.querySelector("[data-volunteer-dropdown]");
    if (!dropdown) return;

    const trigger = dropdown.querySelector("[data-volunteer-trigger]");
    const triggerText = dropdown.querySelector("[data-volunteer-trigger-text]");
    const panel = dropdown.querySelector("[data-volunteer-panel]");
    const searchInput = dropdown.querySelector("[data-volunteer-search]");
    const items = Array.from(dropdown.querySelectorAll("[data-volunteer-item]"));
    const checkboxes = Array.from(dropdown.querySelectorAll(".volunteer-dropdown-checkbox"));

    function updateTriggerText() {
        const checked = checkboxes.filter((cb) => cb.checked);
        if (checked.length === 0) {
            triggerText.textContent = "Select volunteers";
            return;
        }

        if (checked.length === 1) {
            const label = checked[0].closest("[data-volunteer-item]");
            const name = label.querySelector("strong")?.textContent?.trim() || "1 volunteer";
            triggerText.textContent = name;
            return;
        }

        triggerText.textContent = `${checked.length} volunteers selected`;
    }

    function openDropdown() {
        dropdown.classList.add("open");
    }

    function closeDropdown() {
        dropdown.classList.remove("open");
    }

    function filterItems() {
        const query = (searchInput.value || "").trim().toLowerCase();

        items.forEach((item) => {
            const haystack = item.dataset.search || "";
            const matches = !query || haystack.includes(query);
            item.style.display = matches ? "" : "none";
        });
    }

    trigger.addEventListener("click", function (event) {
        event.preventDefault();
        dropdown.classList.toggle("open");
    });

    document.addEventListener("click", function (event) {
        if (!dropdown.contains(event.target)) {
            closeDropdown();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeDropdown();
        }
    });

    if (searchInput) {
        searchInput.addEventListener("input", filterItems);
    }

    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", updateTriggerText);
    });

    updateTriggerText();
});