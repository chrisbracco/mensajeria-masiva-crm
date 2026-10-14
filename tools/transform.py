#!/usr/bin/env python3
"""Fase 2 de ARQUITECTURA-CONTENIDO.md: reescribe index.html con reemplazos exactos de texto.

Uso: python3 tools/gen_demo.py && python3 tools/transform.py [index.html]

Cada reemplazo exige encontrar el texto original exactamente las veces esperadas; si no,
el script se detiene sin escribir nada. Al final corre la verificación de la sección 6.
"""
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'index.html')
TOOLS = os.path.join(ROOT, 'tools')

doc = open(SRC, encoding='utf-8').read()
orig = doc
n_rep = 0


def R(old, new, n=1):
    """Reemplazo exacto: old tiene que aparecer exactamente n veces."""
    global doc, n_rep
    c = doc.count(old)
    if c != n:
        raise SystemExit('ERROR: se esperaban %d apariciones y hay %d de:\n%s' % (n, c, old[:300]))
    doc = doc.replace(old, new)
    n_rep += 1


def RE(pat, new, n=1, flags=re.S):
    """Reemplazo por expresión regular anclada (para bloques largos o líneas generadas)."""
    global doc, n_rep
    found = re.findall(pat, doc, flags)
    if len(found) != n:
        raise SystemExit('ERROR: regex con %d coincidencias (se esperaban %d): %s' % (len(found), n, pat[:200]))
    doc = re.sub(pat, lambda m: new, doc, flags=flags)
    n_rep += 1


def LINE(key, new):
    """Reemplaza la línea completa que contiene key (única)."""
    global doc, n_rep
    lines = doc.split('\n')
    idx = [i for i, l in enumerate(lines) if key in l]
    if len(idx) != 1:
        raise SystemExit('ERROR: %d líneas contienen %r' % (len(idx), key))
    lines[idx[0]] = new
    doc = '\n'.join(lines)
    n_rep += 1


# ═════════ Copias estáticas (para visores sin JS), calculadas igual que el JS ═════════
GRUPOS = [  # mismo array que el JS (Sankey)
    ('Clientes frecuentes', [20, 4, 2], '#3F6652'),
    ('Compraron hace meses', [30, 3, 1], '#3C5470'),
    ('Preguntaron y no compraron', [25, 2, 0], '#8BA0B9'),
    ('Nuevos', [25, 1, 0], '#A9AEB6'),
]
SK_K = 1.8


def fnum(x):
    x = round(x, 2)
    return ('%d' % x) if x == int(x) else ('%g' % x)


def sankey_static():
    VW, VH, X, W, K, GAP, CY = 380, 296, [2, 185, 368], 10, SK_K, [10, 8, 8], 168
    seg = [[None] * 3 for _ in GRUPOS]
    for s in range(3):
        tot = sum(max(g[1][s] * K, 2 if g[1][s] else 0) for g in GRUPOS)
        y = CY - (tot + GAP[s] * (len(GRUPOS) - 1)) / 2
        for i, g in enumerate(GRUPOS):
            h = max(g[1][s] * K, 2 if g[1][s] else 0)
            seg[i][s] = (y, y + h)
            y += h + GAP[s]
    out = ['<defs><clipPath id="skc"><rect class="sk-rev" x="0" y="0" width="%d" height="%d"></rect></clipPath></defs><g clip-path="url(#skc)">' % (VW, VH)]
    for i, (_, v, col) in enumerate(GRUPOS):
        for s in range(2):
            if not v[s + 1]:
                continue
            xa, xb = X[s] + W, X[s + 1]
            m, A, B = (xa + xb) / 2, seg[i][s], seg[i][s + 1]
            d = 'M%s %s C%s %s %s %s %s %s L%s %s C%s %s %s %s %s %s Z' % tuple(fnum(z) for z in (
                xa, A[0], m, A[0], m, B[0], xb, B[0], xb, B[1], m, B[1], m, A[1], xa, A[1]))
            out.append('<path d="%s" fill="%s" fill-opacity="0.32"></path>' % (d, col))
        for s in range(3):
            if v[s]:
                out.append('<rect x="%d" y="%s" width="%d" height="%s" rx="2" fill="%s"></rect>' % (
                    X[s], fnum(seg[i][s][0]), W, fnum(seg[i][s][1] - seg[i][s][0]), col))
    out.append('</g>')
    heads = [('100', 'enviados', 'start', X[0]), ('10', 'respondieron', 'middle', X[1] + W / 2), ('3', 'compraron', 'end', X[2] + W)]
    for num, lab, anc, x in heads:
        out.append('<text x="%s" y="24" text-anchor="%s" font-family="Geist, sans-serif" font-size="19" fill="#1C2129">%s <tspan fill="#7D838D" font-size="15">%s</tspan></text>' % (fnum(x), anc, num, lab))
    aria = ('Embudo de la campaña: de 100 enviados, 10 respondieron y 3 compraron. Clientes frecuentes: 20 enviados, '
            '4 respondieron y 2 compraron; compraron hace meses: 30, 3 y 1; preguntaron y no compraron: 25, 2 y ninguna compra; nuevos: 25, 1 y ninguna compra.')
    return ('        <svg class="sankey" id="sankey" viewBox="0 0 %d %d" role="img" aria-label="%s">%s</svg>' % (VW, VH, aria, ''.join(out)))


def respondio(v):
    if not v[1]:
        return 'nadie respondió'
    g = math.gcd(v[1], v[0]) or 1
    x, y = v[1] // g, v[0] // g
    return '%d de cada %d %s' % (x, y, 'respondió' if x == 1 else 'respondieron')


def legend_static():
    return ('        <div class="sk-legend" id="skLegend">' + ''.join(
        '<div style="--c: %s;"><b>%s</b><span>%s</span><span>%s</span></div>' % (col, n, ' → '.join(map(str, v)), respondio(v))
        for n, v, col in GRUPOS) + '</div>')


def js_round2(x):
    # toFixed(2) de JS (redondeo de la representación decimal); para la copia estática basta
    return '%.2f' % (math.floor(x * 100 + 0.5) / 100)


def heat_static():
    days = ['L', 'M', 'M', 'J', 'V', 'S', 'D']
    vals = []
    for d in range(7):
        for h in range(24):
            base = .3 if h < 7 else 1.6 if h < 12 else 2.2 if h < 15 else 2 if h < 18 else 4.6 if h < 22 else 1.2
            if 18 <= h <= 20:
                base += 1.8
            if d >= 5:
                base *= 1.35
            vals.append(max(0, base + math.sin(d * 7.1 + h * 1.7) * .8))
    mx = max(vals)
    out = []
    for d in range(7):
        out.append('<span class="d" style="grid-area: %d / 1;">%s</span>' % (d + 1, days[d]))
        for h in range(24):
            out.append('<i class="h" style="grid-area: %d / %d; --a: %s; --k: %d;"></i>' % (d + 1, h + 2, js_round2(.08 + vals[d * 24 + h] / mx * .82), d * 24 + h))
    return '        <div class="heat" id="heat" aria-hidden="true">' + ''.join(out) + '<div class="team"></div></div>'


UNO = [2, 9, 13, 21, 27, 34, 38, 46, 51, 58, 64, 71, 77, 85, 93]   # los ~15 que alcanzas a mano
RESP = [4, 17, 23, 31, 42, 55, 62, 69, 80, 96]                     # los ~10 que responden


def dots_static():
    return ''.join('<i style="--i:%d"%s></i>' % (i, ' class="win"' if i in UNO else '') for i in range(100))


# ═════════ 3.0 · head, comentario de identidad, barra ═════════
R('<title>Tibisay Hoteles · Propuesta C&amp;Co</title>', '<title>Pulso · Mensajería masiva y atención personalizada</title>')
R('  Identidad C&Co (propuesta)', '  Identidad Pulso')
R('  - Recorrido: problema → por qué importa → el sistema por fases → el panel de gerencia → la lógica detrás → inversión → siguiente paso. La calculadora de impacto vive en una ventana que se abre desde el problema, la barra y el cierre.',
  '  - Recorrido: problema → demo de una campaña → por qué funciona → las tres piezas → resultados → por dentro → cómo empezamos → siguiente paso. La calculadora de alcance vive en una ventana que se abre desde el problema, la barra y el cierre.')
R('  - Números de ejemplo coherentes en toda la página: hoy 6 de 300; con el sistema 300 → 100 cotizados → 24 reservas, a unos $400 por reserva.',
  '  - Números de ejemplo coherentes en toda la página: 100 clientes → 95 les llega → 10 responden → 3 compran.')
R('''        C&amp;Co
      </span>''', '''        Pulso
      </span>''')
R('<a class="nav-demo" href="#demo" aria-label="Ver la demo de WhatsApp">', '<a class="nav-demo" href="#demo" aria-label="Ver la demo">')
R('<span class="lbl">WhatsApp</span></a>', '<span class="lbl">Demo</span></a>')
R('''        <a href="#sistema">El sistema</a>
        <a href="#panel">El panel</a>
        <a href="#logica">Cómo funciona</a>
        <a href="#inversion">Inversión</a>
        <a href="#calculadora" data-open-calc>Sus números</a>''', '''        <a href="#sistema">Cómo funciona</a>
        <a href="#panel">Resultados</a>
        <a href="#logica">Por dentro</a>
        <a href="#calculadora" data-open-calc>Tu alcance</a>''')

# ═════════ 3.1 · HERO ═════════
R('<span>Propuesta para <b>Tibisay Hoteles</b>, piloto en Canaima</span>', '<span><b>Mensajería masiva</b> + atención personalizada</span>')
R('<h1>Del anuncio a la reserva confirmada.</h1>', '<h1>Un mensaje para todos. Atención para cada uno.</h1>')
R('<p class="lead">Un panel comercial para el hotel: contesta el WhatsApp al instante, no deja que ningún interesado se enfríe y les muestra qué anuncio trajo cada reserva.</p>',
  '<p class="lead">Envía tu promoción a toda tu base de clientes de una sola vez, por mensaje de texto. Cuando alguien responde, lo atiende una persona de tu equipo, y cada conversación queda en la ficha del cliente.</p>')
