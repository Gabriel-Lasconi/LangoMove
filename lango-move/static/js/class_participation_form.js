document.addEventListener("DOMContentLoaded", function () {
    function closeAllDropdowns(exceptDropdown = null) {
        document.querySelectorAll("[data-dropdown-root]").forEach((dropdown) => {
            if (dropdown !== exceptDropdown) {
                dropdown.classList.remove("open");
                const field = dropdown.closest(".auth-field");
                if (field) {
                    field.classList.remove("dropdown-open");
                }
            }
        });
    }

    function setupMultiSelectDropdown(config) {
        const dropdown = document.querySelector(config.rootSelector);
        if (!dropdown) return;

        const trigger = dropdown.querySelector(config.triggerSelector);
        const triggerText = dropdown.querySelector(config.triggerTextSelector);
        const searchInput = dropdown.querySelector(config.searchSelector);
        const list = dropdown.querySelector(config.listSelector);
        const items = Array.from(dropdown.querySelectorAll(config.itemSelector));
        const inputs = Array.from(dropdown.querySelectorAll(config.inputSelector));
        const field = dropdown.closest(".auth-field");

        function updateTriggerText() {
            const checked = inputs.filter((input) => input.checked);

            if (checked.length === 0) {
                triggerText.textContent = config.emptyText;
                return;
            }

            if (checked.length === 1) {
                const label = checked[0].closest(config.itemSelector);
                const name = label.querySelector("strong")?.textContent?.trim() || config.singleFallbackText;
                triggerText.textContent = name;
                return;
            }

            triggerText.textContent = `${checked.length} ${config.multipleText}`;
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
            closeAllDropdowns(dropdown);
            dropdown.classList.add("open");
            if (field) {
                field.classList.add("dropdown-open");
            }
            resetFilter();

            if (searchInput) {
                setTimeout(() => searchInput.focus(), 0);
            }
        }

        function closeDropdown() {
            dropdown.classList.remove("open");
            if (field) {
                field.classList.remove("dropdown-open");
            }
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

        inputs.forEach((input) => {
            input.addEventListener("change", updateTriggerText);
        });

        updateTriggerText();
    }

    function setupSingleSelectDropdown(config) {
        const dropdown = document.querySelector(config.rootSelector);
        if (!dropdown) return;

        const trigger = dropdown.querySelector(config.triggerSelector);
        const triggerText = dropdown.querySelector(config.triggerTextSelector);
        const searchInput = dropdown.querySelector(config.searchSelector);
        const list = dropdown.querySelector(config.listSelector);
        const items = Array.from(dropdown.querySelectorAll(config.itemSelector));
        const inputs = Array.from(dropdown.querySelectorAll(config.inputSelector));
        const field = dropdown.closest(".auth-field");

        function updateTriggerText() {
            const checked = inputs.find((input) => input.checked);

            if (!checked) {
                triggerText.textContent = config.emptyText;
                return;
            }

            const label = checked.closest(config.itemSelector);
            const name = label.querySelector("strong")?.textContent?.trim() || config.singleFallbackText;
            triggerText.textContent = name;
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
            closeAllDropdowns(dropdown);
            dropdown.classList.add("open");
            if (field) {
                field.classList.add("dropdown-open");
            }
            resetFilter();

            if (searchInput) {
                setTimeout(() => searchInput.focus(), 0);
            }
        }

        function closeDropdown() {
            dropdown.classList.remove("open");
            if (field) {
                field.classList.remove("dropdown-open");
            }
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

        inputs.forEach((input) => {
            input.addEventListener("change", function () {
                updateTriggerText();
                closeDropdown();
            });
        });

        updateTriggerText();
    }

    setupSingleSelectDropdown({
        rootSelector: "[data-teacher-dropdown]",
        triggerSelector: "[data-teacher-trigger]",
        triggerTextSelector: "[data-teacher-trigger-text]",
        searchSelector: "[data-teacher-search]",
        listSelector: "[data-teacher-list]",
        itemSelector: "[data-teacher-item]",
        inputSelector: ".teacher-dropdown-radio",
        emptyText: "Select teacher",
        singleFallbackText: "Teacher selected",
    });

    setupMultiSelectDropdown({
        rootSelector: "[data-volunteer-dropdown]",
        triggerSelector: "[data-volunteer-trigger]",
        triggerTextSelector: "[data-volunteer-trigger-text]",
        searchSelector: "[data-volunteer-search]",
        listSelector: "[data-volunteer-list]",
        itemSelector: "[data-volunteer-item]",
        inputSelector: ".volunteer-dropdown-checkbox",
        emptyText: "Select volunteers",
        singleFallbackText: "1 volunteer",
        multipleText: "volunteers selected",
    });
});