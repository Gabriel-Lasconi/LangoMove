document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("history-modal");
    const modalBody = document.getElementById("history-modal-body");
    const closeButton = document.getElementById("history-modal-close");
    const historyItems = document.querySelectorAll("[data-history-item]");

    if (!modal || !modalBody || !closeButton || !historyItems.length) {
        return;
    }

    function openModal(contentHtml) {
        modalBody.innerHTML = contentHtml;
        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("modal-open");
    }

    function closeModal() {
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("modal-open");
    }

    historyItems.forEach((item) => {
        function handleOpen() {
            const template = item.querySelector(".profile-history-modal-template");
            if (!template) return;
            openModal(template.innerHTML);
        }

        item.addEventListener("click", handleOpen);

        item.addEventListener("keydown", function (event) {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                handleOpen();
            }
        });
    });

    closeButton.addEventListener("click", closeModal);

    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && modal.classList.contains("open")) {
            closeModal();
        }
    });
});