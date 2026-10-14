#!/usr/bin/env python3
"""Transform: Pulso -> Mittel (identidad grafica), volar demo HTML, incrustar video.
Uso: python3 tools/transform_mittel.py  (corre desde la raiz del repo)
"""
import re, sys, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "index.html"
src = P.read_text(encoding="utf-8")
orig_len = len(src)
n = 0

def rep(old, new, count=1):
    global src, n
    found = src.count(old)
    assert found >= 1, f"NO ENCONTRADO: {old[:80]!r}"
    if count != -1:
        assert found == count, f"ESPERABA {count}, HALLE {found}: {old[:80]!r}"
    src = src.replace(old, new)
    n += 1

def rep_re(pattern, new):
    global src, n
    src2, c = re.subn(pattern, new, src, count=1, flags=re.S)
    assert c == 1, f"REGEX SIN MATCH: {pattern[:80]!r}"
    src = src2
    n += 1

# ---------- 1. Marca Pulso -> Mittel ----------
rep("<title>Pulso · Mensajería masiva y atención personalizada</title>",
    "<title>Mittel · Mensajería masiva y atención personalizada</title>")
rep("Identidad Pulso", "Identidad Mittel")

# Nav: montanita SVG + "Pulso" -> mark Mittel + "Mittel"
old_mark = '''      <span class="mark">
        <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true"><circle cx="13" cy="13" r="12" fill="none" stroke="#1C2129" stroke-width="1.4"/><path d="M5.5 16.5 L9 9.5 L12.2 14 L15 8 L20.5 16.5" fill="none" stroke="#1C2129" stroke-width="1.4" stroke-linejoin="round"/></svg>
        Pulso
      </span>'''
new_mark = '''      <span class="mark">
        <img src="assets/mittel-mark.png" width="26" height="26" alt="" aria-hidden="true">
        Mittel
      </span>'''
rep(old_mark, new_mark)

# Comparador: "Con Pulso" -> "Con Mittel" (boton + texto nojs + hook JS)
rep('data-mode="pulso">Con Pulso</button>', 'data-mode="mittel">Con Mittel</button>')
rep("Con Pulso: <b>100 de 100</b>", "Con Mittel: <b>100 de 100</b>")
rep("var all = mode === 'pulso';", "var all = mode === 'mittel';")

# Footer
rep("<span>Pulso · Mensajería masiva y atención personalizada</span>",
    "<span>Mittel · Mensajería masiva y atención personalizada</span>")

# ---------- 2. Fuentes Mittel: Syne (display) + Instrument Sans (body) ----------
rep("family=Geist:wght@300;400;500;600&family=Instrument+Serif&display=swap",
    "family=Syne:wght@600;700;800&family=Instrument+Sans:wght@400;500;600&display=swap")
rep('--serif:"Instrument Serif","Times New Roman",serif;',
    '--serif:"Syne",sans-serif;')
rep('--sans:"Geist","Helvetica Neue",system-ui,sans-serif;',
    '--sans:"Instrument Sans",system-ui,sans-serif;')

# ---------- 3. Volar boton flotante #waFab ----------
old_fab = '''<button type="button" class="wa-fab" id="waFab" aria-label="Probar la demo: abrir la conversación de ejemplo" aria-haspopup="dialog" aria-controls="waOv">
  <span class="wa-fab__ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M6.5 4h11A2.5 2.5 0 0 1 20 6.5v7a2.5 2.5 0 0 1-2.5 2.5H11l-4.5 3.8V16h0A2.5 2.5 0 0 1 4 13.5v-7A2.5 2.5 0 0 1 6.5 4z"/><path d="M8.5 9.2h7M8.5 12h4.5"/></svg></span>
  <span class="wa-fab__tx">Probar demo</span>
</button>
'''
rep(old_fab, "")

# ---------- 4. Volar overlay #waOv ----------
old_ov = '''<div class="wa-ov" id="waOv" role="dialog" aria-modal="true" aria-labelledby="waOvT" hidden>
  <div class="wa-ov__panel" id="waPanel">
    <div class="wa-ov__h">
      <span class="av s">TN</span>
      <div class="wa-ov__id"><b id="waOvT">Tu Negocio</b><small>Mensaje de texto</small></div>
      <button type="button" class="wa-ov__x" id="waX" aria-label="Cerrar la conversación"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button>
    </div>
    <div class="wa-ov__body" id="waBody"></div>
    <div class="ph-in" aria-hidden="true"><span>Mensaje de texto</span><i><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg></i></div>
  </div>
</div>

'''
rep(old_ov, "")

# ---------- 5. JS: bloque boton flotante -> stubs (fabCheck/fabSync los usan refresh/onMQ/scroll) ----------
rep_re(r"  /\* ---------- Boton flotante de la demo ---------- \*/.*?(?=  /\* ---------- Chat inmersivo ---------- \*/)",
"""  /* Demo flotante eliminada: stubs para no romper refresh/onMQ/scroll */
  function fabCheck(){}
  function fabSync(){}
""")
# ---------- 6. JS: volar bloque chat inmersivo (era el ultimo; conservar refresh) ----------
rep_re(r"  /\* ---------- Chat inmersivo ---------- \*/.*?  refresh\(\); fabCheck\(\);\n\}\)\(\);",
"""  refresh();
})();""")

# ---------- 7. Demo HTML -> video incrustado ----------
rep_re(r"    <!-- demo:inicio · lo genera tools/gen_demo\.py, no editar a mano -->.*?    <!-- demo:fin -->",
'''    <div class="video-demo">
      <video controls playsinline preload="metadata" src="assets/demo.mp4" aria-label="Video: así se ve una campaña de mensajería masiva"></video>
      <p class="small muted">Dale play: así se ve una campaña, de principio a fin.</p>
    </div>''')

# ---------- 8. Copy del header de la seccion demo ----------
rep("La demo · una campaña de principio a fin</span>",
    "Míralo en acción</span>")
rep("<h2>Así se ve una campaña.</h2>",
    "<h2>Así se ve una campaña.</h2>")
rep("Un mismo mensaje sale a tus 100 clientes. Arriba, el teléfono de una clienta que responde; abajo, lo que ves tú al mismo tiempo. Lo automático lo decides tú, y cualquier conversación la puede tomar una persona cuando quiera.",
    "Un mismo mensaje sale a tus 100 clientes. Dale play: responden al mismo tiempo y la IA atiende cada conversación en vivo, de forma personalizada.")

# ---------- 9. CSS demo (keyframes) -> estilos del video ----------
rep_re(r"/\* demo:inicio \*/.*?/\* demo:fin \*/",
'''/* video demo incrustado */
.video-demo{max-width:960px;margin:26px auto 0}
.video-demo video{width:100%;height:auto;display:block;border-radius:18px;box-shadow:0 24px 70px -28px rgba(20,26,36,.35);background:#0e1116}
.video-demo .small{margin:10px 2px 0}''')

# ---------- 10. JS demo IIFE -> fuera (el video no necesita animacion) ----------
rep_re(r"  /\* Demo de una campaña\. La animación es solo CSS.*?if \(demo\) window\.addEventListener\('beforeprint', demo\.print\);\n", "")

P.write_text(src, encoding="utf-8")
print(f"OK: {n} reemplazos, {orig_len} -> {len(src)} bytes")
