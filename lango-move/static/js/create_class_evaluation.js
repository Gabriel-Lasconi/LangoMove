document.addEventListener("DOMContentLoaded", function () {
    const classroomSelect = document.getElementById("id_classroom");
    const courseField = document.getElementById("id_course");

    if (courseField) {
        courseField.setAttribute("disabled", "disabled");
    }

    if (!classroomSelect) return;

    classroomSelect.addEventListener("change", function () {
        const classroomId = this.value;
        const url = new URL(window.location.href);

        if (classroomId) {
            url.searchParams.set("classroom", classroomId);
        } else {
            url.searchParams.delete("classroom");
        }

        window.location.href = url.toString();
    });
});