R('''        <li data-for="ad"><span>1</span>Ven el anuncio y escriben</li>
        <li data-for="chat"><span>2</span>Les contestan al momento, a cualquier hora</li>
        <li data-for="deal"><span>3</span>Reservan, y ustedes saben de dónde vinieron</li>''', '''        <li data-for="ad"><span>1</span>Escribes un mensaje y le llega a todos</li>
        <li data-for="chat"><span>2</span>Responden y los atiendes uno a uno</li>
        <li data-for="deal"><span>3</span>Cierras la venta y sabes qué campaña funcionó</li>''')
R('<a class="btn" href="#cierre">Empezar con el diagnóstico</a>', '<a class="btn" href="#cierre">Quiero mi primera campaña</a>')
R(' Ver el WhatsApp en acción</a>', ' Ver una campaña en acción</a>')
R('aria-label="Animación de ejemplo: un anuncio de Instagram, la conversación de WhatsApp con el asistente y la reserva confirmada con su campaña de origen."',
  'aria-label="Animación de ejemplo: se escribe una campaña y se envía a 100 clientes, llegan las respuestas a la bandeja con lo que pide cada uno, y una venta avanza en el tablero de la campaña."')
RE(r'          <div class="post card">\n            <div class="post-h"><span class="av s">TH</span>.*?<button class="wa-btn" tabindex="-1">Enviar mensaje por WhatsApp</button>\n            </div>\n          </div>',
   '''          <div class="post card">
            <div class="post-h"><span class="av s">TN</span><div><b>Nueva campaña</b><small>Mensaje de texto</small></div></div>
            <div class="post-img cmp">
              <p class="cmp-to"><span>Para</span><b>Todos tus clientes · 100</b></p>
              <p class="cmp-msg">Hola, <mark>{nombre}</mark>. Esta semana tienes 20% en tu próxima compra. Responde 1 para ver qué entra o 2 para hablar con alguien. BAJA para no recibir más.</p>
              <p class="cmp-n">142/160 caracteres</p>
            </div>
            <div class="post-b">
              <p><b>Promo de la semana.</b> Sale hoy a las 6:00 p. m., con el nombre de cada cliente.</p>
              <button class="wa-btn" tabindex="-1">Enviar a 100</button>
            </div>
          </div>''')
R('''            <div class="chat-h"><span class="av s">TH</span><div><b>Tibisay Canaima</b><small>en línea</small></div></div>
            <div class="msgs">
              <p class="m cli" style="--d:.3s">Hola! cuánto sale para diciembre?</p>
              <p class="m out" style="--d:1.5s"><small>Asistente</small>¡Hola! Con gusto. ¿Qué fechas tienen en mente y cuántas personas viajan?</p>
              <p class="m cli" style="--d:3.1s">del 20 al 23, somos 2 adultos y un niño de 8</p>
              <div class="extract" style="--d:4.2s">
                <span class="chip">Llegada 20 dic</span>
                <span class="chip">3 noches</span>
                <span class="chip">2 adultos, 1 niño</span>
              </div>
              <p class="m out" style="--d:5.1s"><small>Asistente</small>Listo. Andreína les prepara la cotización ahorita mismo.</p>''',
  '''            <div class="chat-h"><span class="av s">TN</span><div><b>Respuestas</b><small>Promo de la semana · llegando</small></div></div>
            <div class="msgs">
              <p class="m cli" style="--d:.3s"><small>Ana M.</small>1</p>
              <p class="m cli" style="--d:1.5s"><small>Pedro R.</small>¿Hay en otro color?</p>
              <p class="m cli" style="--d:3.1s"><small>Sofía L.</small>2</p>
              <div class="extract" style="--d:4.2s">
                <span class="chip">Quiere ver la promo</span>
                <span class="chip">Pide hablar con alguien</span>
                <span class="chip">Asignado a Laura</span>
              </div>
              <p class="m out" style="--d:5.1s"><small>Automático</small>¡Listo! Ya te pasé la promo. Laura te escribe en un momento.</p>''')
R('''            <h3>Reservas de diciembre</h3>
            <div class="cols"><div>Cotizado <span>12</span></div><div>Tentativa <span>6</span></div><div>Confirmada <span>24</span></div></div>''',
  '''            <h3>Promo de la semana</h3>
            <div class="cols"><div>Respondió <span>5</span></div><div>En atención <span>2</span></div><div>Venta <span>3</span></div></div>''')
R('<div class="deal"><b>Familia Rondón</b>20–23 dic · $1.140</div>', '<div class="deal"><b>Ana M.</b>2 unidades · $72</div>')
R('''              <span>Vino del anuncio <b>Salto Ángel, diciembre</b></span>
              <span>$4,38 de pauta por mensaje · $42 por reserva</span>''', '''              <span>Campaña <b>Promo de la semana</b></span>
              <span>100 enviados · 10 respondieron · 3 ventas</span>''')
# Piel del redactor de campaña (escena s-ad)
R('.stage.press .wa-btn{transform:scale(.95)}\n', '''.stage.press .wa-btn{transform:scale(.95)}
.cmp{display:grid;align-content:start;gap:12px;padding:6px 16px 0;overflow:hidden}
.cmp-to{display:flex;gap:8px;align-items:baseline;font-size:.8rem;color:var(--ink3);padding-bottom:10px;border-bottom:1px solid var(--line)}
.cmp-to b{color:var(--ink);font-weight:500}
.cmp-msg{background:var(--mist-bg);color:var(--ink);border-radius:18px 18px 18px 6px;padding:12px 14px;font-size:.9rem;line-height:1.45}
.cmp-msg mark{background:rgba(60,84,112,.14);color:var(--mist-ink);border-radius:4px;padding:0 3px}
.cmp-n{font-size:.74rem;color:var(--ink3);text-align:right}
''')

# ═════════ 3.2 · PROBLEMA ═════════
R('<h2>La pauta funciona. Lo que se pierde está después.</h2>', '<h2>Tienes la lista. Lo difícil es llegarle a todos.</h2>')
R('<p>Lo que nos contaron en la reunión del 9 de octubre: unos $1.000 al mes en pauta para Canaima, unos 300 mensajes y unas 6 reservas.</p>',
  '<p>Escribirle a cada cliente uno por uno no escala: en una tarde llegas a unos pocos y los demás ni se enteran de tu promoción. Con un envío masivo le llega a toda tu base al mismo tiempo.</p>')
LINE('<div class="glass"><div class="dots" id="dots" aria-hidden="true">',
     '      <div class="glass"><div class="dots" id="dots" aria-hidden="true">' + dots_static() + '</div></div>')
R('<p class="big" id="bigN">6<small>de 300</small></p>', '<p class="big" id="bigN">15<small>de 100</small></p>')
R('<p class="muted" id="bigT">Cada punto es un mensaje de WhatsApp al mes. Hoy salen unas 6 reservas, y no se sabe qué anuncio trajo cada una.</p>',
  '<p class="muted" id="bigT">Lo que alcanzas a escribir a mano en una tarde. Los otros 85 no se enteran.</p>')
R('''            <button type="button" aria-pressed="true" data-mode="hoy">Hoy</button>
            <button type="button" aria-pressed="false" data-mode="meta">Meta del piloto</button>''',
  '''            <button type="button" aria-pressed="true" data-mode="uno">Uno por uno</button>
            <button type="button" aria-pressed="false" data-mode="pulso">Con Pulso</button>''')
R('<button type="button" class="link" data-open-calc>Hagan sus números</button>', '<button type="button" class="link" data-open-calc>Calcula tu alcance</button>')
R('<p class="nojs muted">Meta del piloto: <b>24 de 300</b>, cuatro veces lo de hoy, con la misma pauta. El número real sale del diagnóstico.</p>',
  '<p class="nojs muted">Con Pulso: <b>100 de 100</b>. A todos les llega el mismo mensaje. Los que responden pasan a tu bandeja para atenderlos en persona.</p>')
R('.dots{display:grid;grid-template-columns:repeat(25,1fr);', '.dots{display:grid;grid-template-columns:repeat(20,1fr);')
R('.dots.filt.meta i.win{background:var(--sage-ink)}', '.dots.filt.all i.win{background:var(--mist-ink);transform:none}\n.dots.filt.all i.resp{background:var(--sage-ink);transform:scale(1.3)}')
R('''  /* 300 puntos */
  var dots = document.getElementById('dots');
  var hoy = [17, 64, 118, 171, 222, 279];
  var meta = hoy.concat([3, 29, 41, 52, 77, 93, 106, 131, 146, 158, 184, 199, 209, 236, 251, 263, 290, 297]);
  dots.textContent = ''; // la copia estática del HTML es para visores sin JavaScript
  for (var i = 0; i < 300; i++) { var d = document.createElement('i'); d.style.setProperty('--i', i); dots.appendChild(d); }
  var bigN = document.getElementById('bigN'), bigT = document.getElementById('bigT');
  function mark(mode){
    var list = mode === 'meta' ? meta : hoy;
    dots.classList.toggle('meta', mode === 'meta');
    Array.prototype.forEach.call(dots.children, function(e, idx){ e.classList.toggle('win', list.indexOf(idx) > -1); });
    bigN.innerHTML = list.length + '<small>de 300</small>';
    bigT.textContent = mode === 'meta'
      ? 'Con respuesta inmediata y seguimiento por toques, la meta del piloto es 24 de 300: cuatro veces lo de hoy, con la misma pauta. El número real sale del diagnóstico.'
      : 'Cada punto es un mensaje de WhatsApp al mes. Hoy salen unas 6 reservas, y no se sabe qué anuncio trajo cada una.';''',
  '''  /* 100 puntos: un punto es un cliente */
  var dots = document.getElementById('dots');
  var uno = %s;
  var resp = %s;
  dots.textContent = ''; // la copia estática del HTML es para visores sin JavaScript
  for (var i = 0; i < 100; i++) { var d = document.createElement('i'); d.style.setProperty('--i', i); dots.appendChild(d); }
  var bigN = document.getElementById('bigN'), bigT = document.getElementById('bigT');
  function mark(mode){
    var all = mode === 'pulso';
    dots.classList.toggle('all', all);
    Array.prototype.forEach.call(dots.children, function(e, idx){ e.classList.toggle('win', all || uno.indexOf(idx) > -1); e.classList.toggle('resp', all && resp.indexOf(idx) > -1); });
    bigN.innerHTML = (all ? 100 : uno.length) + '<small>de 100</small>';
    bigT.textContent = all
      ? 'A todos les llega el mismo mensaje. Los que responden pasan a tu bandeja para atenderlos en persona.'
      : 'Lo que alcanzas a escribir a mano en una tarde. Los otros 85 no se enteran.';''' % (UNO, RESP))
