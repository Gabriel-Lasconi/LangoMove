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
    const sectionHeaders = Array.from(document.querySelectorAll(".pronunciation-section-header"));
    const lists = Array.from(document.querySelectorAll(".pronunciation-items-list"));
    const emptyState = document.getElementById("pronunciation-empty-state");
    const searchInput = document.getElementById("pronunciation-search");
    const resetButton = document.getElementById("pronunciation-reset-filters");
    const resultsCount = document.getElementById("pronunciation-results-count");

    const activeTypePill = document.getElementById("active-type-pill");
    const activeAudioPill = document.getElementById("active-audio-pill");
    const activeLanguagePill = document.getElementById("active-language-pill");
    const activePosPill = document.getElementById("active-pos-pill");
    const activeTopicPill = document.getElementById("active-topic-pill");

    const typeButtons = Array.from(document.querySelectorAll("#type-filters .chip"));
    const audioButtons = Array.from(document.querySelectorAll("#audio-filters .chip"));
    const languageButtons = Array.from(document.querySelectorAll("#language-filters .chip"));
    const posButtons = Array.from(document.querySelectorAll("#pos-filters .chip"));
    const topicButtons = Array.from(document.querySelectorAll("#topic-filters .chip"));

    function prettifyLabel(value) {
        if (!value || value === "all") return "All";
        return value.replace(/\b\w/g, (char) => char.toUpperCase());
    }

    function setActiveButton(buttons, attrName, selectedValue) {
        buttons.forEach((button) => {
            const value = button.dataset[attrName] || "";
            button.classList.toggle("active", value === selectedValue);
        });
    }

    function updateSummaryPills() {
        if (activeTypePill) {
            activeTypePill.textContent = `Type: ${prettifyLabel(state.type)}`;
        }
        if (activeAudioPill) {
            activeAudioPill.textContent = `Audio: ${prettifyLabel(state.audio)}`;
        }
        if (activeLanguagePill) {
            activeLanguagePill.textContent = `Language: ${prettifyLabel(state.language)}`;
        }
        if (activePosPill) {
            activePosPill.textContent = `Part of speech: ${prettifyLabel(state.pos)}`;
        }
        if (activeTopicPill) {
            activeTopicPill.textContent = `Topic: ${prettifyLabel(state.topic)}`;
        }
    }

    function matchesTopic(itemTopics, selectedTopic) {
        if (selectedTopic === "all") return true;
        if (!itemTopics) return false;

        const normalizedTopics = itemTopics
            .split("|")
            .map((topic) => topic.trim().toLowerCase())
            .filter(Boolean);

        return normalizedTopics.includes(selectedTopic);
    }

    function applyFilters() {
        let visibleCount = 0;
        const visibleByType = {
            vocabulary: 0,
            phrases: 0
        };

        items.forEach((item) => {
            const itemType = (item.dataset.itemType || "").toLowerCase();
            const itemAudio = (item.dataset.audioState || "").toLowerCase();
            const itemLanguage = (item.dataset.language || "").toLowerCase();
            const itemPos = (item.dataset.pos || "").toLowerCase();
            const itemTopics = (item.dataset.topics || "").toLowerCase();
            const itemSearch = (item.dataset.search || "").toLowerCase();

            const matchesType =
                state.type === "all" || itemType === state.type;

            const matchesAudio =
                state.audio === "all" || itemAudio === state.audio;

            const matchesLanguage =
                state.language === "all" || itemLanguage === state.language;

            const matchesPos =
                state.pos === "all" || itemPos === state.pos;

            const matchesTopicFilter =
                matchesTopic(itemTopics, state.topic);

            const matchesSearch =
                !state.search || itemSearch.includes(state.search);

            const shouldShow =
                matchesType &&
                matchesAudio &&
                matchesLanguage &&
                matchesPos &&
                matchesTopicFilter &&
                matchesSearch;

            item.style.display = shouldShow ? "" : "none";

            if (shouldShow) {
                visibleCount += 1;
                if (visibleByType[itemType] !== undefined) {
                    visibleByType[itemType] += 1;
                }
            }
        });

        sectionHeaders.forEach((header) => {
            const sectionType = header.dataset.section;
            header.style.display = visibleByType[sectionType] > 0 ? "" : "none";
        });

        lists.forEach((list) => {
            const listType = list.dataset.listType;
            list.style.display = visibleByType[listType] > 0 ? "" : "none";
        });

        if (emptyState) {
            emptyState.style.display = visibleCount === 0 ? "" : "none";
        }

        if (resultsCount) {
            resultsCount.textContent = `${visibleCount} item${visibleCount === 1 ? "" : "s"}`;
        }

        updateSummaryPills();
    }

    typeButtons.forEach((button) => {
        button.addEventListener("click", function () {
            state.type = this.dataset.type || "all";
            setActiveButton(typeButtons, "type", state.type);
            applyFilters();
        });
    });

    audioButtons.forEach((button) => {
        button.addEventListener("click", function () {
            state.audio = this.dataset.audio || "all";
            setActiveButton(audioButtons, "audio", state.audio);
            applyFilters();
        });
    });

    languageButtons.forEach((button) => {
        button.addEventListener("click", function () {
            state.language = this.dataset.language || "all";
            setActiveButton(languageButtons, "language", state.language);
            applyFilters();
        });
    });

    posButtons.forEach((button) => {
        button.addEventListener("click", function () {
            state.pos = this.dataset.pos || "all";
            setActiveButton(posButtons, "pos", state.pos);
            applyFilters();
        });
    });

    topicButtons.forEach((button) => {
        button.addEventListener("click", function () {
            state.topic = this.dataset.topic || "all";
            setActiveButton(topicButtons, "topic", state.topic);
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

            if (searchInput) {
                searchInput.value = "";
            }

            setActiveButton(typeButtons, "type", "all");
            setActiveButton(audioButtons, "audio", "all");
            setActiveButton(languageButtons, "language", "all");
            setActiveButton(posButtons, "pos", "all");
            setActiveButton(topicButtons, "topic", "all");

            applyFilters();
        });
    }

    applyFilters();
});