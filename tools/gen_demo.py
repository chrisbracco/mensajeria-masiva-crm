#!/usr/bin/env python3
"""Generador de la demo de la landing (bloque <!-- demo:inicio --> ... <!-- demo:fin -->).

Reemplaza a propuesta/demo-whatsapp.mjs (no está en el repo). A partir del guion de
28 mensajes de ARQUITECTURA-CONTENIDO.md (sección 4) calcula la línea de tiempo y emite:

  tools/demo_block.html   el bloque HTML (checkbox #dmGo + .demo#dm con data-dur / data-ini)
  tools/demo_block.css    las reglas .dmv y los @keyframes dm0…dmN
  tools/demo_timing.json  la línea de tiempo (ms) para revisar o depurar

La animación es solo CSS: cada pieza (.dmv) tiene su propio @keyframes que dura lo mismo
que la demo entera, y el JS de la página solo da play, pausa y salta (lee data-dur y
data-ini del HTML, así que no hay que tocarlo cuando cambia el timing).
"""
import html
import json
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))

# ───────── Guion (sección 4) ─────────
CAMP1 = ('Hola, Ana. Esta semana tienes 20% en tu próxima compra. Responde 1 para ver qué entra '
         'o 2 para hablar con alguien. BAJA para no recibir más.')
CAMP2 = ('Hola, Ana. Llegó lo nuevo y nuestros clientes lo ven primero. Responde 1 para verlo '
         'o 2 para hablar con Laura. BAJA para no recibir más.')

# (capítulo, quién, texto, hora)   quién: camp | auto | laura | ana
GUION = [
    (1, 'camp', CAMP1, '6:02 p. m.'),
    (2, 'ana', '1', '6:04 p. m.'),
    (2, 'auto', '¡Listo! Esto es lo que entra en la promo: tunegocio.com/promo. Si algo te gusta, respóndeme aquí.', '6:04 p. m.'),
    (2, 'ana', 'me gusta el segundo. lo tienen en otro color?', '6:05 p. m.'),
    (2, 'auto', 'Buena pregunta para Laura. Ya te la paso, te escribe en un momento.', '6:05 p. m.'),
    (3, 'laura', 'Hola, Ana, soy Laura. Sí: lo tenemos en azul y en gris. ¿Cuál prefieres?', '6:09 p. m.'),
    (3, 'ana', 'azul. y si llevo dos, el descuento es para los dos?', '6:10 p. m.'),
    (3, 'laura', 'Sí, el 20% va en cada uno. Los dos te quedan en $72 en vez de $90.', '6:10 p. m.'),
    (3, 'ana', 'perfecto. hacen envíos?', '6:11 p. m.'),
    (3, 'laura', 'Sí, a domicilio, o lo retiras en la tienda sin costo. ¿Qué te queda mejor?', '6:27 p. m.'),
    (3, 'ana', 'lo retiro el sábado', '6:28 p. m.'),
    (3, 'laura', 'Hecho. Te los aparto a tu nombre hasta el sábado. ¿Cómo prefieres pagar?', '6:28 p. m.'),
    (3, 'ana', 'transferencia', '6:29 p. m.'),
    (3, 'laura', 'Te paso los datos en el siguiente mensaje. Cuando pagues, mándame el número de referencia y lo dejo confirmado.', '6:29 p. m.'),
    (4, 'ana', 'listo, ya transferí. referencia 004821', '7:31 p. m.'),
    (4, 'laura', '¡Recibido, Ana! Pedido confirmado: 2 unidades en azul, $72, retiro el sábado.', '7:33 p. m.'),
    (4, 'ana', 'gracias Laura!!', '7:33 p. m.'),
    (4, 'laura', 'A ti. El sábado en la mañana te escribimos para recordártelo.', '7:34 p. m.'),
    (4, 'auto', 'Hola, Ana. Tu pedido ya está listo para retirar hoy, de 9 a 6. Te esperamos.', '9:00 a. m.'),
    (4, 'ana', 'paso a las 11', '9:06 a. m.'),
    (4, 'laura', 'Perfecto, te lo dejo en caja a tu nombre.', '9:08 a. m.'),
    (4, 'ana', 'ya lo tengo, quedó divino', '11:20 a. m.'),
    (4, 'laura', '¡Qué alegría! Cualquier cosa, escríbenos por aquí mismo.', '11:22 a. m.'),
    (5, 'camp', CAMP2, '6:00 p. m.'),
    (5, 'ana', '2', '6:03 p. m.'),
    (5, 'auto', 'Te paso con Laura, que ya te conoce.', '6:03 p. m.'),
    (5, 'laura', '¡Hola otra vez, Ana! ¿Te muestro lo nuevo en azul, como la vez pasada?', '6:05 p. m.'),
    (5, 'ana', 'sí! mándame lo que tengas', '6:06 p. m.'),
]
# Separadores de día: van antes del mensaje con ese índice
DIAS = {0: 'Hoy', 18: 'Sábado', 23: 'Un mes después'}
# Capítulos (sección 3.3): título y bajada
CAPS = [
    ('Sale la campaña', 'El mismo mensaje les llega a los 100.'),
    ('Alguien responde', 'Respuesta automática y pase a una persona.'),
    ('Te atiende una persona', 'Laura resuelve dudas y aparta el pedido.'),
    ('Se cierra la venta', 'Pago, confirmación y aviso de retiro.'),
    ('Vuelve a comprar', 'La campaña siguiente la reconoce.'),
]
# Índice del mensaje donde espera Ana: tras él corre el cronómetro de 15 minutos
ESPERA_TRAS = 8

