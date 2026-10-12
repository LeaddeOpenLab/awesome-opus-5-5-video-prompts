const t = (text) => window.siteI18n?.t(text) || text;
const search = document.querySelector("input[data-search]");
const cards = [...document.querySelectorAll("[data-card]")];
const filters = [...document.querySelectorAll("[data-filter]")];
let category = "all";
function filterCards() {
  const query = search?.value.trim().toLowerCase() || "";
  let visible = 0;
  for (const card of cards) {
    const show =
      (category === "all" || card.dataset.category === category) &&
      (card.dataset.search + " " + card.textContent.toLowerCase()).includes(
        query,
      );
    card.hidden = !show;
    if (show) visible++;
  }
  const count = document.querySelector("[data-count]");
  if (count)
    count.textContent = t(
      `${visible} ${visible === 1 ? "example" : "examples"}`,
    );
  const empty = document.querySelector("[data-empty]");
  if (empty) empty.hidden = visible !== 0;
}
search?.addEventListener("input", filterCards);
document.addEventListener("languagechange", filterCards);
filters.forEach((button) =>
  button.addEventListener("click", () => {
    category = button.dataset.filter;
    filters.forEach((item) =>
      item.setAttribute("aria-pressed", String(item === button)),
    );
    filterCards();
  }),
);
document.querySelectorAll("[data-copy]").forEach((button) =>
  button.addEventListener("click", async () => {
    const code = document.getElementById(button.dataset.copy);
    try {
      await navigator.clipboard.writeText(code.textContent);
      button.textContent = t("Copied ✓");
      setTimeout(() => {
        button.textContent = t("Copy prompt");
      }, 2000);
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(code);
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = t("Text selected — copy manually");
    }
  }),
);
const dialog = document.querySelector("[data-preview-dialog]");
if (dialog) {
  const video = dialog.querySelector("video");
  document.querySelectorAll("[data-preview]").forEach((button) =>
    button.addEventListener("click", () => {
      dialog.querySelector("h2").textContent = t(button.dataset.title);
      dialog.querySelector("[data-preview-link]").href = button.dataset.link;
      video.poster = button.dataset.poster;
      video.src = button.dataset.preview;
      dialog.showModal();
      video.play().catch(() => {});
    }),
  );
  dialog
    .querySelector("[data-close]")
    .addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      const r = dialog.getBoundingClientRect();
      if (
        event.clientX < r.left ||
        event.clientX > r.right ||
        event.clientY < r.top ||
        event.clientY > r.bottom
      )
        dialog.close();
    }
  });
  dialog.addEventListener("close", () => {
    video.pause();
    video.removeAttribute("src");
    video.load();
  });
}
