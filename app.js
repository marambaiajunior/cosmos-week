// app.js — inicialização segura após defer

(function () {
  function init() {
    if (!window.postsData) {
      console.warn("postsData ainda não disponível.");
      return;
    }

    // chama sua função existente de renderização
    if (typeof renderPosts === "function") {
      renderPosts(window.postsData);
    } else {
      console.warn("renderPosts não definido.");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();