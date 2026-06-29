document.documentElement.classList.add("js-enabled");

const THEME_STORAGE_KEY = "documind-theme";
const LIGHT_THEME = "django-classic";
const DARK_THEME = "ai-workspace";

const getStoredTheme = () => {
    try {
        return localStorage.getItem(THEME_STORAGE_KEY);
    } catch (error) {
        return null;
    }
};

const setStoredTheme = (theme) => {
    try {
        localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch (error) {
        return;
    }
};

const applyTheme = (theme) => {
    const selectedTheme = theme === DARK_THEME ? DARK_THEME : LIGHT_THEME;
    document.documentElement.dataset.theme = selectedTheme;
    document.documentElement.classList.toggle("dark", selectedTheme === DARK_THEME);

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
        const isDark = selectedTheme === DARK_THEME;
        const label = button.querySelector("[data-theme-label]");

        button.setAttribute("aria-pressed", String(isDark));
        button.setAttribute(
            "aria-label",
            isDark ? "Switch to Django Classic theme" : "Switch to AI Workspace theme",
        );

        if (label) {
            label.textContent = isDark ? "AI Workspace" : "Django Classic";
        }
    });
};

applyTheme(getStoredTheme());

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

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const nextTheme = document.documentElement.dataset.theme === DARK_THEME ? LIGHT_THEME : DARK_THEME;
            applyTheme(nextTheme);
            setStoredTheme(nextTheme);
        });
    });

    applyTheme(getStoredTheme());

    if (window.lucide) {
        window.lucide.createIcons({
            attrs: {
                "stroke-width": 2,
            },
        });
    }
});
