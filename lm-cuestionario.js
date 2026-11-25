(function () {
  var f = document.getElementById("lm-cuest");
  if (!f) return;
  var qs = [].slice.call(f.querySelectorAll(".lm-q")), res = document.getElementById("lm-cuest-res"), tail = document.getElementById("lm-tail");
  var TXT = {
    alto: ["¡Enhorabuena, tu plan tiene sentido!", "Tu plan de readaptación tiene sentido y estás haciendo lo más óptimo. ¡Sigue así!"],
    medio: ["No vas mal encaminado, pero se puede mejorar", "Parece que el plan no es el mejor posible y se podría optimizar en varios aspectos clave."],
    bajo: ["Es muy probable que sigas estancado", "Siguiendo este enfoque, es muy probable que sigas estancado durante meses (o años)."]
  };
  function calc() {
    var si = 0, resp = 0, no = [];
    qs.forEach(function (q) {
      var c = q.querySelector("input:checked");
      if (c) { resp++; if (c.value === "1") si++; else no.push(q.querySelector(".t").textContent); }
    });
    document.getElementById("lm-cuest-n").textContent = resp + " de " + qs.length + " respondidas";
    document.getElementById("lm-cuest-b").style.width = (resp * 100 / qs.length) + "%";
    if (resp < qs.length) { res.innerHTML = '<p class="lm-vacio">Responde las ' + qs.length + " preguntas para ver tu resultado.</p>"; tail.hidden = true; return; }
    var k = si >= 17 ? "alto" : si >= 12 ? "medio" : "bajo";
    var h = '<div class="lm-r ' + k + '"><div class="lm-r-n"><b>' + si + '</b><span>de ' + qs.length + '</span></div><div><h4>' + TXT[k][0] + "</h4><p>" + TXT[k][1] + "</p></div></div>";
    if (no.length) h += '<div class="lm-ahora"><h4>Lo que te está faltando</h4><ul>' + no.map(function (t) { return "<li>" + t.replace(/&/g, "&amp;").replace(/</g, "&lt;") + "</li>"; }).join("") + "</ul></div>";
    res.innerHTML = h;
    tail.hidden = k === "alto";
  }
  f.addEventListener("change", calc);
})();