# ───────── Ritmo ─────────
REVEAL = 400        # lo que tarda una burbuja en abrirse
FADE_IN, FADE_OUT = 250, 150   # cambios de texto (.vx)
RAMP = 300          # capítulos y pasos del embudo
SEP_LEAD = 600      # del separador de día / inicio de capítulo al primer mensaje
TAIL = 3500         # cuánto queda quieta la última burbuja antes de reiniciar


def lectura(texto):
    """Tiempo para leer una burbuja antes de que llegue la siguiente."""
    return max(1200, min(4000, 850 + 22 * len(texto)))


def respuesta(quien):
    return {'ana': 350, 'auto': 250, 'laura': 450, 'camp': 300}[quien]


def timeline():
    t = [0] * len(GUION)
    ini = [0] * len(CAPS)
    dia_t = {0: 0}
    espera = {}
    for i, (cap, quien, texto, _) in enumerate(GUION):
        if i == 0:
            t[i] = SEP_LEAD
            continue
        prev_cap, _, prev_txt, _ = GUION[i - 1]
        base = t[i - 1] + lectura(prev_txt)
        if i - 1 == ESPERA_TRAS:
            # Ana pregunta y nadie contesta: aparece el aviso, corre el cronómetro y salta la alerta
            w = t[i - 1] + 700
            c0 = w + 450
            pasos = [c0 + k * 220 for k in range(1, 16)]
            alerta = pasos[-1] + 120
            espera = {'caja': w, 'pasos': pasos, 'alerta': alerta}
            base = alerta + 2200
        if cap != prev_cap:
            ini[cap - 1] = base
            if i in DIAS:
                dia_t[i] = base
            t[i] = base + SEP_LEAD
        elif i in DIAS:
            dia_t[i] = base
            t[i] = base + SEP_LEAD
        else:
            t[i] = base + respuesta(quien) - 300
    D = t[-1] + lectura(GUION[-1][2]) + TAIL
    D = int(round(D / 100.0)) * 100
    return t, ini, dia_t, espera, D


T, INI, DIA_T, ESPERA, D = timeline()


def pct(ms):
    v = ms / D * 100
    s = ('%.3f' % v).rstrip('0').rstrip('.')
    return s + '%'


