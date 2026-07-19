(() => {
  "use strict";

  const nav = document.querySelector(".site-header nav");
  const active = nav?.querySelector(".nav-link.active");
  if (!nav || !active) return;

  const safetyGutter = 2;

  function revealActiveLink() {
    nav.style.paddingInlineEnd = "";
    if (nav.scrollWidth <= nav.clientWidth) {
      nav.scrollLeft = 0;
      return;
    }
    if (active.offsetWidth === 0) return;

    nav.style.paddingInlineEnd = `${safetyGutter}px`;

    const navRect = nav.getBoundingClientRect();
    const activeRect = active.getBoundingClientRect();
    if (
      activeRect.left >= navRect.left + safetyGutter &&
      activeRect.right <= navRect.right - safetyGutter
    ) return;

    const centered = nav.scrollLeft + (
      activeRect.left + activeRect.right - navRect.left - navRect.right
    ) / 2;
    const maximum = nav.scrollWidth - nav.clientWidth;
    nav.scrollLeft = Math.max(0, Math.min(maximum, centered));
  }

  revealActiveLink();
  document.fonts?.ready.then(revealActiveLink);
  window.addEventListener("resize", revealActiveLink, { passive: true });
})();
