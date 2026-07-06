/* Marque la page comme "JS actif" pour activer les animations en
   amélioration progressive (voir .js .reveal dans style.css) */
document.documentElement.classList.add("js");

/* Écran d'ouverture : affiché uniquement lors de la toute première
   arrivée sur le site pendant la session du visiteur */
(function () {
  var preloader = document.getElementById("preloader");
  if (!preloader) return;

  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var dejaVu = false;
  try {
    dejaVu = window.sessionStorage.getItem("ufrStaSplashVu") === "1";
  } catch (e) {
    dejaVu = false;
  }

  if (dejaVu || reduceMotion) {
    preloader.parentNode.removeChild(preloader);
    return;
  }

  document.documentElement.classList.add("no-scroll");
  preloader.classList.add("is-active");

  function masquerPreloader() {
    preloader.classList.add("is-hiding");
    document.documentElement.classList.remove("no-scroll");
    try {
      window.sessionStorage.setItem("ufrStaSplashVu", "1");
    } catch (e) {
      /* stockage indisponible : tant pis, on masque quand meme */
    }
    window.setTimeout(function () {
      if (preloader.parentNode) {
        preloader.parentNode.removeChild(preloader);
      }
    }, 700);
  }

  window.addEventListener("load", function () {
    window.setTimeout(masquerPreloader, 900);
  });

  /* Filet de sécurité : si "load" tarde, on masque quand même */
  window.setTimeout(masquerPreloader, 3500);
})();

document.addEventListener("DOMContentLoaded", function () {
  /* Ombre sur l'en-tête au défilement */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScrollHeader = function () {
      if (window.scrollY > 12) {
        header.classList.add("is-scrolled");
      } else {
        header.classList.remove("is-scrolled");
      }
    };
    onScrollHeader();
    window.addEventListener("scroll", onScrollHeader, { passive: true });
  }

  /* Animation d'ouverture des blocs au défilement */
  var revealSelectors = [
    ".card",
    ".section-header",
    ".directeur-bloc",
    ".semestre-card",
    ".stat-card",
    ".empty-state",
    ".article-img",
    ".login-card",
  ];
  var revealEls = document.querySelectorAll(revealSelectors.join(","));

  if (revealEls.length) {
    if ("IntersectionObserver" in window) {
      revealEls.forEach(function (el) {
        el.classList.add("reveal");
      });
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.15, rootMargin: "0px 0px -10% 0px" }
      );
      revealEls.forEach(function (el) {
        observer.observe(el);
      });
    } else {
      revealEls.forEach(function (el) {
        el.classList.add("reveal", "is-visible");
      });
    }
  }

  /* Menu de navigation mobile */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".main-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
  }

  /* Lightbox simple pour les grilles de photos */
  var grids = document.querySelectorAll(".photo-grid");
  var overlay = document.querySelector(".lightbox-overlay");
  var overlayImg = overlay ? overlay.querySelector("img") : null;
  var closeBtn = overlay ? overlay.querySelector(".lightbox-close") : null;

  function openLightbox(src, alt) {
    if (!overlay || !overlayImg) return;
    overlayImg.src = src;
    overlayImg.alt = alt || "";
    overlay.classList.add("is-open");
  }

  function closeLightbox() {
    if (!overlay) return;
    overlay.classList.remove("is-open");
  }

  grids.forEach(function (grid) {
    grid.addEventListener("click", function (event) {
      var img = event.target.closest("img");
      if (img) {
        openLightbox(img.getAttribute("src"), img.getAttribute("alt"));
      }
    });
  });

  if (closeBtn) closeBtn.addEventListener("click", closeLightbox);
  if (overlay) {
    overlay.addEventListener("click", function (event) {
      if (event.target === overlay) closeLightbox();
    });
  }
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeLightbox();
  });

  /* Confirmation avant suppression (admin) */
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var message =
        form.getAttribute("data-confirm") || "Confirmer la suppression ?";
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });
});
