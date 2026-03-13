document.addEventListener("DOMContentLoaded", function () {
    const dropdown = document.querySelector("[data-volunteer-dropdown]");
    if (!dropdown) return;

    const trigger = dropdown.querySelector("[data-volunteer-trigger]");
    const triggerText = dropdown.querySelector("[data-volunteer-trigger-text]");
    const searchInput = dropdown.querySelector("[data-volunteer-search]");
    const list = dropdown.querySelector("[data-volunteer-list]");
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

    function resetFilter() {
        if (searchInput) {
            searchInput.value = "";
        }

        items.forEach((item) => {
            item.style.display = "";
        });

        if (list) {
            list.scrollTop = 0;
        }
    }

    function filterItems() {
        const query = (searchInput.value || "").trim().toLowerCase();

        items.forEach((item) => {
            const haystack = item.dataset.search || "";
            item.style.display = !query || haystack.includes(query) ? "" : "none";
        });

        if (list) {
            list.scrollTop = 0;
        }
    }

    function openDropdown() {
        dropdown.classList.add("open");
        resetFilter();

        if (searchInput) {
            setTimeout(() => searchInput.focus(), 0);
        }
    }

    function closeDropdown() {
        dropdown.classList.remove("open");
    }

    trigger.addEventListener("click", function (event) {
        event.preventDefault();

        if (dropdown.classList.contains("open")) {
            closeDropdown();
        } else {
            openDropdown();
        }
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