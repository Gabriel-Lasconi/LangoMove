document.addEventListener("DOMContentLoaded", function () {
    const state = {
        type: "all",
        audio: "all",
        language: "all",
        search: ""
    };

    const items = Array.from(document.querySelectorAll(".pronunciation-item"));
    const typeButtons = Array.from(document.querySelectorAll("#type-filters .chip"));
    const audioButtons = Array.from(document.querySelectorAll("#audio-filters .chip"));
    const languageContainer = document.getElementById("language-filters");
    const searchInput = document.getElementById("pronunciation-search");
    const emptyState = document.getElementById("pronunciation-empty-state");
    const sectionHeaders = Array.from(document.querySelectorAll(".pronunciation-section-header"));
    const lists = Array.from(document.querySelectorAll(".pronunciation-items-list"));

    function deduplicateLanguageChips() {
        if (!languageContainer) return;

        const seen = new Set();
        const chips = Array.from(languageContainer.querySelectorAll(".pronunciation-language-chip"));

        chips.forEach((chip) => {
            const value = (chip.dataset.languageOption || "").trim().toLowerCase();
            if (!value || seen.has(value)) {
                chip.remove();
                return;
            }
            seen.add(value);
            chip.dataset.language = value;
        });
    }

    function setActive(buttons, key, value) {
        buttons.forEach((btn) => {
            btn.classList.toggle("active", btn.dataset[key] === value);
        });
    }

    function applyFilters() {
        let visibleCount = 0;
        const visibleByType = { vocabulary: 0, phrases: 0 };

        items.forEach((item) => {
            const itemType = item.dataset.itemType;
            const itemAudio = item.dataset.audioState;
            const itemLanguage = (item.dataset.language || "").trim().toLowerCase();
            const itemSearch = (item.dataset.search || "").toLowerCase();

            const matchesType = state.type === "all" || itemType === state.type;
            const matchesAudio = state.audio === "all" || itemAudio === state.audio;
            const matchesLanguage = state.language === "all" || itemLanguage === state.language;
            const matchesSearch = !state.search || itemSearch.includes(state.search);

            const visible = matchesType && matchesAudio && matchesLanguage && matchesSearch;
            item.style.display = visible ? "" : "none";

            if (visible) {
                visibleCount += 1;
                if (visibleByType[itemType] !== undefined) {
                    visibleByType[itemType] += 1;
                }
            }
        });

        sectionHeaders.forEach((header) => {
            const type = header.dataset.section;
            header.style.display = visibleByType[type] > 0 ? "" : "none";
        });

        lists.forEach((list) => {
            const type = list.dataset.listType;
            list.style.display = visibleByType[type] > 0 ? "" : "none";
        });

        if (emptyState) {
            emptyState.style.display = visibleCount === 0 ? "" : "none";
        }
    }

    typeButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            state.type = this.dataset.type;
            setActive(typeButtons, "type", state.type);
            applyFilters();
        });
    });

    audioButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            state.audio = this.dataset.audio;
            setActive(audioButtons, "audio", state.audio);
            applyFilters();
        });
    });

    if (languageContainer) {
        languageContainer.addEventListener("click", function (event) {
            const chip = event.target.closest(".chip");
            if (!chip) return;

            const allLanguageChips = Array.from(languageContainer.querySelectorAll(".chip"));
            allLanguageChips.forEach((c) => c.classList.remove("active"));
            chip.classList.add("active");

            state.language = chip.dataset.language || "all";
            applyFilters();
        });
    }

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            state.search = this.value.trim().toLowerCase();
            applyFilters();
        });
    }

    deduplicateLanguageChips();

    const allLanguageButton = document.querySelector('#language-filters .chip[data-language="all"]');
    if (allLanguageButton) {
        allLanguageButton.classList.add("active");
    }

    applyFilters();
});