# ───────── Keyframes ─────────
KF = []  # cuerpos de @keyframes, el índice es el número dmN


def kf(stops):
    """stops: lista de (ms, 'decl'); devuelve el nombre dmN. Se ordena y se quitan duplicados exactos."""
    out, last = [], None
    for ms, decl in stops:
        p = '0%' if ms <= 0 else ('100%' if ms >= D else pct(ms))
        if last is not None and p == last[0]:
            if decl == last[1]:
                continue
            raise SystemExit('keyframe con dos valores en %s (%s): %r vs %r' % (p, len(KF), last[1], decl))
        out.append((p, decl))
        last = (p, decl)
    vals = [float(p[:-1]) for p, _ in out]
    if vals != sorted(vals):
        raise SystemExit('keyframes fuera de orden en dm%d: %r' % (len(KF), out))
    KF.append(''.join('%s{%s}' % s for s in out))
    return 'dm%d' % (len(KF) - 1)


H_MSG = 'max-height:0;opacity:0;transform:translateY(8px)'


def S_MSG(h):
    return 'max-height:%dpx;opacity:1;transform:none' % h


def reveal(t, h=420, hide=None, hide_dur=400):
    st = [(0, H_MSG)]
    if t > 0:
        st.append((t, H_MSG))
    st.append((t + REVEAL, S_MSG(h)))
    if hide is not None:
        st += [(hide, S_MSG(h)), (hide + hide_dur, H_MSG), (D, H_MSG)]
    else:
        st.append((D, S_MSG(h)))
    return kf(st)


def swaps(entries, fin=FADE_IN, fout=FADE_OUT):
    """entries: [(inicio_ms, ...)] ordenados; cada uno se ve desde su inicio hasta el siguiente.
    Devuelve un nombre de keyframes por entrada."""
    names = []
    for k, e in enumerate(entries):
        a = e[0]
        b = entries[k + 1][0] if k + 1 < len(entries) else None
        if b is not None and b - a < fin + 50:
            raise SystemExit('cambios demasiado juntos: %r' % (entries,))
        if a <= 0:
            st = [(0, 'opacity:1')]
        else:
            st = [(0, 'opacity:0'), (a, 'opacity:0'), (a + fin, 'opacity:1')]
        if b is None:
            st.append((D, 'opacity:1'))
        else:
            st += [(b, 'opacity:1'), (b + fout, 'opacity:0'), (D, 'opacity:0')]
        names.append(kf(st))
    return names


def esc(s):
    return html.escape(s, quote=False)


def escq(s):
    return html.escape(s, quote=True)


# ───────── Chat ─────────
chat = []
ana_ult = max(i for i, g in enumerate(GUION) if g[1] == 'ana')
for i, (cap, quien, texto, hora) in enumerate(GUION):
    if i in DIAS:
        n = reveal(DIA_T[i])
        chat.append('<div class="cw dmv" style="animation-name:%s"><div class="wa-day">%s</div></div>' % (n, esc(DIAS[i])))
    n = reveal(T[i])
    if quien == 'ana':
        tm = hora + (' · Entregado' if i == ana_ult else '')
        burbuja = '<div class="wm me">%s<span class="tm">%s</span></div>' % (esc(texto), esc(tm))
    else:
        if quien == 'camp':
            nm = '<span class="nm">Campaña · %s</span>' % ('Promo de la semana' if cap == 1 else 'Novedades')
        elif quien == 'auto':
            nm = '<span class="nm">Automático</span>'
        else:
            nm = '<span class="nm hu">Laura · Tu Negocio</span>'
        burbuja = '<div class="wm th">%s%s<span class="tm">%s</span></div>' % (nm, esc(texto), esc(hora))
    chat.append('<div class="cw dmv" style="animation-name:%s">%s</div>' % (n, burbuja))

