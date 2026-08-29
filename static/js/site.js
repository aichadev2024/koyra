/* Koyra Distribution — interactions du site public
   Progressif : sans JS, la page reste entièrement fonctionnelle. */
(function () {
    "use strict";

    /* ---- Menu mobile --------------------------------------------------- */
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("site-nav");

    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            var open = nav.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", open ? "true" : "false");
        });

        // Referme le menu quand on clique un lien ou qu'on repasse en desktop
        nav.addEventListener("click", function (e) {
            if (e.target.tagName === "A") {
                nav.classList.remove("is-open");
                toggle.setAttribute("aria-expanded", "false");
            }
        });

        window.addEventListener("resize", function () {
            if (window.innerWidth > 860 && nav.classList.contains("is-open")) {
                nav.classList.remove("is-open");
                toggle.setAttribute("aria-expanded", "false");
            }
        });
    }

    /* ---- En-tête compacté au défilement ------------------------------ */
    var header = document.querySelector(".main-header");
    if (header) {
        var onScroll = function () {
            header.classList.toggle("is-scrolled", window.scrollY > 24);
        };
        onScroll();
        window.addEventListener("scroll", onScroll, { passive: true });
    }

    /* ---- Révélations au défilement ----------------------------------- */
    var prefersReduced = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    if (!prefersReduced && "IntersectionObserver" in window) {
        document.documentElement.classList.add("js-reveal");

        var targets = document.querySelectorAll(
            ".section-header, .grid-layout > .card"
        );

        var reveal = function (el) {
            el.classList.add("is-visible");
        };

        var io = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        reveal(entry.target);
                        io.unobserve(entry.target);
                    }
                });
            },
            { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
        );

        targets.forEach(function (el, i) {
            el.classList.add("reveal-ready");
            // léger décalage en cascade pour les grilles
            el.style.transitionDelay = (i % 4) * 60 + "ms";
            io.observe(el);
        });

        // Filet de sécurité : quoi qu'il arrive, tout est révélé au bout d'1,6 s
        // (au cas où l'observer ne se déclencherait pas dans un contexte donné).
        setTimeout(function () {
            targets.forEach(reveal);
        }, 1600);
    }
})();
