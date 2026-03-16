document.addEventListener("DOMContentLoaded", function () {
    const state = {
        type: "all",
        audio: "all",
        language: "all",
        pos: "all",
        topic: "all",
        search: ""
    };

    const items = Array.from(document.querySelectorAll(".pronunciation-item"));

    const typeButtons = Array.from(document.querySelectorAll("#type-filters .chip"));
    const audioButtons = Array.from(document.querySelectorAll("#audio-filters .chip"));
    const languageButtons = Array.from(document.querySelectorAll("#language-filters .chip"));
    const posButtons = Array.from(document.querySelectorAll("#pos-filters .chip"));
    const topicButtons = Array.from(document.querySelectorAll("#topic-filters .chip"));

    const vocabularyOnlyFilters = document.getElementById("vocabulary-only-filters");
    const posFilterGroup = document.getElementById("pos-filter-group");
    const topicFilterGroup = document.getElementById("topic-filter-group");

    const searchInput = document.getElementById("pronunciation-search");
    const emptyState = document.getElementById("pronunciation-empty-state");
    const sectionHeaders = Array.from(document.querySelectorAll(".pronunciation-section-header"));
    const lists = Array.from(document.querySelectorAll(".pronunciation-items-list"));

    const resultsCount = document.getElementById("pronunciation-results-count");
    const resetButton = document.getElementById("pronunciation-reset-filters");

    const activeTypePill = document.getElementById("active-type-pill");
    const activeAudioPill = document.getElementById("active-audio-pill");
    const activeLanguagePill = document.getElementById("active-language-pill");
    const activePosPill = document.getElementById("active-pos-pill");
    const activeTopicPill = document.getElementById("active-topic-pill");

    function getLabel(button, fallback = "All") {
        return button ? button.textContent.trim() : fallback;
    }

    function setActive(buttons, dataKey, value) {
        buttons.forEach((btn) => {
            btn.classList.toggle("active", (btn.dataset[dataKey] || "") === value);
        });
    }

    function getActiveButton(buttons, dataKey, value) {
        return buttons.find((btn) => (btn.dataset[dataKey] || "") === value);
    }

    function normalizeListField(value) {
        return (value || "")
            .split("|")
            .map((part) => part.trim().toLowerCase())
            .filter(Boolean);
    }

    function updateConditionalFilters() {
        const phrasesOnly = state.type === "phrases";

        if (vocabularyOnlyFilters) {
            vocabularyOnlyFilters.style.display = phrasesOnly ? "none" : "grid";
        }

        if (posFilterGroup) {
            posFilterGroup.style.display = phrasesOnly ? "none" : "";
        }

        if (topicFilterGroup) {
            topicFilterGroup.style.display = phrasesOnly ? "none" : "";
        }

        if (activePosPill) {
            activePosPill.style.display = phrasesOnly ? "none" : "";
        }

        if (activeTopicPill) {
            activeTopicPill.style.display = phrasesOnly ? "none" : "";
        }

        if (phrasesOnly) {
            state.pos = "all";
            state.topic = "all";
            setActive(posButtons, "pos", "all");
            setActive(topicButtons, "topic", "all");
        }
    }

    function updateActiveFilterPills() {
        const activeTypeButton = getActiveButton(typeButtons, "type", state.type);
        const activeAudioButton = getActiveButton(audioButtons, "audio", state.audio);
        const activeLanguageButton = getActiveButton(languageButtons, "language", state.language);
        const activePosButton = getActiveButton(posButtons, "pos", state.pos);
        const activeTopicButton = getActiveButton(topicButtons, "topic", state.topic);

        if (activeTypePill) {
            activeTypePill.textContent = `Type: ${getLabel(activeTypeButton)}`;
        }

        if (activeAudioPill) {
            activeAudioPill.textContent = `Audio: ${getLabel(activeAudioButton)}`;
        }

        if (activeLanguagePill) {
            activeLanguagePill.textContent = `Language: ${getLabel(activeLanguageButton)}`;
        }

        if (activePosPill) {
            activePosPill.textContent = `Part of speech: ${getLabel(activePosButton)}`;
        }

        if (activeTopicPill) {
            activeTopicPill.textContent = `Topic: ${getLabel(activeTopicButton)}`;
        }
    }

    function applyFilters() {
        let visibleCount = 0;
        const visibleByType = { vocabulary: 0, phrases: 0 };

        items.forEach((item) => {
            const itemType = (item.dataset.itemType || "").trim().toLowerCase();
            const itemAudio = (item.dataset.audioState || "").trim().toLowerCase();
            const itemLanguage = (item.dataset.language || "").trim().toLowerCase();
            const itemPos = (item.dataset.pos || "").trim().toLowerCase();
            const itemTopics = normalizeListField(item.dataset.topics || "");
            const itemSearch = (item.dataset.search || "").toLowerCase();

            const matchesType = state.type === "all" || itemType === state.type;
            const matchesAudio = state.audio === "all" || itemAudio === state.audio;
            const matchesLanguage = state.language === "all" || itemLanguage === state.language;
            const matchesPos = state.type === "phrases" || state.pos === "all" || itemPos === state.pos;
            const matchesTopic = state.type === "phrases" || state.topic === "all" || itemTopics.includes(state.topic);
            const matchesSearch = !state.search || itemSearch.includes(state.search);

            const visible = matchesType && matchesAudio && matchesLanguage && matchesPos && matchesTopic && matchesSearch;

            item.style.display = visible ? "" : "none";

            if (visible) {
                visibleCount += 1;
                if (visibleByType[itemType] !== undefined) {
                    visibleByType[itemType] += 1;
                }
            }
        });

        sectionHeaders.forEach((header) => {
            const type = (header.dataset.section || "").trim().toLowerCase();
            header.style.display = visibleByType[type] > 0 ? "" : "none";
        });

        lists.forEach((list) => {
            const type = (list.dataset.listType || "").trim().toLowerCase();
            list.style.display = visibleByType[type] > 0 ? "" : "none";
        });

        if (emptyState) {
            emptyState.style.display = visibleCount === 0 ? "" : "none";
        }

        if (resultsCount) {
            resultsCount.textContent = `${visibleCount} ${visibleCount === 1 ? "item" : "items"}`;
        }

        updateActiveFilterPills();
    }

    typeButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            state.type = this.dataset.type || "all";
            setActive(typeButtons, "type", state.type);
            updateConditionalFilters();
            applyFilters();
        });
    });

    audioButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            state.audio = this.dataset.audio || "all";
            setActive(audioButtons, "audio", state.audio);
            applyFilters();
        });
    });

    languageButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            state.language = this.dataset.language || "all";
            setActive(languageButtons, "language", state.language);
            applyFilters();
        });
    });

    posButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            state.pos = this.dataset.pos || "all";
            setActive(posButtons, "pos", state.pos);
            applyFilters();
        });
    });

    topicButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            state.topic = this.dataset.topic || "all";
            setActive(topicButtons, "topic", state.topic);
            applyFilters();
        });
    });

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            state.search = this.value.trim().toLowerCase();
            applyFilters();
        });
    }

    if (resetButton) {
        resetButton.addEventListener("click", function () {
            state.type = "all";
            state.audio = "all";
            state.language = "all";
            state.pos = "all";
            state.topic = "all";
            state.search = "";

            setActive(typeButtons, "type", "all");
            setActive(audioButtons, "audio", "all");
            setActive(languageButtons, "language", "all");
            setActive(posButtons, "pos", "all");
            setActive(topicButtons, "topic", "all");

            if (searchInput) {
                searchInput.value = "";
            }

            updateConditionalFilters();
            applyFilters();
        });
    }

    updateConditionalFilters();
    applyFilters();
});