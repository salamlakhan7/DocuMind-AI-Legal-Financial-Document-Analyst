document.documentElement.classList.add("js-enabled");

document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("dashboard-sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");
    const openButtons = document.querySelectorAll("[data-sidebar-open]");
    const closeButtons = document.querySelectorAll("[data-sidebar-close]");
    const navLinks = document.querySelectorAll("[data-nav-link]");

    const openSidebar = () => {
        if (!sidebar || !backdrop) {
            return;
        }

        sidebar.classList.remove("-translate-x-full");
        backdrop.classList.remove("hidden");
    };

    const closeSidebar = () => {
        if (!sidebar || !backdrop) {
            return;
        }

        sidebar.classList.add("-translate-x-full");
        backdrop.classList.add("hidden");
    };

    openButtons.forEach((button) => button.addEventListener("click", openSidebar));
    closeButtons.forEach((button) => button.addEventListener("click", closeSidebar));
    backdrop?.addEventListener("click", closeSidebar);

    navLinks.forEach((link) => {
        if (link.href === window.location.href) {
            link.classList.add("is-active");
            link.setAttribute("aria-current", "page");
        }

        link.addEventListener("click", closeSidebar);
    });

    document.querySelectorAll("form").forEach((form) => {
        form.addEventListener("submit", () => {
            const submitButton = form.querySelector("button[type='submit']");
            if (!submitButton || submitButton.dataset.loading === "true") {
                return;
            }

            submitButton.dataset.loading = "true";
            submitButton.dataset.originalText = submitButton.textContent.trim();
            submitButton.textContent = submitButton.dataset.loadingText || "Working...";
            submitButton.disabled = true;
            submitButton.classList.add("cursor-wait", "opacity-80");
        });
    });
});