R("if (!dots.querySelector('.win')) mark('hoy');", "if (!dots.querySelector('.win')) mark('uno');")

# ═════════ 3.3 · DEMO ═════════
R('<!-- ───────── DEMO DE WHATSAPP ───────── -->', '<!-- ───────── DEMO DE UNA CAMPAÑA ───────── -->')
R('<span class="tag" style="--c:var(--sage)"><i></i>Fase 2 · WhatsApp comercial, en acción</span>', '<span class="tag" style="--c:var(--sage)"><i></i>La demo · una campaña de principio a fin</span>')
R('<h2>Así atendería su WhatsApp.</h2>', '<h2>Así se ve una campaña.</h2>')
R('<p>Una conversación de ejemplo, del anuncio a la reserva y de vuelta un año después. En el teléfono, lo que ve el huésped; en el panel, lo que ve el hotel al mismo tiempo. Las respuestas del asistente las deciden ustedes, y cualquier chat se puede tomar cuando quieran.</p>',
  '<p>Un mismo mensaje sale a tus 100 clientes. Arriba, el teléfono de una clienta que responde; abajo, lo que ves tú al mismo tiempo. Lo automático lo decides tú, y cualquier conversación la puede tomar una persona cuando quiera.</p>')
demo_html = open(os.path.join(TOOLS, 'demo_block.html'), encoding='utf-8').read()
demo_css = open(os.path.join(TOOLS, 'demo_block.css'), encoding='utf-8').read()
RE(r'    <!-- demo:inicio .*?<!-- demo:fin -->', demo_html)
RE(r'/\* demo:inicio \*/.*?/\* demo:fin \*/', demo_css)
# Piel SMS neutra
R('/* Demo de WhatsApp: a un lado el teléfono del huésped, al otro el panel del hotel */', '/* Demo: a un lado la conversación de la clienta, al otro tu bandeja */')
R('overflow:hidden;display:flex;flex-direction:column;background:#EFEAE2;font-size:14.5px', 'overflow:hidden;display:flex;flex-direction:column;background:#F4F5F7;font-size:14.5px')
R('.ph-h small .typ{color:var(--sage-ink)}\n', '')
R('background:#EFEAE2 radial-gradient(rgba(122,95,53,.09) 1px,transparent 1.2px) 0 0/16px 16px}', 'background:#F4F5F7}')
R('background:rgba(239,234,226,.4);cursor:pointer', 'background:rgba(244,245,247,.4);cursor:pointer')
R('.wm.me{align-self:flex-end;background:#D9FDD3;', '.wm.me{align-self:flex-end;background:var(--mist-bg);')
R('.wm .tm svg{color:#53BDEB}\n', '')
R('''.wm.typ{padding:11px 13px;display:flex;gap:4px}
.wm.typ i{width:7px;height:7px;border-radius:50%;background:#8696A0;animation:blink 1.1s infinite both}
.wm.typ i:nth-child(2){animation-delay:.18s}.wm.typ i:nth-child(3){animation-delay:.36s}
''', '')
RE(r'\.wa-ref\{[^\n]*\n\.wa-ref svg\{[^\n]*\n\.wa-ref b\{[^\n]*\n\.wa-btns\{[^\n]*\n\.wa-btns span\{[^\n]*\n\.wa-btns span\.press\{[^\n]*\n\.wa-btns\.used span:not\(\.picked\)\{[^\n]*\n\.wa-img\{[^\n]*\n\.wa-img svg\{[^\n]*\n', '')
R('.ph-in i{width:38px;height:38px;border-radius:50%;background:var(--sage-ink);', '.ph-in i{width:38px;height:38px;border-radius:50%;background:var(--ink);')
R('/* ===== Propuesta A · sin iPhone: la conversacion es un chat de WhatsApp a ancho completo ===== */', '/* ===== Sin iPhone: la conversacion es un chat de mensajes de texto a ancho completo ===== */')
R('.wa-chat{position:relative;width:100%;height:min(700px,max(480px,calc(100svh - 190px)));border-radius:26px;overflow:hidden;background:#EFEAE2;',
  '.wa-chat{position:relative;width:100%;height:min(700px,max(480px,calc(100svh - 190px)));border-radius:26px;overflow:hidden;background:#F4F5F7;')
R('.wa-chat .ph-h{padding:10px 14px 10px 10px;background:#075E54;color:#fff;border-bottom:0}', '.wa-chat .ph-h{padding:10px 14px 10px 10px;background:var(--ink);color:#fff;border-bottom:0}')
R('.wa-chat .ph-h small .typ{color:#fff}\n', '')
R('  /* Edge a edge, como WhatsApp en el telefono */', '  /* Edge a edge, como la app de mensajes del telefono */')
R('''  /* Demo de WhatsApp. La animación es solo CSS (la genera demo-whatsapp.mjs) y el play es un checkbox,''',
  '''  /* Demo de una campaña. La animación es solo CSS (la genera tools/gen_demo.py) y el play es un checkbox,''')

# ═════════ 3.4 · POR QUÉ FUNCIONA ═════════
R('''      <h2>Por qué vale la pena.</h2>
      <p>Tres datos de la industria que explican de dónde sale la mejora.</p>''', '''      <h2>Por qué funciona.</h2>
      <p>Tres ideas simples detrás de cada campaña.</p>''')
R('<p>más probable concretar un interesado cuando se le responde en menos de una hora.</p>', '<p>más probable concretar una venta cuando a quien pregunta se le responde en menos de una hora.</p>')
RE(r'      <div class="glass fact">\n        <span class="v">15–25%</span>.*?Meta, estudio global 2024</a></span>\n      </div>',
   '''      <div class="glass fact">
        <span class="v">100 de 100</span>
        <p>Un mensaje de texto le llega a cualquier teléfono, sin apps ni cuentas. Nadie se queda fuera de tu promoción.</p>
      </div>
      <div class="glass fact">
        <span class="v">1 ficha</span>
        <p>por cliente: lo que compró, lo que preguntó y quién lo atendió. La próxima campaña ya sabe a quién le habla.</p>
      </div>''')
R('<p class="swipe" aria-hidden="true">Deslicen para ver más →</p>', '<p class="swipe" aria-hidden="true">Desliza para ver más →</p>', n=3)

# ═════════ 3.5 · SISTEMA ═════════
R('''      <h2>Así se vería el sistema.</h2>
      <p>Pedazos de las pantallas que va a usar su equipo. Los datos son de ejemplo; el diagnóstico pone los suyos.</p>''', '''      <h2>Tres piezas, un mismo lugar.</h2>
      <p>Así se ven las pantallas que usa tu equipo. Los datos son de ejemplo.</p>''')
R('''        <span class="tag" style="--c:var(--mist)"><i></i>Fase 1 · Ver y medir</span>
        <h3>Cuánto cuesta cada mensaje, cada día, por campaña.</h3>
        <ul>
          <li>Gasto, mensajes y costo por mensaje de cada anuncio.</li>
          <li>Enlaces y formularios marcados para saber de qué campaña viene cada contacto.</li>
          <li>A qué horas escriben y cuándo no hay nadie para contestar.</li>
          <li>Sugerencias claras: qué subir, qué pausar y por qué.</li>
        </ul>
        <p class="price"><b>32 horas</b>1 a 2 semanas</p>''', '''        <span class="tag" style="--c:var(--mist)"><i></i>1 · Envío masivo</span>
        <h3>Un mensaje, toda tu base, en minutos.</h3>
        <ul>
          <li>Escribes el mensaje una vez y eliges a quién: todos o un grupo.</li>
          <li>Cada mensaje lleva el nombre del cliente.</li>
          <li>Programas el día y la hora.</li>
          <li>Quien responde BAJA no vuelve a recibir.</li>
        </ul>''')
R('''<b>Anuncios · Canaima</b></span><small>Últimos 30 días</small></div>
          <div class="ui-body">
            <div>
              <div class="camp h"><span>Campaña</span><span>Mensajes</span><span class="r">Por mensaje</span><span class="r">Reservas</span></div>
              <div class="camp"><span>Salto Ángel, diciembre</span><span class="meter"><i style="--w:96%"></i></span><span class="r">$4,38</span><span class="r">10</span></div>
              <div class="camp"><span>Laguna, fin de semana</span><span class="meter"><i style="--w:58%"></i></span><span class="r">$4,48</span><span class="r">5</span></div>
              <div class="camp"><span>Paquete familia</span><span class="meter"><i style="--w:31%"></i></span><span class="r">$3,55</span><span class="r">4</span></div>
              <div class="camp"><span>Promo genérica</span><span class="meter"><i class="bad" style="--w:22%"></i></span><span class="r bad-t">$9,55</span><span class="r bad-t">0</span></div>
            </div>''', '''<b>Campañas · último mes</b></span><small>4 campañas</small></div>
          <div class="ui-body">
            <div>
              <div class="camp h"><span>Campaña</span><span>Enviados</span><span class="r">Respuestas</span><span class="r">Ventas</span></div>
              <div class="camp"><span>Promo de la semana</span><span class="meter"><i style="--w:95%"></i></span><span class="r">10</span><span class="r">3</span></div>
              <div class="camp"><span>Novedades</span><span class="meter"><i style="--w:92%"></i></span><span class="r">8</span><span class="r">2</span></div>
              <div class="camp"><span>Recordatorio de pago</span><span class="meter"><i style="--w:36%"></i></span><span class="r">12</span><span class="r">5</span></div>
              <div class="camp"><span>Saludo genérico</span><span class="meter"><i class="bad" style="--w:96%"></i></span><span class="r bad-t">2</span><span class="r bad-t">0</span></div>
            </div>''')
