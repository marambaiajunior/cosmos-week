(function(){
  'use strict';
  function track(name, params){
    try {
      if (typeof window.gtag === 'function') window.gtag('event', name, params || {});
    } catch (_) {}
  }
  document.addEventListener('click', function(e){
    var el = e.target.closest('[data-book-cta]');
    if (!el) return;
    track('book_cta_click', {
      book_title: 'Vórtice Maligno',
      cta_location: el.getAttribute('data-book-cta') || 'unknown',
      link_url: el.href || ''
    });
    if (el.matches('[data-clube-autores]')) {
      track('book_clube_autores_click', {
        book_title: 'Vórtice Maligno',
        cta_location: el.getAttribute('data-book-cta') || 'unknown',
        link_url: el.href || ''
      });
    }
  });
  var toggle=document.getElementById('mobileNavToggle');
  var nav=document.getElementById('mainNav');
  if(toggle && nav){
    toggle.addEventListener('click',function(){
      var open=toggle.getAttribute('aria-expanded')==='true';
      toggle.setAttribute('aria-expanded',String(!open));
      nav.classList.toggle('open',!open);
    });
  }
})();
