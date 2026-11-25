(function () {
  var f = document.getElementById("lm-form");
  if (!f) return;
  var tabs = [].slice.call(f.querySelectorAll(".lm-tab")), panels = [].slice.call(f.querySelectorAll(".lm-panel")), out = f.querySelector(".lm-result");
  var cur = null;
  var TXT = {
    bajo: ["Todavía queda trabajo por delante", "Con menos de 5 ítems marcados, aparentemente queda mucho trabajo por delante, y habría que ver si no te estás estancando de forma innecesaria. ¿Crees que estás trabajando de forma adecuada en tu lesión? ¿O crees que quizás haya una o varias cosas que puedan estar fallando?"],
    medio: ["Vas por buen camino, pero falta trabajo", "Con 5 o 6 ítems marcados no vas mal encaminado, pero aún te falta trabajo por hacer. Quizás habría que revisar por qué no cumples con todo y qué se podría hacer para optimizarlo. ¿En qué sientes que estás más atascado? ¿Y por qué no terminas de estar como te gustaría?"],
    alto: ["¡Enhorabuena, vas bastante bien!", "Con 7 u 8 ítems marcados parece que vas bastante bien. Sigue así."]
  };
  function esc(t) { return t.replace(/&/g, "&amp;").replace(/</g, "&lt;"); }
  function calc() {
    var p = panels.filter(function (x) { return x.dataset.f === cur; })[0];
    if (!p) { out.innerHTML = ""; return; }
    var cs = [].slice.call(p.querySelectorAll("input")), n = cs.length, c = cs.filter(function (x) { return x.checked; }).length;
    var k = c >= 7 ? "alto" : c >= 5 ? "medio" : "bajo";
    var falta = cs.filter(function (x) { return !x.checked; }).map(function (x) { return "<li>" + esc(x.nextElementSibling.textContent.trim()) + "</li>"; });
    var h = '<div class="lm-r ' + k + '"><div class="lm-r-n"><b>' + c + '</b><span>de ' + n + '</span></div><div><h4>' + TXT[k][0] + '</h4><p>' + TXT[k][1] + "</p></div></div>";
    var sig = Number(cur) < 4 ? Number(cur) + 1 : 0;
    var ahora = '<div class="lm-ahora"><h4>Qué toca ahora</h4>';
    if (k === "alto") ahora += sig ? '<p>Ya puedes empezar a plantearte la <b>Fase ' + sig + '</b>.</p><button type="button" class="lm-btn lm-ir" data-f="' + sig + '">Ir a la Fase ' + sig + "</button>" : "<p>Estás en la recta final. Asegúrate de cerrar lo que te falte antes de volver al deporte sin límites.</p>";
    else ahora += "<p>Céntrate en esta fase: lo que te falta por marcar es tu lista de trabajo.</p>";
    if (falta.length) ahora += "<p><b>Te falta por cumplir:</b></p><ul>" + falta.join("") + "</ul>";
    out.innerHTML = h + ahora + "</div>";
    out.className = "lm-result on";
  }
  function show(id, scroll) {
    cur = id;
    tabs.forEach(function (t) { var on = t.dataset.f === id; t.classList.toggle("on", on); t.setAttribute("aria-selected", on); });
    panels.forEach(function (x) { x.classList.toggle("on", x.dataset.f === id); });
    calc();
    if (scroll) f.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  tabs.forEach(function (t) { t.addEventListener("click", function () { show(t.dataset.f); }); });
  f.addEventListener("change", calc);
  f.addEventListener("click", function (e) { var b = e.target.closest(".lm-ir"); if (b) show(b.dataset.f, true); });
  out.className = "lm-result";
  out.innerHTML = '<p class="lm-vacio">Elige tu fase para empezar.</p>';
})();