R('<p><b>Muevan los $210 de "Promo genérica" a "Paquete familia".</b> Cada mensaje sale a menos de la mitad y ya trajo 4 reservas.</p>',
  '<p><b>"Saludo genérico" no vendió nada:</b> la próxima vez manda una oferta concreta, como en "Promo de la semana".</p>')
R('''        <span class="tag" style="--c:var(--sage)"><i></i>Fase 2 · WhatsApp comercial</span>
        <h3>Nadie se queda esperando, y cada chat tiene su responsable.</h3>
        <ul>
          <li>El WhatsApp del hotel en un servidor propio, con una bandeja para todo el equipo.</li>
          <li>Un asistente contesta al instante, pide fechas, personas y habitación, y resume cada chat.</li>
          <li>Si un cliente lleva 15 minutos sin respuesta, la gerencia se entera.</li>
          <li>Cada interesado avanza de cotizado a hospedado. Si se pierde, queda el motivo.</li>
          <li>Cada intento de contacto queda como toque, positivo o negativo, y el sistema avisa cuándo toca insistir.</li>
          <li>Cada reserva confirmada vuelve a Meta, para que la pauta busque gente que reserva.</li>
        </ul>
        <p class="price"><b>72 horas</b>unas 3 semanas</p>''', '''        <span class="tag" style="--c:var(--sage)"><i></i>2 · Bandeja y atención personalizada</span>
        <h3>Nadie que responde se queda esperando.</h3>
        <ul>
          <li>Todas las respuestas llegan a una bandeja para tu equipo.</li>
          <li>Las respuestas simples ("1", "2") se contestan solas; lo demás pasa a una persona.</li>
          <li>Cada conversación tiene un responsable.</li>
          <li>Si alguien lleva 15 minutos sin respuesta, te avisamos.</li>
          <li>Cada contacto queda registrado y el sistema te dice cuándo volver a escribir.</li>
        </ul>''')
R('''              <div class="row"><span class="av s">MR</span><div><b>María Rondón</b><p>Resumen: 2 habitaciones, 22 al 26 dic, abona hoy</p></div><div class="who"><span class="pill">Reserva tentativa</span>Andreína</div></div>
              <div class="row" id="lateRow"><span class="av">JP</span><div><b>José Pérez</b><p>¿Tienen habitación para 4 en enero?</p></div><div class="who"><span class="pill wait">Esperando <span id="timer">15:00</span></span>Carla</div></div>
              <div class="row"><span class="av a">LG</span><div><b>Luisa Guerra</b><p>Asistente: ¿para qué fechas sería?</p></div><div class="who"><span class="pill ai">Calificando</span>Asistente</div></div>''',
  '''              <div class="row"><span class="av s">AM</span><div><b>Ana Méndez</b><p>Resumen: 2 unidades, retira el sábado</p></div><div class="who"><span class="pill">Por pagar</span>Laura</div></div>
              <div class="row" id="lateRow"><span class="av">PR</span><div><b>Pedro Ríos</b><p>¿Tienen envío a domicilio?</p></div><div class="who"><span class="pill wait">Esperando <span id="timer">15:00</span></span>Jorge</div></div>
              <div class="row"><span class="av a">SL</span><div><b>Sofía López</b><p>Automático: ¿qué te gustaría ver?</p></div><div class="who"><span class="pill ai">Automático</span>Automático</div></div>''')
R('''              José Pérez lleva 15 minutos sin respuesta. Avisamos a gerencia.''', '''              Pedro Ríos lleva 15 minutos sin respuesta. Te avisamos.''')
R('''        <span class="tag" style="--c:var(--sand)"><i></i>Fase 3 · Huéspedes que vuelven</span>
        <h3>El que ya vino es el más fácil de traer de nuevo.</h3>
        <ul>
          <li>Base de huéspedes a partir del sistema del hotel.</li>
          <li>Grupos listos: quién vino hace un año, quién preguntó y no reservó.</li>
          <li>Qué fechas les piden y no tienen cupo, para decidir tarifas y temporadas.</li>
          <li>Mensajes por WhatsApp con plantillas aprobadas y topes para no saturar.</li>
        </ul>
        <p class="price"><b>24 horas</b>1 semana</p>''', '''        <span class="tag" style="--c:var(--sand)"><i></i>3 · Tu base de clientes (CRM)</span>
        <h3>El que ya te compró es el más fácil de que vuelva.</h3>
        <ul>
          <li>Importas tu lista de clientes en minutos.</li>
          <li>Grupos listos: quién compró, quién preguntó y no compró, quién no responde hace tiempo.</li>
          <li>Cada campaña nueva se arma con un grupo, sin saturar a nadie.</li>
        </ul>''')
R('<b>Vinieron en diciembre 2025</b></span><small>23 huéspedes</small></div>', '<b>Compraron en la última promo</b></span><small>Grupo</small></div>')
R('<span class="av">CM</span><div><b>Carlos Medina</b><small>4 personas · 3 noches</small></div><span class="small">$1.320</span>',
  '<span class="av">AM</span><div><b>Ana Méndez</b><small>2 compras · cliente desde marzo</small></div><span class="small">$72</span>')
R('<span class="av r">AV</span><div><b>Ana Velásquez</b><small>2 personas · 2 noches</small></div><span class="small">$640</span>',
  '<span class="av r">LR</span><div><b>Luis Romero</b><small>1 compra · cliente desde junio</small></div><span class="small">$45</span>')
R('<span class="av a">RS</span><div><b>Ricardo Salas</b><small>5 personas · 4 noches</small></div><span class="small">$1.980</span>',
  '<span class="av a">EC</span><div><b>Elena Castro</b><small>4 compras · cliente desde enero</small></div><span class="small">$63</span>')
R('''<p id="sendTxt">Plantilla: <b>"Vuelve a Canaima esta temporada"</b></p>
              <button type="button" id="sendBtn" tabindex="-1">Enviar a 23</button>''', '''<p id="sendTxt">Mensaje: <b>"Llegó lo nuevo y lo ves primero"</b></p>
              <button type="button" id="sendBtn" tabindex="-1">Enviar al grupo</button>''')
R('''    setTimeout(function(){ b.classList.remove('press'); b.textContent = 'Enviado'; p.innerHTML = '<b>23</b> enviados'; }, 1150*k);
    setTimeout(function(){ p.innerHTML = '<b>23</b> enviados · <b>5</b> ya respondieron'; }, 2600*k);''',
  '''    setTimeout(function(){ b.classList.remove('press'); b.textContent = 'Enviado'; p.innerHTML = '<b>Enviado</b>'; }, 1150*k);
    setTimeout(function(){ p.innerHTML = '<b>Enviado</b> · <b>2</b> ya respondieron'; }, 2600*k);''')
R('  .camp > :nth-child(4){display:none}', '  .camp > :nth-child(3){display:none}')
R('/* Fases apiladas: en pantallas grandes y altas, cada fase se queda pegada arriba y la siguiente se le monta encima */',
  '/* Piezas apiladas: en pantallas grandes y altas, cada pieza se queda pegada arriba y la siguiente se le monta encima */')

# ═════════ 3.6 · RESULTADOS (antes panel de gerencia) ═════════
R('<!-- ───────── PANEL DE GERENCIA ───────── -->', '<!-- ───────── RESULTADOS ───────── -->')
R('/* Panel de gerencia */', '/* Resultados */')
R('''      <h2>El panel de gerencia.</h2>
      <p>Lo que ven los dueños cada mañana: dónde se va la plata, dónde se pierde la gente y cuánto va a entrar. Datos de ejemplo de un diciembre.</p>''',
  '''      <h2>Lo que pasó con cada campaña.</h2>
      <p>Cuántos recibieron, cuántos respondieron y cuántos compraron. Datos de ejemplo de una campaña a 100 clientes.</p>''')
R('<header><h3>Del anuncio a la reserva, por campaña</h3><small>300 mensajes · 100 cotizados · 24 reservas</small></header>',
  '<header><h3>De enviado a venta, por grupo</h3><small>100 enviados · 10 respondieron · 3 compraron</small></header>')
LINE('<svg class="sankey" id="sankey"', sankey_static())
LINE('<div class="sk-legend" id="skLegend">', legend_static())
R('<p class="ins">Uno de cada tres mensajes llega a cotización, y uno de cada cuatro cotizados reserva. Salto Ángel trae <b>10 de las 24 reservas</b> a <b>$42 de pauta cada una</b>; Promo genérica trae mensajes pero <b>ninguna reserva</b>.</p>',
  '<p class="ins">De 100 enviados, <b>10 respondieron</b> y <b>3 compraron</b>. Los clientes frecuentes responden el doble: <b>la próxima promo, empieza por ellos.</b></p>')
R('.sk-legend{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));', '.sk-legend{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));')
R('''  /* Sankey por campaña */
  var ads = [
    {n:'Salto Ángel, diciembre', v:[96,34,10], col:'#3C5470', pauta:420},
    {n:'Laguna, fin de semana',  v:[58,21,5],  col:'#8BA0B9', pauta:260},
    {n:'Paquete familia',        v:[31,14,4],  col:'#3F6652', pauta:110},
    {n:'Promo genérica',         v:[22,6,0],   col:'#8A4A4E', pauta:210},
    {n:'Sin anuncio',            v:[93,25,5],  col:'#A9AEB6', pauta:0}
  ];''', '''  /* Sankey de la campaña, por grupo de la base: enviados → respondieron → compraron */
  var ads = [
%s
  ];''' % ',\n'.join("    {n:'%s', v:[%s], col:'%s'}" % (n, ','.join(map(str, v)), c) for n, v, c in GRUPOS))