# Hora de la barra de estado: una por mensaje
st_names = swaps([(0 if i == 0 else T[i], g[3]) for i, g in enumerate(GUION)])
st_spans = ''.join('<span class="dmv" style="animation-name:%s">%s</span>' % (n, esc(GUION[i][3].split(' ')[0]))
                   for i, n in enumerate(st_names))

# ───────── Capítulos ─────────
OFF_BG, ON_BG = 'background-color:rgba(255,255,255,0)', 'background-color:rgba(255,255,255,.62)'
N_OFF = 'background-color:rgba(255,255,255,0);border-color:rgba(28,33,41,.14);color:#7D838D'
N_CUR = 'background-color:#1C2129;border-color:#1C2129;color:#fff'
N_DONE = 'background-color:#E4ECE7;border-color:#E4ECE7;color:#3F6652'
caps_html, now_spans = [], []
for k, (tit, baj) in enumerate(CAPS):
    a = INI[k]
    b = INI[k + 1] if k + 1 < len(CAPS) else None
    # barra
    st = [(0, 'width:0')]
    if a > 0:
        st.append((a, 'width:0'))
    st += [(b, 'width:100%'), (D, 'width:100%')] if b else [(D, 'width:100%')]
    bar = kf(st)
    # fondo del botón
    st = [(0, OFF_BG)] + ([(a, OFF_BG)] if a > 0 else []) + [(a + RAMP, ON_BG)]
    st += [(b, ON_BG), (b + RAMP, OFF_BG), (D, OFF_BG)] if b else [(D, ON_BG)]
    bg = kf(st)
    # número
    st = [(0, N_OFF)] + ([(a, N_OFF)] if a > 0 else []) + [(a + RAMP, N_CUR)]
    st += [(b, N_CUR), (b + RAMP, N_DONE), (D, N_DONE)] if b else [(D, N_CUR)]
    num = kf(st)
    caps_html.append(
        '          <li><button type="button" class="dmv" data-ini="%d" aria-label="Capítulo %d: %s" style="animation-name:%s">'
        '<span class="n dmv" style="animation-name:%s">%d</span><span class="tx"><b>%s</b><small>%s</small>'
        '<span class="bar"><i class="dmv" style="animation-name:%s"></i></span></span></button></li>'
        % (a, k + 1, escq(tit), bg, num, k + 1, esc(tit), esc(baj), bar))
for k, n in enumerate(swaps([(INI[k], c) for k, c in enumerate(CAPS)])):
    now_spans.append('<span class="dmv" style="animation-name:%s">%d de %d<b>%s</b></span>' % (n, k + 1, len(CAPS), esc(CAPS[k][0])))

# ───────── Bandeja: registro y franja en vivo ─────────
REG = [
    (T[0] + 300, '18:02', 'Campaña "Promo de la semana" enviada a 100 clientes.'),
    (T[0] + 2600, '18:03', '95 entregados.'),
    (T[2], '18:04', 'Ana respondió 1: se le envió la promo automáticamente.'),
    (T[4], '18:05', 'Pidió una persona: asignada a Laura.'),
    (T[5], '18:09', 'Laura tomó la conversación con el resumen a la vista.'),
    (T[6], '18:10', 'Le interesan 2 unidades en azul.'),
    (ESPERA['alerta'], '18:26', '15 minutos sin respuesta: te avisamos.'),
    (T[11], '18:28', 'Laura apartó 2 unidades: pasa a En atención.'),
    (INI[3], '19:02', '10 respondieron en la primera hora.'),
    (T[14], '19:31', 'Ana envió la referencia de pago.'),
    (T[15], '19:33', 'Pago recibido. Venta: $72.'),
    (T[18], 'Sáb 09:00', 'Recordatorio de retiro enviado.'),
    (T[21], 'Sáb 11:20', 'Pedido retirado en la tienda.'),
    (T[22] + 1400, 'Sáb 18:00', 'Grupo "Compraron en la promo": 3 clientes.'),
    (T[23] + 300, '18:00', 'Campaña "Novedades" enviada a 100.'),
    (T[25], '18:03', 'Ana respondió: vuelve con Laura, ya la atendió antes.'),
    (T[26], '18:05', 'Laura le muestra lo nuevo en azul.'),
]
assert all(REG[k][0] < REG[k + 1][0] for k in range(len(REG) - 1)), 'el registro tiene que ir en orden'
assert REG[-1][0] < D and REG[13][0] < INI[4], 'el grupo tiene que armarse antes de la campaña siguiente'
tick_entries = [(0, 'Campaña lista para salir a 100 clientes…')] + [(r[0], r[2]) for r in REG]
tick_spans = ''.join('<span class="dmv" style="animation-name:%s">%s</span>' % (n, escq(tick_entries[k][1]))
                     for k, n in enumerate(swaps(tick_entries)))
