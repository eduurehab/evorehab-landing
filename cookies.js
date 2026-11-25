// EVOREHAB landing · Aviso de cookies.
// Solo hay un servicio que pueda poner cookies: YouTube (los vídeos). Mientras la persona no las acepte, no se carga
// ningún vídeo de YouTube dentro de la página: al pulsar uno se abre en YouTube, en otra pestaña.
(function () {
  var K = 'evo-cookies';           // 'todas' | 'esenciales'
  var RAIZ = new URL('./', document.currentScript.src).pathname;
  var estado = null, oyentes = [], aviso = null;
  try { estado = localStorage.getItem(K); } catch (e) {}

  function guardar(v) {
    estado = v;
    try { localStorage.setItem(K, v); } catch (e) {}
    oyentes.forEach(function (f) { f(v); });
    if (v === 'todas') pixel();
    else if (pixelCargado && window.fbq) fbq('consent', 'revoke');
  }

  // Píxel de Meta: solo en las páginas que definan window.EVO_PIXEL (con el ID) y solo si se aceptan las cookies.
  // Cada clic a WhatsApp se cuenta como evento «Contacto», sin enviar ningún dato de la persona.
  var pixelCargado = false;
  function pixel() {
    if (!window.EVO_PIXEL || pixelCargado || estado !== 'todas') return;
    pixelCargado = true;
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', window.EVO_PIXEL);
    fbq('track', 'PageView');
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="wa.me"]');
    if (a && pixelCargado && window.fbq) fbq('track', 'Contact');
  });

  function cerrar() { if (aviso) { aviso.remove(); aviso = null; } }

  function mostrar() {
    if (aviso) return;
    aviso = document.createElement('div');
    aviso.className = 'ck';
    aviso.setAttribute('role', 'dialog');
    aviso.setAttribute('aria-label', 'Cookies');
    aviso.innerHTML =
      '<p><b>Cookies</b><br>' + (window.EVO_PIXEL
        ? 'Usamos cookies de YouTube para reproducir los vídeos y el píxel de Meta para medir nuestra publicidad. '
        : 'Usamos cookies de YouTube solo para reproducir los vídeos en esta página. ') +
      'Puedes aceptarlas o quedarte solo con las esenciales. <a href="' + RAIZ + 'cookies/">Más información</a></p>' +
      '<div class="ck-bt"><button type="button" data-ck="esenciales">Solo esenciales</button>' +
      '<button type="button" data-ck="todas">Aceptar</button></div>';
    aviso.addEventListener('click', function (e) {
      var b = e.target.closest('[data-ck]'); if (!b) return;
      guardar(b.getAttribute('data-ck')); cerrar();
    });
    document.body.appendChild(aviso);
  }

  function acepta() { return estado === 'todas'; }

  // Dirección del vídeo incrustado: siempre en modo de privacidad ampliada de YouTube.
  function embed(id, autoplay) {
    return 'https://www.youtube-nocookie.com/embed/' + id + '?rel=0' + (autoplay ? '&autoplay=1' : '');
  }

  // Vídeos que se muestran como portada con botón de play ([data-yt-embed]): si hay permiso, se carga el reproductor;
  // si no, el clic abre el vídeo en YouTube.
  function montar(portada, autoplay) {
    var id = portada.getAttribute('data-yt-embed');
    var f = document.createElement('iframe');
    f.src = embed(id, autoplay);
    f.title = portada.getAttribute('data-titulo') || 'Vídeo';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    f.allowFullscreen = true;
    portada.replaceWith(f);
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (estado !== 'todas' && estado !== 'esenciales') mostrar();
    document.querySelectorAll('[data-yt-embed]').forEach(function (p) {
      if (acepta()) return montar(p, false);
      p.addEventListener('click', function (e) {
        e.preventDefault();
        if (acepta()) montar(p, true); else window.open(p.href, '_blank', 'noopener');
      });
    });
    document.querySelectorAll('[data-cookies]').forEach(function (a) {
      a.addEventListener('click', function (e) { e.preventDefault(); mostrar(); });
    });
  });

  // Si acepta con el aviso ya delante, los vídeos con portada pasan a reproducirse en la página.
  oyentes.push(function (v) {
    if (v !== 'todas') return;
    document.querySelectorAll('[data-yt-embed]').forEach(function (p) { montar(p, false); });
  });

  pixel();   // si ya había aceptado en una visita anterior

  window.EvoCookies = { acepta: acepta, embed: embed, reabrir: mostrar };
})();