R('var VW = narrow ? 380 : 760, VH = narrow ? 300 : 290;', 'var VW = narrow ? 380 : 760, VH = narrow ? 296 : 290;')
R('/* Fases */', '/* Las tres piezas */')
R('var X = narrow ? [2, 185, 368] : [40, 372, 704], W = 10, K = .64,', 'var X = narrow ? [2, 185, 368] : [40, 372, 704], W = 10, K = %s,' % SK_K)
R("var heads = [['300','mensajes','start'],['100','cotizados','middle'],['24','reservas','end']];",
  "var heads = [['100','enviados','start'],['10','respondieron','middle'],['3','compraron','end']];")
R('''      var per = a.pauta ? (a.v[2] ? '$' + Math.round(a.pauta/a.v[2]) + ' de pauta por reserva' : 'sin reservas') : 'orgánico';''',
  '''      var g = (function gcd(x, y){ return y ? gcd(y, x % y) : x; })(a.v[0], a.v[1]) || 1, x = a.v[1] / g;
      var per = a.v[1] ? x + ' de cada ' + (a.v[0] / g) + (x === 1 ? ' respondió' : ' respondieron') : 'nadie respondió';''')
R('<header><h3>Cuándo escriben</h3><small>Mensajes por día y hora</small></header>', '<header><h3>A qué hora responden</h3><small>Respuestas por día y hora</small></header>')
LINE('<div class="heat" id="heat" aria-hidden="true">', heat_static())
R('<p class="ins" id="heatIns">El <b>64%</b> de los mensajes llega cuando no hay nadie atendiendo, sobre todo de noche y el domingo. <b>Ahí contesta el asistente.</b></p>',
  '<p class="ins" id="heatIns">La mayoría responde <b>entre las 6 y las 9 de la noche</b>. Programa tus envíos para esa hora, o deja lo automático contestando cuando tu equipo no está.</p>')
R('''  /* Mapa de calor: mensajes por día y hora */''', '''  /* Mapa de calor: respuestas por día y hora */''')
R('''      var base = h < 7 ? .3 : h < 12 ? 2.2 : h < 15 ? 3 : h < 19 ? 2.4 : h < 23 ? 4.6 : 1.4;
      if (h >= 20 && h <= 22) base += 1.6;''', '''      var base = h < 7 ? .3 : h < 12 ? 1.6 : h < 15 ? 2.2 : h < 18 ? 2 : h < 22 ? 4.6 : 1.2;
      if (h >= 18 && h <= 20) base += 1.8;''')
R('''    var pct = Math.round(off/tot*100);
    document.getElementById('heatIns').innerHTML = 'El <b>' + pct + '%</b> de los mensajes llega cuando no hay nadie atendiendo, sobre todo de noche y el domingo. <b>Ahí contesta el asistente.</b>';
''', '')
R('''        <header><h3>Cuánto va a entrar</h3><small>Diciembre</small></header>
        <div class="fc-bar" aria-hidden="true"><i style="--w:80%"></i><i style="--w:14%"></i></div>
        <div class="fc-nums">
          <div>Confirmado<b>$9.600</b></div>
          <div>Esperado<b>$1.700</b></div>
          <div>Meta<b>$12.000</b></div>
        </div>
        <div class="probs">
          <div>Cotizado<b>20%</b></div>
          <div>Tentativa<b>60%</b></div>
          <div>Con abono<b>100%</b></div>
        </div>
        <p class="ins">Ya está confirmado el <b>80% de la meta</b>. Con lo que viene en camino llegan al 94%: faltan <b>$700</b>, y salen de mover las tentativas.</p>''',
  '''        <header><h3>Ventas de la campaña</h3><small>Promo de la semana</small></header>
        <div class="fc-bar" aria-hidden="true"><i style="--w:50%"></i><i style="--w:25%"></i></div>
        <div class="fc-nums">
          <div>Cobrado<b>$180</b></div>
          <div>En conversación<b>$90</b></div>
          <div>Objetivo<b>$360</b></div>
        </div>
        <div class="probs">
          <div>Respondió<b>10%</b></div>
          <div>En atención<b>50%</b></div>
          <div>Pagó<b>100%</b></div>
        </div>
        <p class="ins">Ya entró <b>la mitad del objetivo</b>. Con lo que está en conversación llegas al 75%: faltan <b>$90</b>, y salen de darle seguimiento a los que dejaron de contestar.</p>''')
# Calendario: fuera completo (HTML, JS, CSS y reglas sin JS)
RE(r'\n      <div class="glass tile c12" data-play="cal">.*?</div>\n      </div>\n(?=\n      <div class="glass tile c7" data-play="lost">)', '\n')
RE(r'\n  /\* Calendario de demanda:.*?\n  \}\)\(\);\n(?=\n  /\* Pantallas que se animan al llegar \*/)', '\n')
RE(r'\.cal\{display:grid;grid-template-columns:repeat\(7,1fr\);gap:5px\}\n.*?\.calx-steps b\{color:var\(--ink\);font-weight:500\}\n\n', '')
R('html:not(.js) .seg,html:not(.js) [data-open-calc],html:not(.js) .calx-day{display:none!important}', 'html:not(.js) .seg,html:not(.js) [data-open-calc]{display:none!important}')
R('html:not(.js) .cal .day{opacity:1}\n', '')
R('  .hero-grid,.problem,.phase,.money,.calc,.calx-grid{grid-template-columns:1fr}\n  .calx-grid .cal-w{max-width:440px}\n', '  .hero-grid,.problem,.phase,.money,.calc{grid-template-columns:1fr}\n')
R('  .btn:hover,button.day:hover{transform:none}', '  .btn:hover{transform:none}')
# Por qué no compraron
R('''        <header><h3>Por qué se pierden</h3><small>Motivos de las reservas perdidas</small></header>
        <div class="lost">
          <div class="ln"><span>Precio<small>decisión del huésped</small></span><span class="meter"><i style="--w:31%"></i></span><span class="r">31%</span></div>
          <div class="ln can"><span>No había cupo<small>se puede mover</small></span><span class="meter"><i style="--w:24%"></i></span><span class="r">24%</span></div>
          <div class="ln can"><span>Dejó de contestar<small>se puede mover</small></span><span class="meter"><i style="--w:22%"></i></span><span class="r">22%</span></div>
          <div class="ln"><span>Cambió las fechas<small>decisión del huésped</small></span><span class="meter"><i style="--w:13%"></i></span><span class="r">13%</span></div>
          <div class="ln"><span>Eligió otro destino<small>decisión del huésped</small></span><span class="meter"><i style="--w:10%"></i></span><span class="r">10%</span></div>
        </div>
        <p class="ins"><b>Casi la mitad</b> se pierde por cosas que el hotel puede cambiar: cupo y seguimiento.</p>''',
  '''        <header><h3>Por qué no compraron</h3><small>Motivos de los que respondieron y no compraron</small></header>
        <div class="lost">
          <div class="ln"><span>Precio<small>decisión del cliente</small></span><span class="meter"><i style="--w:31%"></i></span><span class="r">31%</span></div>
          <div class="ln can"><span>No era el momento<small>se puede mover</small></span><span class="meter"><i style="--w:24%"></i></span><span class="r">24%</span></div>
          <div class="ln can"><span>Dejó de contestar<small>se puede mover</small></span><span class="meter"><i style="--w:22%"></i></span><span class="r">22%</span></div>
          <div class="ln"><span>Ya lo tenía<small>decisión del cliente</small></span><span class="meter"><i style="--w:13%"></i></span><span class="r">13%</span></div>
          <div class="ln"><span>No le interesó<small>decisión del cliente</small></span><span class="meter"><i style="--w:10%"></i></span><span class="r">10%</span></div>
        </div>
        <p class="ins"><b>Casi la mitad</b> no compró por cosas que sí puedes mover: el momento y el seguimiento.</p>''')
R('''        <header><h3>Cuántos toques hacen falta</h3><small>Intentos de contacto hasta que responden</small></header>
        <div class="touch" aria-label="Ejemplo: primer toque por WhatsApp sin respuesta, segundo toque por llamada sin respuesta, tercer toque por WhatsApp con respuesta.">
          <span class="t"><i>−</i>WhatsApp</span><span class="arr">→</span>
          <span class="t"><i>−</i>Llamada</span><span class="arr">→</span>
          <span class="t pos"><i>+</i>Respondió</span>''', '''        <header><h3>Seguimiento</h3><small>Intentos de contacto hasta que responden</small></header>
        <div class="touch" aria-label="Ejemplo: primer toque por mensaje sin respuesta, segundo toque por llamada sin respuesta, tercer toque por mensaje con respuesta.">
          <span class="t"><i>−</i>Mensaje</span><span class="arr">→</span>
          <span class="t"><i>−</i>Llamada</span><span class="arr">→</span>
          <span class="t pos"><i>+</i>Mensaje</span>''')

# ═════════ 3.7 · POR DENTRO ═════════
R('<!-- ───────── LÓGICA ───────── -->', '<!-- ───────── POR DENTRO ───────── -->')
R('''      <h2>La lógica detrás.</h2>
      <p>Lo que no se ve pero hace que los números sean confiables. Cada mensaje, clic y reserva recorre este camino.</p>''', '''      <h2>Por dentro.</h2>
      <p>Lo que no se ve, pero hace que cada envío llegue y cada respuesta tenga dueño.</p>''')