log_items = []
for r in reversed(REG):  # lo nuevo arriba
    n = reveal(r[0], h=120)
    log_items.append('              <li class="cw dmv" style="animation-name:%s"><span class="ln"><span>%s</span>%s</span></li>'
                     % (n, esc(r[1]), escq(r[2])))

# ───────── Bandeja: ficha ─────────
pill_e = [(0, 'Automático', 'ai'), (T[4], 'Laura', ''), (T[23], 'Automático', 'ai'), (T[25], 'Laura', '')]
pill = ''.join('<span class="dmv%s" style="animation-name:%s">%s</span>' % (' ' + e[2] if e[2] else '', n, e[1])
               for e, n in zip(pill_e, swaps(pill_e)))

OFF = 'border-top-color:#E9ECEF;color:#A9AEB6'
ON = 'border-top-color:#A9C0B2;color:#A9AEB6'
CUR = 'border-top-color:#3F6652;color:#1C2129'
PASOS = ['Enviado', 'Respondió', 'En atención', 'Venta']
# (ms, índice del paso actual o -1 para reiniciar)
EMBUDO = [(T[0], 0), (T[1], 1), (T[11], 2), (T[15], 3), (T[23], 0), (T[24], 1), (T[26], 2)]
steps_html = []
for s, nombre in enumerate(PASOS):
    est = lambda cur: CUR if s == cur else (ON if s < cur else OFF)
    st, prev = [(0, OFF)], OFF
    for ms, cur in EMBUDO:
        nuevo = est(cur)
        st += [(ms, prev), (ms + RAMP, nuevo)]
        prev = nuevo
    st.append((D, prev))
    steps_html.append('<li class="dmv" style="animation-name:%s">%s</li>' % (kf(st), nombre))

CAMPOS = [
    ('Campaña', [(0, '—'), (T[0], 'Promo de la semana'), (T[23], 'Novedades')]),
    ('Respondió', [(0, '—'), (T[1], '1 · ver promo'), (T[4], 'Pidió a una persona'), (T[23], '—'), (T[24], '2 · con Laura')]),
    ('Interés', [(0, '—'), (T[6], '2 unidades, azul'), (T[26], 'Lo nuevo, en azul')]),
    ('Entrega', [(0, '—'), (T[10], 'Retiro en tienda, sábado'), (T[21], 'Retirado')]),
    ('Atiende', [(0, '—'), (T[1], 'Automático'), (T[4], 'Laura'), (T[23], 'Automático'), (T[25], 'Laura')]),
    ('Valor', [(0, '—'), (T[7], '$72'), (T[23], 'Antes: $72')]),
]
campos_html = []
for nombre, ent in CAMPOS:
    spans = ''.join('<span class="dmv%s" style="animation-name:%s">%s</span>' % (' no' if e[1] == '—' else '', n, esc(e[1]))
                    for e, n in zip(ent, swaps(ent)))
    campos_html.append('              <div><dt>%s</dt><dd class="vx">%s</dd></div>' % (nombre, spans))

