(function () {
  var box = document.getElementById("lm-arbol");
  if (!box) return;
  var Q = [
    ["¿Tengo extensión completa, activa y la tolero sin dolor residual al día siguiente?", "Ejercicios de extensión activa y pasiva"],
    ["¿Puedo flexionar del todo la rodilla en descarga y en carga ligera sin dolor ni compensaciones?", "Ejercicios de flexión con peso corporal asistida y rangos parciales"],
    ["¿Puedo aceptar y producir fuerza con una sola pierna sin perder control?", "Fuerza unilateral básica y ejercicios monopodales"],
    ["¿Puedo desacelerar y frenar mi cuerpo a baja velocidad sin dolor ni inseguridad?", "Trabajo excéntrico, deceleraciones controladas y patrones de aterrizaje"],
    ["¿Tolero impactos repetidos sin dolor durante ni después?", "Pliometría de bajo impacto a 2 piernas y a 1, y aumento progresivo del volumen"]
  ];
  var el = document.getElementById("lm-arbol-q"), n = document.getElementById("lm-arbol-n"), b = document.getElementById("lm-arbol-b");
  var i = 0, resp = [];
  var UP = '<svg viewBox="0 0 24 24"><path d="M7 11v9H4v-9zM7 11l4-8a2 2 0 0 1 2 2v4h6a2 2 0 0 1 2 2l-1 7a2 2 0 0 1-2 2H7"/></svg>';
  var DOWN = '<svg viewBox="0 0 24 24"><path d="M17 13V4h3v9zM17 13l-4 8a2 2 0 0 1-2-2v-4H5a2 2 0 0 1-2-2l1-7a2 2 0 0 1 2-2h11"/></svg>';
  function pasos() {
    return '<ol class="lm-arbol-ruta">' + Q.map(function (q, k) {
      var c = k < resp.length ? (resp[k] ? "ok" : "no") : k === i ? "act" : "";
      return '<li class="' + c + '"><span>' + (k + 1) + "</span></li>";
    }).join("") + "</ol>";
  }
  function pinta() {
    b.style.width = (Math.min(i, 5) * 100 / 5) + "%";
    if (i < 5 && !(resp.length && resp[resp.length - 1] === false)) {
      n.textContent = "Pregunta " + (i + 1) + " de 5";
      el.innerHTML = pasos() + '<div class="lm-arbol-card"><h3>' + Q[i][0] + '</h3><div class="lm-arbol-ops"><button type="button" class="si" data-v="1">' + UP + ' Sí</button><button type="button" class="no" data-v="0">' + DOWN + ' No</button></div>' + (i ? '<button type="button" class="lm-arbol-back">← Volver a la anterior</button>' : "") + "</div>";
    } else if (i < 5) {
      n.textContent = "Tu resultado";
      el.innerHTML = pasos() + '<div class="lm-arbol-res no"><span class="tag">Tu prioridad ahora</span><h3>' + Q[i][1] + '</h3><p>Es lo que toca trabajar antes de pasar al siguiente paso. Cuando lo tengas claro y sin molestias, vuelve y responde otra vez.</p><button type="button" class="lm-btn lm-arbol-reset">Volver a empezar</button></div>';
    } else {
      n.textContent = "Tu resultado";
      b.style.width = "100%";
      el.innerHTML = pasos() + '<div class="lm-arbol-res ok"><span class="tag">¡Enhorabuena!</span><h3>Puedes empezar una progresión de carrera</h3><p>Has respondido que sí a las 5 preguntas.</p><button type="button" class="lm-btn lm-arbol-reset">Volver a empezar</button></div>';
    }
  }
  box.addEventListener("click", function (e) {
    var t = e.target.closest("button");
    if (!t) return;
    if (t.dataset.v !== undefined) { resp.push(t.dataset.v === "1"); if (t.dataset.v === "1") i++; pinta(); }
    else if (t.classList.contains("lm-arbol-back")) { i--; resp.pop(); pinta(); }
    else if (t.classList.contains("lm-arbol-reset")) { i = 0; resp = []; pinta(); box.scrollIntoView({ behavior: "smooth", block: "start" }); }
  });
  pinta();
})();