R('''      <div class="glass node"><span class="k">1</span><h3>Meta y WhatsApp</h3><p>Anuncios, clics y mensajes llegan como eventos, al momento.</p></div>
      <div class="glass node"><span class="k">2</span><h3>Verificación</h3><p>Firma de Meta, sin duplicados, teléfono en formato internacional.</p></div>
      <div class="glass node"><span class="k">3</span><h3>Un huésped, una ficha</h3><p>Anuncio, chat y reserva se unen en la misma persona.</p></div>
      <div class="glass node"><span class="k">4</span><h3>Reglas</h3><p>Califica, asigna asesora, vigila los 15 minutos y marca cuándo insistir.</p></div>
      <div class="glass node"><span class="k">5</span><h3>Panel y alertas</h3><p>Embudo, pronóstico y avisos, siempre al día.</p></div>
      <div class="glass node"><span class="k">6</span><h3>De vuelta a Meta</h3><p>La reserva confirmada regresa como venta, con su valor.</p></div>''',
  '''      <div class="glass node"><span class="k">1</span><h3>Tu lista</h3><p>Subes tus clientes; limpiamos duplicados y números mal escritos.</p></div>
      <div class="glass node"><span class="k">2</span><h3>La campaña</h3><p>Mensaje, grupo y hora; sale a todos a la vez.</p></div>
      <div class="glass node"><span class="k">3</span><h3>Las respuestas</h3><p>Llegan a una sola bandeja, ordenadas por cliente.</p></div>
      <div class="glass node"><span class="k">4</span><h3>Reglas</h3><p>Contesta lo simple, asigna una persona y vigila los 15 minutos.</p></div>
      <div class="glass node"><span class="k">5</span><h3>La ficha</h3><p>Campaña, conversación y venta, en el mismo cliente.</p></div>
      <div class="glass node"><span class="k">6</span><h3>La próxima campaña</h3><p>Con lo aprendido, sabes a quién escribirle y cuándo.</p></div>''')
R('<p class="loop-cap">El ciclo se cierra: <b>Meta aprende qué anuncios traen huéspedes que pagan</b>, no solo gente que escribe.</p>',
  '<p class="loop-cap">El ciclo se cierra: <b>cada campaña te enseña quién compra</b>, no solo quién lee.</p>')
R('''      <div class="glass"><h3>Solo entra lo que viene de Meta</h3><p>Cada mensaje se verifica con su firma digital antes de tocar la base de datos.</p></div>
      <div class="glass"><h3>Nada se cuenta dos veces</h3><p>Cada evento lleva un identificador único, aunque Meta reintente el envío.</p></div>
      <div class="glass"><h3>La huella del clic</h3><p>Guardamos el identificador de cada clic en el anuncio, y con él unimos anuncio y reserva.</p></div>
      <div class="glass"><h3>Cada toque cuenta</h3><p>Cada intento de contacto queda en la ficha: positivo si el cliente respondió, negativo si no. Se sabe cuál fue el primero, cuál el último y cuándo toca insistir.</p></div>
      <div class="glass"><h3>El número no se bloquea</h3><p>Se respeta la ventana de 24 horas de WhatsApp: fuera de ella, solo plantillas aprobadas.</p></div>
      <div class="glass"><h3>Sus datos, en su servidor</h3><p>La información del hotel vive en un servidor propio, con accesos por rol.</p></div>''',
  '''      <div class="glass"><h3>Lista limpia</h3><p>Cada número se revisa antes de enviar: sin duplicados ni formatos rotos.</p></div>
      <div class="glass"><h3>Nadie recibe dos veces</h3><p>Cada envío tiene su identificador; si algo se reintenta, no se repite.</p></div>
      <div class="glass"><h3>Baja con una palabra</h3><p>Quien responde BAJA sale de la lista al instante y no vuelve a recibir.</p></div>
      <div class="glass"><h3>Cada contacto cuenta</h3><p>Cada intento queda en la ficha: si respondió o no, el primero, el último y cuándo toca volver a escribir.</p></div>
      <div class="glass"><h3>¿Y por WhatsApp?</h3><p>WhatsApp no está hecho para envíos masivos: si mandas lo mismo a muchos desde tu número, te lo pueden bloquear. Por eso la campaña sale por mensaje de texto, que le llega a cualquier teléfono, y tu WhatsApp queda tranquilo.</p></div>
      <div class="glass"><h3>Tus clientes son tuyos</h3><p>Tu lista vive en tu cuenta, con accesos por persona. La exportas cuando quieras.</p></div>''')
R('<p class="honest">Una nota honesta: con pocas reservas al mes, Meta aprende más lento. El beneficio de devolverle las ventas crece a medida que crece el volumen.</p>',
  '<p class="honest">Una nota honesta: el envío masivo hace que te lean; lo que vende es responder rápido y bien. Por eso la bandeja importa tanto como el envío.</p>')

# ═════════ 3.8 · CÓMO EMPEZAMOS ═════════
R('<!-- ───────── INVERSIÓN ───────── -->', '<!-- ───────── CÓMO EMPEZAMOS ───────── -->')
R('/* Inversión */', '/* Cómo empezamos */')
R('''      <h2>Por etapas, en horas.</h2>
      <p>Empezamos con un diagnóstico corto. Con lo que encontremos ahí confirmamos el alcance y las horas de cada fase.</p>''', '''      <h2>Tu primera campaña, en tres pasos.</h2>
      <p>Sin instalaciones ni contratos largos. Empezamos con tu lista y una campaña real.</p>''')
R('''          <thead><tr><th>Etapa</th><th class="n">Semanas</th><th class="n">Horas</th></tr></thead>
          <tbody>
            <tr><td>Diagnóstico</td><td class="n">1</td><td class="n">16</td></tr>
            <tr><td>Fase 1 · Ver y medir</td><td class="n">1–2</td><td class="n">32</td></tr>
            <tr><td>Fase 2 · WhatsApp comercial</td><td class="n">3</td><td class="n">72</td></tr>
            <tr><td>Fase 3 · Huéspedes que vuelven</td><td class="n">1</td><td class="n">24</td></tr>
            <tr class="total"><td>Total</td><td class="n">6–7</td><td class="n big-n">144 h</td></tr>
          </tbody>''', '''          <thead><tr><th>Paso</th><th>Qué pasa</th></tr></thead>
          <tbody>
            <tr><td>1 · Subes tu lista</td><td>Nos pasas tus clientes; quitamos duplicados y números mal escritos.</td></tr>
            <tr><td>2 · Escribimos juntos el primer mensaje</td><td>Elegimos el grupo, el texto y la hora del envío.</td></tr>
            <tr><td>3 · Lo envías y atiendes desde la bandeja</td><td>Las respuestas llegan a tu bandeja y tu equipo las atiende ahí mismo.</td></tr>
          </tbody>''')
R('''        <p><b>Se cobra la hora trabajada</b>, con tarifa especial por ser el piloto.</p>
        <p><b>Las horas son un estimado con tope.</b> Si usamos menos, cobramos menos. Nunca pasamos de 15% por encima sin su aprobación, y si cambia lo pedido lo reestimamos juntos.</p>
        <p><b>Cada etapa se paga 50% al empezar y 50% al entregar.</b> Pueden parar después de cualquiera: lo entregado queda funcionando y es suyo.</p>
        <p>Después de la Fase 3, <b>operación y soporte mensual</b>. La pauta y los mensajes de WhatsApp los siguen pagando directo a Meta.</p>''',
  '''        <p><b>Pagas por lo que envías.</b> Sin cobro por cada persona de tu equipo.</p>
        <p><b>Sin instalaciones ni contratos largos.</b> Empiezas con tu lista y una campaña real.</p>
        <p><b>Tu lista es tuya.</b> La exportas cuando quieras.</p>''')

# ═════════ 3.9 · CÓMO TE ACOMPAÑAMOS ═════════
R('<div class="sh"><h2>Cómo trabajamos.</h2></div>', '<div class="sh"><h2>Cómo te acompañamos.</h2></div>')
R('<h3>Horas a la vista</h3><p>Reporte semanal con tarea y fecha. Saben en qué se fue cada hora.</p>', '<h3>Te enseñamos a usarlo</h3><p>Tu equipo aprende con tu primera campaña, no con un manual.</p>')
R('<h3>Entrega probada</h3><p>Cada etapa se prueba con su equipo antes de cobrar el cierre.</p>', '<h3>Pruebas antes de enviar</h3><p>Te mandas el mensaje a ti primero y lo revisas antes de que salga a todos.</p>')
R('<h3>Equipo capacitado</h3><p>Las asesoras aprenden a usar cada parte antes de cerrar la fase.</p>', '<h3>Tu equipo, un solo lugar</h3><p>Todas las conversaciones en una bandeja compartida, cada una con su responsable.</p>')
R('<h3>Sin pago por usuario</h3><p>Corre en un servidor propio, no en una plataforma que cobra por cada asesora.</p>', '<h3>Sin pago por usuario</h3><p>Sin cobro por cada persona de tu equipo: suma a quien necesites.</p>')

# ═════════ 3.10 · CIERRE y 3.11 · FOOTER ═════════
R('''      <h2>Empecemos por saber cuántas reservas se quedan en el camino.</h2>
      <p class="lead">Una semana y 16 horas de trabajo, con sus propios chats y su propia pauta.</p>
      <ol class="next">
        <li><span>1</span>Reunión con quien maneja las redes y con comercialización.</li>
        <li><span>2</span>Revisamos los chats y la pauta, y armamos el informe de impacto.</li>
        <li><span>3</span>Les presentamos el informe y confirmamos las fases con esos números.</li>
      </ol>
      <div class="actions" style="margin-top:8px">
        <button type="button" class="btn" data-open-calc>Hagan sus números</button>
      </div>''', '''      <h2>Empieza con tus 100 clientes.</h2>
      <p class="lead">Trae tu lista; en una sesión armamos tu primer mensaje y lo dejamos listo para salir.</p>
      <ol class="next">
        <li><span>1</span>Nos cuentas qué vendes y a quién.</li>
        <li><span>2</span>Subimos tu lista y escribimos la primera campaña.</li>
        <li><span>3</span>La envías y atiendes las respuestas desde tu bandeja.</li>
      </ol>
      <div class="actions" style="margin-top:8px">
        <a class="btn" href="#cierre" data-contacto>Quiero mi primera campaña</a>
        <button type="button" class="link" data-open-calc>Calcula tu alcance</button>
      </div>''')
R('<footer><div class="in"><span>C&amp;Co · Propuesta para Tibisay Hoteles · Octubre 2026</span><span>Pantallas y datos de ejemplo. Válida por 30 días.</span></div></footer>',
  '<footer><div class="in"><span>Pulso · Mensajería masiva y atención personalizada</span><span>Pantallas y datos de ejemplo.</span></div></footer>')