# ───────── Aviso de los 15 minutos ─────────
crono_e = [(0, '0:00')] + [(ms, '%d:00' % (k + 1)) for k, ms in enumerate(ESPERA['pasos'])]
crono = ''.join('<span class="dmv" style="animation-name:%s">%s</span>' % (n, e[1])
                for e, n in zip(crono_e, swaps(crono_e, fin=120, fout=100)))
caja = reveal(ESPERA['caja'], h=80, hide=T[ESPERA_TRAS + 1])
alerta = reveal(ESPERA['alerta'], h=90, hide=T[ESPERA_TRAS + 1])

# ───────── HTML ─────────
PLAY = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.6-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z"/></svg>'
BLOQUE = '''    <!-- demo:inicio · lo genera tools/gen_demo.py, no editar a mano -->
    <input type="checkbox" class="dm-go" id="dmGo" aria-label="Reproducir o pausar la demo">
    <div class="demo" id="dm" data-dur="{D}">
      <div class="dm-ctl">
        <ol class="dm-caps" id="dmCaps">
{caps}
        </ol>
        <div class="dm-bar">
          <button type="button" class="js-only" id="dmPrev" aria-label="Capítulo anterior"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg></button>
          <label class="pp" for="dmGo" aria-hidden="true"><span class="i-play">{play}</span><span class="i-pause"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1.2"/><rect x="14" y="5" width="4" height="14" rx="1.2"/></svg></span></label>
          <button type="button" class="js-only" id="dmNext" aria-label="Capítulo siguiente"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg></button>
          <p class="dm-now"><span class="vx">{now}</span></p>
          <p class="dm-hint js-only">Toca un capítulo para saltar.</p>
        </div>
        <p class="dm-tick" aria-hidden="true"><b class="live">Tu bandeja</b><span class="vx">{tick}</span></p>
      </div>

      <figure class="dm-ph">
        <div class="wa-chat" role="group" aria-label="Teléfono de la clienta: conversación de ejemplo por mensaje de texto con Tu Negocio">
          <div class="ph-scr">
            <div class="ph-st"><span class="vx">{st}</span><span aria-hidden="true"><svg width="17" height="11" viewBox="0 0 17 11" fill="#111B21"><rect x="0" y="7" width="3" height="4" rx="1"/><rect x="4.5" y="5" width="3" height="6" rx="1"/><rect x="9" y="2.5" width="3" height="8.5" rx="1"/><rect x="13.5" y="0" width="3" height="11" rx="1"/></svg><svg width="24" height="12" viewBox="0 0 24 12" fill="none"><rect x=".5" y=".5" width="20" height="11" rx="3" stroke="#111B21" opacity=".4"/><rect x="2" y="2" width="15" height="8" rx="1.8" fill="#111B21"/><path d="M22 4v4" stroke="#111B21" stroke-width="1.6" stroke-linecap="round" opacity=".4"/></svg></span></div>
            <div class="ph-h">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>
              <span class="av s">TN</span>
              <div><b>Tu Negocio</b><small>Mensaje de texto</small></div>
            </div>
            <div class="ph-msgs" aria-hidden="true">
{chat}
            </div>
            <div class="ph-in" aria-hidden="true"><span>Mensaje de texto</span><i><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg></i></div>
            <label class="dm-poster" for="dmGo" aria-hidden="true"><span>{play}</span><b>Ver la conversación</b></label>
          </div>
        </div>
        <figcaption class="small">Ejemplo ilustrativo<span class="dm-down"> · abajo, lo que ves tú ↓</span></figcaption>
      </figure>

      <div class="ui glass dm-panel" role="group" aria-label="Tu bandeja: la ficha de la clienta se llena sola mientras conversa">
        <div class="win">
          <div class="ui-bar"><span style="display:flex;align-items:center"><span class="lights"><i></i><i></i><i></i></span><b>Tu bandeja</b></span><small class="live">En vivo</small></div>
          <div class="ui-body" aria-hidden="true">
            <div class="dm-who"><span class="dm-av"><span>AM</span></span><div><b>Ana Méndez</b><small>+•• ••• ••• ••21 · SMS</small></div><span class="vx dm-pill">{pill}</span></div>
            <ol class="dm-steps">{steps}</ol>
            <dl class="dm-f">
{campos}
            </dl>
            <div class="dm-avisos">
              <div class="cw dmv" style="animation-name:{caja}"><div class="dm-wait"><span>Ana espera respuesta</span><b class="vx">{crono}</b></div></div>
              <div class="cw dmv" style="animation-name:{alerta}"><div class="alert"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#E2D6C3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>Ana lleva 15 minutos sin respuesta. Te avisamos.</div></div>
            </div>
            <ol class="dm-log">
{log}
            </ol>
          </div>
        </div>
      </div>
    </div>
    <!-- demo:fin -->'''

