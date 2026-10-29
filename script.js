// EVOREHAB landing page

// Reproductor de vídeo dentro de la página (modal), para que al hacer clic
// en un testimonio o historia de Instagram el vídeo se vea sin salir de la web.
document.addEventListener('DOMContentLoaded', function () {
  var modal = document.getElementById('videoModal');
  var iframe = document.getElementById('videoModalIframe');

  if (!modal || !iframe) return;

  function openModal(videoId) {
    iframe.src = 'https://www.youtube.com/embed/' + videoId + '?autoplay=1&rel=0';
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    iframe.src = '';
    document.body.style.overflow = '';
  }

  document.querySelectorAll('[data-yt-id]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      openModal(link.getAttribute('data-yt-id'));
    });
  });

  document.querySelectorAll('[data-close]').forEach(function (el) {
    el.addEventListener('click', closeModal);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
  });
});

// Carruseles de testimonios: deslizables con el dedo, el trackpad, arrastrando
// con el ratón o con las flechas ‹ ›. Las tarjetas con [hidden] no cuentan.
function initCarousel(el, opts) {
  opts = opts || {};
  var cards = [], aim = null, idle, raf;

  // Envoltorio con las flechas juntas debajo del caso central
  var box = document.createElement('div');
  box.className = 'car';
  el.parentNode.insertBefore(box, el);
  box.appendChild(el);
  var nav = document.createElement('div');
  nav.className = 'car-nav';
  box.appendChild(nav);
  function arrow(dir, label, d) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'car-arrow ' + dir;
    b.setAttribute('aria-label', label);
    b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + d + '" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    nav.appendChild(b);
    return b;
  }
  var prev = arrow('prev', 'Caso anterior', 'M15 18l-6-6 6-6');
  var next = arrow('next', 'Caso siguiente', 'M9 6l6 6-6 6');

  function refresh() {
    cards = Array.prototype.filter.call(el.querySelectorAll('.tc'), function (c) { return !c.hidden; });
  }
  function offsetFor(card) { return card.offsetLeft - (el.clientWidth - card.offsetWidth) / 2; }
  function go(i, smooth) {
    i = Math.max(0, Math.min(cards.length - 1, i));
    el.scrollTo({ left: offsetFor(cards[i]), behavior: smooth ? 'smooth' : 'auto' });
  }
  function nearest() {
    var mid = el.scrollLeft + el.clientWidth / 2, best = 0, bestD = Infinity;
    cards.forEach(function (c, i) {
      var d = Math.abs(c.offsetLeft + c.offsetWidth / 2 - mid);
      if (d < bestD) { bestD = d; best = i; }
    });
    return best;
  }
  function paint() {
    var mid = el.scrollLeft + el.clientWidth / 2;
    cards.forEach(function (c) {
      var t = Math.min(Math.abs(c.offsetLeft + c.offsetWidth / 2 - mid) / (c.offsetWidth + 24), 1);
      c.style.setProperty('--s', (1 - 0.12 * t).toFixed(3));
      c.style.setProperty('--o', (1 - 0.55 * t).toFixed(3));
    });
    var n = nearest();
    prev.disabled = n === 0;
    next.disabled = n === cards.length - 1;
    if (opts.onChange) opts.onChange(n, cards);
  }
  el.addEventListener('scroll', function () {
    cancelAnimationFrame(raf); raf = requestAnimationFrame(paint);
    clearTimeout(idle); idle = setTimeout(function () { aim = null; }, 160);
  });
  window.addEventListener('resize', paint);

  // Flechas: si se pulsan varias veces seguidas, avanzan desde el destino anterior
  function step(d) {
    aim = Math.max(0, Math.min(cards.length - 1, (aim === null ? nearest() : aim) + d));
    go(aim, true);
  }
  prev.addEventListener('click', function () { step(-1); });
  next.addEventListener('click', function () { step(1); });

  // Arrastrar con el ratón (en móvil y trackpad el desplazamiento es nativo)
  var down = false, moved = false, startX = 0, startLeft = 0;
  el.addEventListener('pointerdown', function (e) {
    if (e.pointerType !== 'mouse') return;
    down = true; moved = false; startX = e.clientX; startLeft = el.scrollLeft;
  });
  window.addEventListener('pointermove', function (e) {
    if (!down) return;
    var dx = e.clientX - startX;
    if (!moved && Math.abs(dx) > 5) { moved = true; el.classList.add('drag'); }
    if (moved) el.scrollLeft = startLeft - dx;
  });
  window.addEventListener('pointerup', function () {
    if (!down) return;
    down = false;
    if (moved) { var i = nearest(); el.classList.remove('drag'); go(i, true); }
  });
  el.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);

  refresh();
  var startAt = cards.length > 2 ? (opts.startAt || 0) : 0;
  function start() { go(startAt, false); paint(); }
  start();
  window.addEventListener('load', start);
  if (document.fonts) document.fonts.ready.then(start);

  return {
    go: go,
    cards: function () { return cards; },
    refresh: function () { refresh(); paint(); }
  };
}