# ═════════ 3.12 · CALCULADORA (sección 5) ═════════
R('''      <h2 id="calcT">De 300 mensajes y 6 reservas, a cuánto.</h2>
      <p>Cambien los números para ver su caso. El valor por reserva es un supuesto: lo confirmamos con ustedes en el diagnóstico.</p>''', '''      <h2 id="calcT">Calcula tu alcance.</h2>
      <p>Cambia los números por los tuyos. Los porcentajes son supuestos, no promesas: los afinamos con tu primera campaña.</p>''')
R('''        <div class="row2">
          <label class="f">Mensajes al mes<input id="i-msg" type="number" min="0" value="300"></label>
          <label class="f">Pauta al mes (USD)<input id="i-ads" type="number" min="0" value="1000"></label>
        </div>
        <div class="row2">
          <label class="f">Cierre hoy (%)<input id="i-c0" type="number" min="0" step="0.1" value="2"></label>
          <label class="f">Cierre meta (%)<input id="i-c1" type="number" min="0" step="0.1" value="8"></label>
        </div>
        <div class="row2">
          <label class="f">Más mensajes, misma pauta (%)<input id="i-eff" type="number" min="0" value="0"></label>
          <label class="f">Valor por reserva (USD)<input id="i-tk" type="number" min="0" value="400"></label>
        </div>''', '''        <div class="row2">
          <label class="f">Clientes en tu base<input id="i-cli" type="number" min="0" step="1" value="100"></label>
          <label class="f">Campañas al mes<input id="i-camp" type="number" min="0" step="1" value="1"></label>
        </div>
        <div class="row2">
          <label class="f">Les llega (%)<input id="i-ent" type="number" min="0" max="100" step="0.1" value="95"></label>
          <label class="f">Responden (%)<input id="i-resp" type="number" min="0" max="100" step="0.1" value="10"></label>
        </div>
        <div class="row2">
          <label class="f">Compran de los que responden (%)<input id="i-cie" type="number" min="0" max="100" step="0.1" value="30"></label>
          <label class="f">Venta promedio (USD)<input id="i-tk" type="number" min="0" value="40"></label>
        </div>''')
R('''          <div class="kpi"><span class="l">Reservas al mes</span><span class="v" id="o-res">—</span></div>
          <div class="kpi"><span class="l">Pauta por reserva</span><span class="v" id="o-cpr">—</span></div>
          <div class="kpi hl"><span class="l">Ingreso extra al mes</span><span class="v" id="o-inc">—</span></div>
          <div class="kpi hl"><span class="l">Ingreso extra al año</span><span class="v" id="o-pb">—</span></div>''',
  '''          <div class="kpi"><span class="l">Les llega</span><span class="v" id="o-llega">—</span><span class="l">mensajes al mes</span></div>
          <div class="kpi"><span class="l">Te responden</span><span class="v" id="o-resp">—</span><span class="l">conversaciones para atender</span></div>
          <div class="kpi hl"><span class="l">Ventas al mes</span><span class="v" id="o-ventas">—</span></div>
          <div class="kpi hl"><span class="l">Ingreso al mes</span><span class="v" id="o-inc">—</span><span class="l" id="o-anio"></span></div>''')
R('''  function impact(){
    var msg=v('i-msg'), ads_=v('i-ads'), c0=v('i-c0')/100, c1=v('i-c1')/100, eff=v('i-eff')/100, tk=v('i-tk');
    var r0=msg*c0, r1=msg*(1+eff)*c1, extra=Math.max(0,r1-r0), inc=extra*tk;
    document.getElementById('o-res').textContent = f1(r0) + ' → ' + f1(r1);
    document.getElementById('o-cpr').textContent = (r0 ? usd(ads_/r0) : '—') + ' → ' + (r1 ? usd(ads_/r1) : '—');
    document.getElementById('o-inc').textContent = usd(inc);
    document.getElementById('o-pb').textContent = usd(inc*12);
    document.getElementById('o-txt').textContent = inc > 0
      ? 'Con estos supuestos entran ' + f1(extra) + ' reservas más al mes con la misma pauta: ' + usd(inc*12) + ' más en el año.'
      : 'Con estos supuestos no hay reservas extra. Suban la meta de cierre.';
  }
  ['i-msg','i-ads','i-c0','i-c1','i-eff','i-tk'].forEach(function(id){ document.getElementById(id).addEventListener('input', impact); });''',
  '''  // Unas N: redondeo a entero si pasa de 1; si no, con un decimal
  var aprox = function(n){ return n >= 1 ? fmt(Math.round(n)) : f1(n); };
  function impact(){
    var cli=v('i-cli'), camp=v('i-camp'), ent=v('i-ent')/100, resp=v('i-resp')/100, cie=v('i-cie')/100, tk=v('i-tk');
    var llega=cli*camp*ent, conv=llega*resp, ventas=conv*cie, inc=ventas*tk;
    var porCamp=cli*ent*resp;  // conversaciones que abre cada campaña
    document.getElementById('o-llega').textContent = f1(llega);
    document.getElementById('o-resp').textContent = f1(conv);
    document.getElementById('o-ventas').textContent = f1(ventas);
    document.getElementById('o-inc').textContent = usd(inc);
    document.getElementById('o-anio').textContent = '≈ ' + usd(inc*12) + ' al año';
    document.getElementById('o-txt').textContent = ventas > 0
      ? 'Con estos supuestos, cada campaña a tus ' + fmt(cli) + ' clientes abre unas ' + aprox(porCamp) + ' conversaciones y cierra unas ' + aprox(porCamp*cie) + ' ventas: unos ' + usd(inc) + ' al mes. Sube la frecuencia o mejora la respuesta y mira cómo cambia.'
      : 'Con estos supuestos no sale ninguna venta. Prueba subiendo cuántos responden.';
  }
  ['i-cli','i-camp','i-ent','i-resp','i-cie','i-tk'].forEach(function(id){ document.getElementById(id).addEventListener('input', impact); });''')

# ═════════ 3.13 · BOTÓN FLOTANTE + CONVERSACIÓN INMERSIVA ═════════
R('<!-- ───────── WHATSAPP FLOTANTE + CHAT INMERSIVO (el JS clona aquí la conversación de #demo) ───────── -->',
  '<!-- ───────── BOTÓN FLOTANTE + CONVERSACIÓN INMERSIVA (el JS clona aquí la conversación de #demo) ───────── -->')
R('aria-label="Probar la demo: abrir el chat de WhatsApp"', 'aria-label="Probar la demo: abrir la conversación de ejemplo"')
RE(r'<span class="wa-fab__ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="#fff" focusable="false"><path d="M17\.472.*?"/></svg></span>',
   '<span class="wa-fab__ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M6.5 4h11A2.5 2.5 0 0 1 20 6.5v7a2.5 2.5 0 0 1-2.5 2.5H11l-4.5 3.8V16h0A2.5 2.5 0 0 1 4 13.5v-7A2.5 2.5 0 0 1 6.5 4z"/><path d="M8.5 9.2h7M8.5 12h4.5"/></svg></span>')
R('''      <span class="av s">TH</span>
      <div class="wa-ov__id"><b id="waOvT">Tibisay Canaima</b><small>en línea</small></div>
      <button type="button" class="wa-ov__x" id="waX" aria-label="Cerrar el chat">''', '''      <span class="av s">TN</span>
      <div class="wa-ov__id"><b id="waOvT">Tu Negocio</b><small>Mensaje de texto</small></div>
      <button type="button" class="wa-ov__x" id="waX" aria-label="Cerrar la conversación">''')
R('''    <div class="ph-in" aria-hidden="true"><span>Mensaje</span><i><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10a7 7 0 0 0 14 0M12 17v4"/></svg></i></div>''',
  '''    <div class="ph-in" aria-hidden="true"><span>Mensaje de texto</span><i><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg></i></div>''')
R('/* ===== Propuesta v2 · baraja con GSAP, hero fijo que se desvanece, WhatsApp flotante y chat inmersivo ===== */',
  '/* ===== Baraja con GSAP, hero fijo que se desvanece, boton flotante y conversacion inmersiva ===== */')
R('/* Boton flotante de WhatsApp */', '/* Boton flotante de la demo */')
R('display:grid;place-items:center;background:#25D366;box-shadow:0 8px 22px rgba(37,211,102,.38),0 2px 6px rgba(28,33,41,.18);transition:background .2s}',
  'display:grid;place-items:center;background:var(--ink);box-shadow:0 8px 22px rgba(28,33,41,.3),0 2px 6px rgba(28,33,41,.18);transition:background .2s}')
R('.wa-fab:hover .wa-fab__ic{background:#20BD5A}', '.wa-fab:hover .wa-fab__ic{background:#2C333E}')
R('.wa-fab:focus-visible{outline:2px solid #25D366;outline-offset:4px;border-radius:999px}', '.wa-fab:focus-visible{outline:2px solid var(--mist-ink);outline-offset:4px;border-radius:999px}')
R('.wa-fab__ic::before{content:"";position:absolute;inset:0;border-radius:50%;background:#25D366;', '.wa-fab__ic::before{content:"";position:absolute;inset:0;border-radius:50%;background:var(--mist-ink);')
R('overflow:hidden;background:#EFEAE2;font-size:15px;line-height:1.38', 'overflow:hidden;background:#F4F5F7;font-size:15px;line-height:1.38')
R('padding:max(10px,env(safe-area-inset-top)) 12px 10px 14px;background:#075E54;color:#fff}', 'padding:max(10px,env(safe-area-inset-top)) 12px 10px 14px;background:var(--ink);color:#fff}')
R('''/* Baraja + hero fijo + WhatsApp flotante + chat inmersivo.''', '''/* Baraja + hero fijo + boton flotante + conversacion inmersiva.''')
R('  /* ---------- Boton flotante de WhatsApp ---------- */', '  /* ---------- Boton flotante de la demo ---------- */')

# ═════════ Sección 7 · fix de la baraja ═════════
# Fondo opaco (sin el 6% de transparencia que dejaba ver la tarjeta de abajo)
R('  .stk > section{background:linear-gradient(180deg,rgba(255,255,255,.94),rgba(244,245,247,.98) 260px);}',
  '  .stk > section{background:linear-gradient(180deg,#FFFFFF,#F4F5F7 260px)}')