bloque = BLOQUE.format(
    D=D, caps='\n'.join(caps_html), play=PLAY, now=''.join(now_spans), tick=tick_spans, st=st_spans,
    chat='\n'.join('              ' + c for c in chat), pill=pill, steps=''.join(steps_html),
    campos='\n'.join(campos_html), caja=caja, alerta=alerta, crono=crono, log='\n'.join(log_items))

css = ['/* demo:inicio */',
       '/* Generado por tools/gen_demo.py: %d capítulos, %d mensajes, %s s */' % (len(CAPS), len(GUION), ('%.1f' % (D / 1000)).rstrip('0').rstrip('.')),
       '.dmv{animation-duration:%dms;animation-timing-function:linear;animation-iteration-count:infinite;animation-fill-mode:both;animation-play-state:paused}' % D,
       '@media (prefers-reduced-motion:reduce){.dmv{animation-duration:%dms!important;animation-delay:0s!important;animation-iteration-count:infinite!important}}' % D]
css += ['@keyframes dm%d{%s}' % (k, body) for k, body in enumerate(KF)]
css.append('/* demo:fin */')

# ───────── Chequeos ─────────
import re
usados = re.findall(r'animation-name:(dm\d+)', bloque)
assert len(usados) == len(set(usados)) == len(KF), 'cada keyframe se usa una sola vez (%d usados, %d definidos)' % (len(usados), len(KF))
assert bloque.count('class="wm ') == 28, 'tienen que ser 28 burbujas'
assert bloque.count('class="wa-day"') == 3
assert bloque.count('data-ini=') == 5
assert len(REG) + 1 == len(tick_entries) == 18 and len(log_items) == 17
assert all(len(m[2]) <= 160 for m in GUION if m[1] == 'camp'), 'las campañas caben en un SMS'
assert all(T[k] < T[k + 1] for k in range(len(T) - 1))
assert INI == sorted(INI) and INI[0] == 0

with open(os.path.join(OUT, 'demo_block.html'), 'w', encoding='utf-8') as f:
    f.write(bloque)
with open(os.path.join(OUT, 'demo_block.css'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(css))
with open(os.path.join(OUT, 'demo_timing.json'), 'w', encoding='utf-8') as f:
    json.dump({'dur': D, 'capitulos': [{'ini': INI[k], 'titulo': c[0]} for k, c in enumerate(CAPS)],
               'mensajes': [{'t': T[k], 'cap': g[0], 'quien': g[1], 'texto': g[2]} for k, g in enumerate(GUION)],
               'dias': {GUION[k][3]: v for k, v in DIA_T.items()}, 'espera': ESPERA,
               'registro': [{'t': r[0], 'hora': r[1], 'texto': r[2]} for r in REG],
               'keyframes': len(KF)}, f, ensure_ascii=False, indent=1)

print('demo: %d ms, %d keyframes (dm0…dm%d), capítulos en %s' % (D, len(KF), len(KF) - 1, INI), file=sys.stderr)