# Alto que cabe: cada tarjeta termina dentro de la pantalla aunque arranque más abajo en la pila;
# sombra más corta para que no ensucie el filo de la tarjeta de abajo
R('  .stk > section:not(.hero){max-height:calc(100vh - 112px);max-height:calc(100dvh - 112px);overflow-y:auto;border-top:1px solid var(--glass-edge);border-radius:26px 26px 0 0;box-shadow:0 -18px 44px rgba(40,52,72,.12),inset 0 1px 0 rgba(255,255,255,.9)}',
  '''  .stk > section:not(.hero){max-height:calc(100vh - 112px - var(--i,0)*14px);max-height:calc(100dvh - 112px - var(--i,0)*14px);overflow-y:auto;border-top:1px solid var(--glass-edge);border-radius:26px 26px 0 0;box-shadow:0 -8px 22px rgba(40,52,72,.08),inset 0 1px 0 rgba(255,255,255,.9)}
  /* Margen superior holgado: el filo de 14 px de una tarjeta recogida (escala .9) muestra solo fondo, nunca texto */
  .stk > section.block{padding-top:32px!important}''')
# Velo que no cubre el filo: transparente en los primeros ~18 px de la tarjeta
R('  .deck-shade{position:absolute;inset:0;border-radius:inherit;background:#1C2129;opacity:0;pointer-events:none}',
  '  .deck-shade{position:absolute;inset:0;border-radius:inherit;background:linear-gradient(180deg,rgba(28,33,41,0) 18px,#1C2129 46px);opacity:0;pointer-events:none}')
# Scroll interno reiniciado al recogerse
R('  var shades = [], isDeck = [], qy = [], qsx = [], qsy = [], qo = [];', '  var shades = [], isDeck = [], qy = [], qsx = [], qsy = [], qo = [], atTop = [];')
R('''      if (p === P[i]) continue;
      P[i] = p; apply(i, p);''', '''      if (p === P[i]) continue;
      P[i] = p; apply(i, p);
      // Recogida del todo: lo que asoma es su cabecera aunque el usuario haya bajado dentro de ella.
      // Solo se escribe scrollTop (no se lee layout); al desplegarla se ve desde arriba, con todo su contenido
      if (p >= .97) { if (!atTop[i]) { atTop[i] = true; cards[i].scrollTop = 0; } }
      else if (p < .5) atTop[i] = false;''')
# Hero: termina de desvanecerse antes de que la tarjeta 1 lo cubra a la mitad
R('''  function heroFallback(){
    var hp = Math.max(0, Math.min(1, (y - fadeStart) / (VH * .7)));''', '''  // Recorrido del desvanecido: nunca más que media altura del hero (la tarjeta 1 lo cubre a la mitad justo ahí)
  function heroSpan(){ var vh = VH || win.innerHeight; return Math.max(1, Math.round(Math.min(vh * .7, (H[0] || vh) * .45))); }
  function heroFallback(){
    var hp = Math.max(0, Math.min(1, (y - fadeStart) / heroSpan()));''')
R('        end: function(){ return fadeStart + Math.round(win.innerHeight * .7); },', '        end: function(){ return fadeStart + heroSpan(); },')

open(SRC, 'w', encoding='utf-8').write(doc)

# ═════════ Verificación (sección 6 y maquinaria) ═════════
GSAP = re.search(r'<script>\n/\*!\n \* GSAP 3\.13\.0.*?</script>\n<script>\n/\*!.*?</script>', doc, re.S)
text = doc.replace(GSAP.group(0), '') if GSAP else doc
# El 300 de las tipografías (peso) no es la cifra del caso anterior
text300 = re.sub(r'font-weight:300|wght@300', '', text)

TERMS = [
    # marca y lugar del cliente anterior
    'Tibisay', 'tibisayhoteles', r'>TH<', 'Canaima', 'Salto Ángel', 'Laguna', 'Puerto Ordaz', 'Ciudad Bolívar', 'avioneta',
    'Propuesta para', 'piloto', 'Válida por 30 días', 'Octubre 2026', 'reunión del 9 de octubre', r'C&amp;Co', 'C&Co',
    # hotelería
    'hotel', 'huésped', 'reserva', 'habitación', 'cupo', 'noches', '2 adultos', 'temporada', 'viajero de afuera', 'otro destino',
    'Paquete', 'Fechas que piden', 'calendario', 'Lista de espera', 'Hospedado', 'Tentativa', 'Cotizad', 'Cotizaci',
    # personas del caso anterior
    'Andreína', 'Carolina', 'Rondón', 'José Pérez', r'\bCarla\b', 'Luisa Guerra', 'Carlos Medina', 'Ana Velásquez', 'Ricardo Salas',
    'asesora', 'gerencia',
    # publicidad / Meta (con mayúscula: la etiqueta <meta> y el CSS no son la marca)
    r'(?-i:\bMeta\b)', 'Instagram', 'anuncio', 'pauta', 'Publicidad', 'Vino del anuncio', 'huella del clic', 'Promo genérica',
    # piel de WhatsApp
    '#25D366', '#20BD5A', '#075E54', '#D9FDD3', '#53BDEB', 'en línea', 'escribiendo', 'Ventana 24 h', 'plantilla', 'WhatsApp comercial',
    'wa-btns', 'wa-ref', 'wa-img', 'class="wm th typ"',
    # cifras del caso anterior
    r'\b300\b', '6 de 300', '24 de 300', '100 cotizados', '24 reservas', r'\$1\.000', r'\$4,38', r'\$4,48', r'\$3,55', r'\$9,55', r'\$42\b',
    r'\$52\b', r'\$28\b', r'\$210\b', r'\$1\.140', r'\$570', r'\$1\.320', r'\$640', r'\$1\.980', r'\$9\.600', r'\$1\.700', r'\$12\.000',
    r'\$700', '23 huéspedes', '47 personas', '19 aceptaron', r'(?<![\d.])64%', '15–25%', '−10%', r'\$400',
    # horas y cobro anterior
    '32 horas', '72 horas', '24 horas', '16 horas', '144 h', '1 a 2 semanas', 'unas 3 semanas', '6–7 semanas', 'Una semana y 16 horas',
    'hora trabajada', 'tarifa especial', 'tope de 15%', '50% al empezar', 'Horas a la vista', 'en qué se fue cada hora', r'\bFases?\b',
    'Diagnóstico',
    # visualización y tono
    'diciembre', 'Deslicen', 'Toquen', 'Hagan sus números', 'Sus números',
]
fails = []
for t in TERMS:
    hits = re.findall(t if t.startswith('(?-i') else t, text300 if t == r'\b300\b' else text, re.I)
    if hits:
        fails.append((t, len(hits)))
wa_lines = [l for l in doc.split('\n') if re.search('whatsapp', l, re.I)]

# Maquinaria que usa el JS
NEED = ['id="waFab"', 'id="waOv"', 'id="waPanel"', 'id="waBody"', 'id="waX"', 'id="waOvT"', 'class="stk', 'class="wm ', 'id="demo"', 'id="dm"',
        'id="dmGo"', 'id="dmCaps"', 'id="dmPrev"', 'id="dmNext"', 'id="calculadora"', 'id="calcT"', 'data-open-calc', 'data-close',
        'id="stage"', 'id="journey"', 'id="dots"', 'id="bigN"', 'id="bigT"', 'id="sankey"', 'id="skLegend"', 'id="heat"', 'id="heatIns"',
        'id="timer"', 'id="lateRow"', 'id="alert"', 'id="sendBtn"', 'id="sendTxt"', 'id="o-txt"', 'class="ph-msgs"', 'class="wa-chat"',
        'class="ui glass dm-panel"', 'data-dur=', 'data-ini=', 'class="nojs', 'html:not(.js)', 'prefers-reduced-motion', 'beforeprint',
        'hx-ad', 'deck-shade', 'class="seg"']
missing = [s for s in NEED if s not in doc]
# ids que el JS pide con getElementById y tienen que existir
js_ids = set(re.findall(r"getElementById\('([\w-]+)'\)", text))
js_ids |= set(re.findall(r"\['(i-[\w-]+)'", text)) | set(re.findall(r"'(i-[\w-]+)'", text))
missing_ids = sorted(i for i in js_ids if ('id="%s"' % i) not in doc)
gsap_ok = GSAP is not None and GSAP.group(0) in orig
kf = re.findall(r'@keyframes (dm\d+)\{', doc)
used = re.findall(r'animation-name:(dm\d+)', doc)
cal_left = [s for s in ('id="cal"', 'calDay', '.calx', '.cal ', 'button.day') if s in doc]
tags_ok = all(doc.count('<%s' % t) == doc.count('</%s>' % t) for t in ('section', 'script', 'style', 'dialog', 'svg', 'ol', 'ul', 'table', 'figure'))
divs = (len(re.findall(r'<div\b', doc)), doc.count('</div>'))

print('reemplazos aplicados: %d' % n_rep)
print('tamaño: %d → %d bytes' % (len(orig.encode()), len(doc.encode())))
print('términos prohibidos con resultados: %d %s' % (len(fails), fails))
print('líneas con "whatsapp" (-i): %d' % len(wa_lines))
for l in wa_lines:
    print('   ', l.strip()[:140])
print('maquinaria ausente: %s · ids del JS sin elemento: %s' % (missing or 0, missing_ids or 0))
print('GSAP+ScrollTrigger intactos: %s' % gsap_ok)
print('demo: %d burbujas, %d capítulos, %d keyframes definidos / %d usados, calendario restante: %s'
      % (doc.count('class="wm '), doc.count('data-ini='), len(kf), len(set(used)), cal_left or 0))
print('etiquetas balanceadas: %s · div %d/%d' % (tags_ok, divs[0], divs[1]))
ok = (not fails and len(wa_lines) == 1 and not missing and not missing_ids and gsap_ok and tags_ok and divs[0] == divs[1]
      and len(kf) == len(set(used)) == len(used) and not cal_left and doc.count('class="wm ') == 28)
print('TRANSFORM_OK' if ok else 'TRANSFORM_FALLÓ')
sys.exit(0 if ok else 1)
