# Arquitectura de contenido · Landing de mensajería masiva + CRM

Fase 1 (este documento): qué se queda, qué se reescribe y qué se va. `index.html` NO se toca en esta fase.
Base analizada: `index.html` del commit `6e22a7f` (320 KB, 2.172 líneas; GSAP 3.13 y ScrollTrigger van minificados e inline en las líneas 1929 y 1941).

---

## 1. Posicionamiento

**Le escribes a todos tus clientes con un solo mensaje y atiendes, uno por uno, a los que te responden.**
Mensajería masiva por texto, una bandeja para tu equipo y la ficha de cada cliente, en un solo lugar.

Ejemplo central (se repite en hero, demo y calculadora): *tienes 100 clientes: les llega el mismo mensaje a los 100 de forma automática y tú atiendes en persona al que responde.*

---

## 2. Nombre de marca

**Recomendado: Pulso** (validado). Funciona porque dice lo que hace el servicio: le tomas el pulso a tu base con cada campaña y mantienes un ritmo de contacto. Es corto, se pronuncia igual en cualquier país hispano y no está atado a ningún mercado.

- Alternativa de respaldo: **Recado** (la palabra de toda la vida para "mensaje que alguien te hace llegar"; cálida, pero suena más a mensajería de paquetes).
- Pendiente antes de publicar: revisar disponibilidad de dominio y de marca registrada. "Pulso" es un nombre común y puede estar tomado en algún país.
- En el HTML: `C&Co` aparece en `<title>`, en la barra (`.mark`) y en el footer. Decisión pendiente para Christian: reemplazarlo por "Pulso" o dejar "Pulso · por C&Co".

---

## 3. Mapa sección por sección

Convención: **MANTENER** = queda igual · **REESCRIBIR** = misma estructura y maquinaria, copy/datos nuevos · **ELIMINAR** = se va.
El tono de toda la página pasa de "ustedes" a **"tú"** (le hablamos a quien tiene el negocio): "Deslicen" → "Desliza", "Toquen" → "Toca", "Hagan sus números" → "Calcula tu alcance".

### 3.0 `<head>`, comentario de identidad y barra (líneas 1–23 y 982–999)
- `<title>` → **REESCRIBIR**: `Pulso · Mensajería masiva y atención personalizada`.
- Comentario de identidad (líneas 15–23): **REESCRIBIR** la línea "Números de ejemplo coherentes…" (habla de 300 → 100 → 24 reservas) por la cadena nueva: *100 clientes → 95 les llega → 10 responden → 3 compran*. El resto (paleta, vidrio, tipografías, imprimible) se **MANTIENE**.
- `meta robots noindex`: hoy tiene sentido (era una propuesta privada). Para una landing pública hay que quitarlo. **Decisión pendiente** de Christian.
- Barra: **REESCRIBIR** etiquetas: "WhatsApp" (`.nav-demo .lbl`) → **"Demo"**; "El sistema" → **"Cómo funciona"**; "El panel" → **"Resultados"**; "Cómo funciona" (`#logica`) → **"Por dentro"**; "Inversión" → **"Empezar"** (o se quita, ver 3.8); "Sus números" → **"Tu alcance"**; botón "Empezar" se mantiene. `aria-label="Ver la demo de WhatsApp"` → "Ver la demo".

### 3.1 HERO · `.stk-hero` (--i:0) → **REESCRIBIR copy y las 3 escenas; MANTENER la maquinaria** (sticky, desvanecido con ScrollTrigger, loop de 16,5 s, versión CSS sin JS `hx-*`)
- Pastilla `.for`: "Propuesta para Tibisay Hoteles, piloto en Canaima" → **"Mensajería masiva + atención personalizada"**.
- **Titular:** *Un mensaje para todos. Atención para cada uno.*
- **Lead:** *Envía tu promoción a toda tu base de clientes de una sola vez, por mensaje de texto. Cuando alguien responde, lo atiende una persona de tu equipo, y cada conversación queda en la ficha del cliente.*
- `.journey` (3 pasos): 1 *Escribes un mensaje y le llega a todos* · 2 *Responden y los atiendes uno a uno* · 3 *Cierras la venta y sabes qué campaña funcionó*.
- Botones: "Empezar con el diagnóstico" → **"Quiero mi primera campaña"**; "Ver el WhatsApp en acción" → **"Ver una campaña en acción"**.
- Escenas del `#stage` (mismas clases `s-ad / s-chat / s-deal`, mismo timing):
  - `s-ad` (hoy: post de Instagram con botón "Enviar mensaje por WhatsApp") → **redactor de campaña**: tarjeta con el texto del mensaje, contador "142/160 caracteres", destinatarios "Todos tus clientes · 100" y botón **"Enviar a 100"** (el `press` del JS sigue apretando el botón).
  - `s-chat` (hoy: chat del asistente con chips de fechas) → **respuestas que llegan**: 3 burbujas de clientes distintos ("1", "¿Hay en otro color?", "2") y chips extraídos: *Quiere ver la promo* · *Pide hablar con alguien* · *Asignado a Laura*.
  - `s-deal` (hoy: tablero "Reservas de diciembre", Familia Rondón, "$4,38 de pauta por mensaje · $42 por reserva") → **tablero de la campaña**: columnas *Respondió / En atención / Venta*, tarjeta que avanza *"Ana M. · 2 unidades · $72"*, y franja inferior *"Campaña Promo de la semana · 100 enviados · 10 respondieron · 3 ventas"*.
- `aria-label` del stage: reescribir describiendo las 3 escenas nuevas. `figcaption` "Ejemplo ilustrativo" se mantiene.

### 3.2 PROBLEMA · (--i:1), puntos `#dots` → **REESCRIBIR** (mismo mecanismo de puntos + toggle `.seg`)
- **Titular:** *Tienes la lista. Lo difícil es llegarle a todos.*
- **Copy:** *Escribirle a cada cliente uno por uno no escala: en una tarde llegas a unos pocos y los demás ni se enteran de tu promoción. Con un envío masivo le llega a toda tu base al mismo tiempo.*
- Puntos: de **300 a 100** (un punto = un cliente). Hay que cambiar las 300 `<i>` estáticas del HTML (copia para sin-JS) y el bucle `for (i < 300)` del JS.
- Toggle `.seg`: "Hoy" / "Meta del piloto" → **"Uno por uno"** / **"Con Pulso"**.
  - Uno por uno: se iluminan ~15 puntos → `bigN` "15 *de 100*", texto: *Lo que alcanzas a escribir a mano en una tarde. Los otros 85 no se enteran.*
  - Con Pulso: se iluminan los 100 (los ~10 que responden en otro tono) → "100 *de 100*", texto: *A todos les llega el mismo mensaje. Los que responden pasan a tu bandeja para atenderlos en persona.*
- Botón "Hagan sus números" → **"Calcula tu alcance"**. Párrafo `.nojs` ("Meta del piloto: 24 de 300…") → reescribir con la versión "Con Pulso".
- Se elimina la referencia a "la reunión del 9 de octubre", "$1.000 al mes en pauta", "300 mensajes", "6 reservas".

### 3.3 DEMO · `#demo` (--i:2) → **REESCRIBIR contenido y piel visual; MANTENER la maquinaria** (checkbox `#dmGo` como play sin JS, capítulos con salto, panel sincronizado, autoplay por IntersectionObserver, `prefers-reduced-motion`)
- Tag: "Fase 2 · WhatsApp comercial, en acción" → **"La demo · una campaña de principio a fin"**.
- **Titular:** *Así se ve una campaña.*
- **Copy:** *Un mismo mensaje sale a tus 100 clientes. Arriba, el teléfono de una clienta que responde; abajo, lo que ves tú al mismo tiempo. Lo automático lo decides tú, y cualquier conversación la puede tomar una persona cuando quiera.*
- **Capítulos (5)**: 1 *Sale la campaña* — "El mismo mensaje les llega a los 100." · 2 *Alguien responde* — "Respuesta automática y pase a una persona." · 3 *Te atiende una persona* — "Laura resuelve dudas y aparta el pedido." · 4 *Se cierra la venta* — "Pago, confirmación y aviso de retiro." · 5 *Vuelve a comprar* — "La campaña siguiente la reconoce."
- **Piel SMS neutra (obligatorio, hoy todo grita WhatsApp):**
  - Cabecera del chat `#075E54` (verde WhatsApp) → color de marca neutro (p. ej. `--ink` o `--mist-ink`); nombre del remitente **"Tu Negocio"**; subtítulo "en línea" → **"Mensaje de texto"**. Sin "escribiendo…" (`dm60/dm61`): el SMS no lo muestra.
  - Burbujas: saliente del cliente `#D9FDD3` → gris/azul neutro (`--mist-bg`); entrante blanca se mantiene. Quitar el doble check azul (`#53BDEB`) → texto pequeño **"Entregado"** solo en el último mensaje propio.
  - Fondo con trama `radial-gradient` color arena → fondo liso claro.
  - **Eliminar** los 9 indicadores de escritura `.wm.typ`, los bloques `.wa-btns` (los botones de respuesta rápida no existen en SMS: se responde con "1" / "2"), `.wa-ref` (tarjeta del anuncio) y las dos `.wa-img` (comprobante y foto de Canaima).
  - Las clases internas `wa-*` pueden quedarse (no se ven); lo que se ve no puede decir ni parecer WhatsApp.
- **Panel lateral** (`.dm-panel`) → título **"Tu bandeja"**:
  - `.dm-who`: "Nuevo contacto" → "Ana Méndez", teléfono "+•• ••• ••• ••21 · SMS"; pastilla "Asistente"/"Andreína" → **"Automático" / "Laura"**.
  - `.dm-steps`: Nuevo / Calificado / Cotizado / Confirmada → **Enviado / Respondió / En atención / Venta**.
  - `.dm-f` (6 campos): Vino de / Fechas / Personas / Habitación / Ventana 24 h / Valor → **Campaña** (Promo de la semana → Novedades) · **Respondió** (— → "1 · ver promo" → "Pidió a una persona") · **Interés** (2 unidades, azul) · **Entrega** (Retiro en tienda, sábado) · **Atiende** (Automático → Laura) · **Valor** ($72 → "Antes: $72").
  - Aviso `.dm-wait` + `.alert` (cronómetro 0:00→15:00 y "Avisamos a gerencia"): **MANTENER** la mecánica, reescribir a *"Ana espera respuesta"* / *"Ana lleva 15 minutos sin respuesta. Te avisamos."* (sacar "gerencia").
  - `.dm-log` y `.dm-tick` (18 líneas cada uno, deben coincidir): reescribir, por ejemplo: *Campaña "Promo de la semana" enviada a 100 clientes.* · *95 entregados.* · *Ana respondió 1: se le envió la promo automáticamente.* · *Pidió una persona: asignada a Laura.* · *10 respondieron en la primera hora.* · *15 minutos sin respuesta: te avisamos.* · *Laura apartó 2 unidades: pasa a En atención.* · *Pago recibido. Venta: $72.* · *Recordatorio de retiro enviado.* · *Grupo "Compraron en la promo": 3 clientes.* · *Campaña "Novedades" enviada a 100.* · *Ana respondió: vuelve con Laura, ya la atendió antes.*
- **AVISO TÉCNICO IMPORTANTE:** el bloque `<!-- demo:inicio … demo:fin -->` (HTML) y los `@keyframes dm0…dm162` (CSS, líneas 581–748) los genera `propuesta/demo-whatsapp.mjs`, que **no está en este repo** (solo hay `index.html`). Con 28 mensajes de texto (hoy son 19 de texto + 9 de "escribiendo") cambia todo el timing: `data-dur="57500"`, los `data-ini` de cada capítulo, los `dmNN` de horas (`.ph-st`), log, ticker y campos. Opciones para la fase 2: (a) recuperar el generador y adaptarlo, o (b) escribir un generador nuevo (script) que emita HTML+keyframes. **No reescribir a mano 160 keyframes.**

### 3.4 POR QUÉ VALE LA PENA · (--i:3) `.facts` → **REESCRIBIR** (2 de 3 datos son hoteleros/Meta)
- **Titular:** *Por qué funciona.*
- **Copy:** *Tres ideas simples detrás de cada campaña.*
- Fichas:
  - **7×** — *más probable concretar una venta cuando a quien pregunta se le responde en menos de una hora.* **MANTENER** la fuente (Oldroyd y otros, HBR 2011): es genérica, no hotelera.
  - **100 de 100** — *Un mensaje de texto le llega a cualquier teléfono, sin apps ni cuentas. Nadie se queda fuera de tu promoción.* (dato de producto, sin fuente externa).
  - **1 ficha** — *por cliente: lo que compró, lo que preguntó y quién lo atendió. La próxima campaña ya sabe a quién le habla.* (dato de producto).
- **ELIMINAR**: "15–25% cobran las agencias en línea por reserva" (Sojern, Hospitalitynet) y "−10% costo por venta… anuncios de WhatsApp" (Meta 2024).
- Regla: cualquier cifra de industria nueva (tasas de apertura de SMS, etc.) solo entra con fuente verificable enlazada. No inventar porcentajes.

### 3.5 SISTEMA · `#sistema` (--i:4), 3 `.phase` → **REESCRIBIR** (mismas 3 tarjetas apiladas y sus animaciones `data-play`; fuera las horas)
- **Titular:** *Tres piezas, un mismo lugar.* · **Copy:** *Así se ven las pantallas que usa tu equipo. Los datos son de ejemplo.*
- **Eliminar en las tres** los `<p class="price">` ("32 horas · 1 a 2 semanas", "72 horas · unas 3 semanas", "24 horas · 1 semana") y la palabra "Fase".
- **1 · Envío masivo** (tag "Envía") — *Un mensaje, toda tu base, en minutos.*
  - *Escribes el mensaje una vez y eliges a quién: todos o un grupo.* · *Cada mensaje lleva el nombre del cliente.* · *Programas el día y la hora.* · *Quien responde BAJA no vuelve a recibir.*
  - Pantalla (tabla `.camp`): título "Anuncios · Canaima" → **"Campañas · último mes"**; columnas Campaña / Enviados (barra) / Respuestas / Ventas; filas de ejemplo: *Promo de la semana*, *Novedades*, *Recordatorio de pago*, *Saludo genérico* (esta última en rojo: muchas entregas, cero ventas). `.tip`: *"Saludo genérico" no vendió nada: la próxima vez manda una oferta concreta, como en "Promo de la semana".*
- **2 · Bandeja y atención personalizada** (tag "Atiende") — *Nadie que responde se queda esperando.*
  - *Todas las respuestas llegan a una bandeja para tu equipo.* · *Las respuestas simples ("1", "2") se contestan solas; lo demás pasa a una persona.* · *Cada conversación tiene un responsable.* · *Si alguien lleva 15 minutos sin respuesta, te avisamos.* · *Cada contacto queda registrado y el sistema te dice cuándo volver a escribir.*
  - Pantalla (`.inbox`, `data-play="inbox"`, cronómetro 13:40→15:00 y alerta): **MANTENER** la animación; nombres nuevos y textos: *"Resumen: 2 unidades, retira el sábado"* / *"¿Tienen envío a domicilio?"* / *"Automático: ¿qué te gustaría ver?"*; pastillas "Reserva tentativa" → **"Por pagar"**, "Calificando" → **"Automático"**. Link "Ver la conversación completa ↑" se mantiene.
- **3 · Tu base de clientes (CRM)** (tag "Recuerda") — *El que ya te compró es el más fácil de que vuelva.*
  - *Importas tu lista de clientes en minutos.* · *Grupos listos: quién compró, quién preguntó y no compró, quién no responde hace tiempo.* · *Cada campaña nueva se arma con un grupo, sin saturar a nadie.*
  - Pantalla (`data-play="guests"`): "Vinieron en diciembre 2025 · 23 huéspedes" → **"Compraron en la última promo"**; filas con *"2 compras · cliente desde marzo"* en vez de "4 personas · 3 noches"; botón "Enviar a 23" → **"Enviar al grupo"** y el JS cambia "23 enviados · 5 ya respondieron" por **"Enviado · 2 ya respondieron"** (sin cifras de clientes reales).

### 3.6 PANEL DE GERENCIA · `#panel` (--i:5), bento → **REESCRIBIR**; rescatar 5 de 6 fichas, **ELIMINAR el calendario**
- **Titular:** *Lo que pasó con cada campaña.* · **Copy:** *Cuántos recibieron, cuántos respondieron y cuántos compraron. Datos de ejemplo de una campaña a 100 clientes.*
- **Sankey** (`#sankey`, `.c12`) → **RESCATABLE como embudo de campaña.** Columnas: *100 enviados → 10 respondieron → 3 compraron*. Los "anuncios" del array `ads` pasan a **grupos de la base**: *Clientes frecuentes · Compraron hace meses · Preguntaron y no compraron · Nuevos*. Leyenda: "$42 de pauta por reserva" → **"x de cada y respondió"**. Insight: *Los clientes frecuentes responden el doble: la próxima promo, empieza por ellos.* (Ajustar la `aria-label` y la copia estática del SVG para sin-JS).
- **Heatmap** (`#heat`, `.c7`) → **RESCATABLE como "A qué hora responden".** Misma rejilla 7×24 y recuadro "equipo atendiendo". Insight nuevo: *La mayoría responde entre las 6 y las 9 de la noche. Programa tus envíos para esa hora, o deja lo automático contestando cuando tu equipo no está.* Quitar "Ahí contesta el asistente".
- **"Cuánto va a entrar"** (`.c5`, `fc`) → **RESCATABLE como "Ventas de la campaña"**: *Cobrado / En conversación / Meta*; probabilidades *Respondió 10% · En atención 50% · Pagó 100%*. Sin la meta "$12.000 de diciembre": usar cifras chicas coherentes con 100 clientes.
- **Calendario "Fechas que piden"** (`#cal`, `.c12`) → **ELIMINAR** completo: HTML, el bloque JS "Calendario de demanda" (líneas 1776–1800) y el CSS `.cal*` / `.calx*` (líneas ~290–304) y su regla sin-JS (`html:not(.js) .cal .day`, `.calx-day`). Es 100% hotelero (cupo, temporada, viajero de afuera).
- **"Por qué se pierden"** (`.c7`, `lost`) → **RESCATABLE como "Por qué no compraron"**: *Precio* (decisión del cliente) · *No era el momento* (se puede mover) · *Dejó de contestar* (se puede mover) · *Ya lo tenía* · *No le interesó*. Insight: *Casi la mitad no compró por cosas que sí puedes mover: el momento y el seguimiento.*
- **"Cuántos toques hacen falta"** (`.c5`, `touch`) → **RESCATABLE como "Seguimiento"**: cadena *Mensaje (−) → Llamada (−) → Mensaje (+)*; quitar "WhatsApp" de las píldoras y de la `aria-label`.
- Al quitar el calendario el bento queda: c12 (Sankey) / c7+c5 (heat + ventas) / c7+c5 (motivos + seguimiento). Cuadra sin huecos.

### 3.7 LÓGICA · `#logica` (--i:6) → **REESCRIBIR** (mismo `.flow` de 6 nodos, el lazo `.loop` y las 6 fichas `.expert`)
- **Titular:** *Por dentro.* · **Copy:** *Lo que no se ve, pero hace que cada envío llegue y cada respuesta tenga dueño.*
- Nodos: 1 *Tu lista* — Subes tus clientes; limpiamos duplicados y números mal escritos. · 2 *La campaña* — Mensaje, grupo y hora; sale a todos a la vez. · 3 *Las respuestas* — Llegan a una sola bandeja, ordenadas por cliente. · 4 *Reglas* — Contesta lo simple, asigna una persona y vigila los 15 minutos. · 5 *La ficha* — Campaña, conversación y venta, en el mismo cliente. · 6 *La próxima campaña* — Con lo aprendido, sabes a quién escribirle y cuándo.
- `.loop-cap`: *El ciclo se cierra: **cada campaña te enseña quién compra**, no solo quién lee.*
- Fichas `.expert`:
  - *Lista limpia* — Cada número se revisa antes de enviar: sin duplicados ni formatos rotos.
  - *Nadie recibe dos veces* — Cada envío tiene su identificador; si algo se reintenta, no se repite.
  - *Baja con una palabra* — Quien responde BAJA sale de la lista al instante y no vuelve a recibir.
  - *Cada contacto cuenta* — Cada intento queda en la ficha: si respondió o no, el primero, el último y cuándo toca volver a escribir.
  - **¿Y por WhatsApp?** — *WhatsApp no está hecho para envíos masivos: si mandas lo mismo a muchos desde tu número, te lo pueden bloquear. Por eso la campaña sale por mensaje de texto, que le llega a cualquier teléfono, y tu WhatsApp queda tranquilo.* ← **ÚNICA mención de WhatsApp en toda la página.**
  - *Tus clientes son tuyos* — Tu lista vive en tu cuenta, con accesos por persona. La exportas cuando quieras.
- `.honest` ("con pocas reservas al mes, Meta aprende más lento…") → reescribir: *Una nota honesta: el envío masivo hace que te lean; lo que vende es responder rápido y bien. Por eso la bandeja importa tanto como el envío.*

### 3.8 INVERSIÓN · `#inversion` (--i:7) → **REESCRIBIR** como **"Cómo empezamos"** (sin horas)
- **Titular:** *Tu primera campaña, en tres pasos.* · **Copy:** *Sin instalaciones ni contratos largos. Empezamos con tu lista y una campaña real.*
- La tabla (Etapa / Semanas / Horas, total 144 h) se reconvierte en pasos: *1 Subes tu lista* · *2 Escribimos juntos el primer mensaje* · *3 Lo envías y atiendes desde la bandeja*. Sin columna de horas ni semanas.
- `.terms` ("Se cobra la hora trabajada", "tope de 15%", "50% al empezar", "pauta a Meta") → **ELIMINAR** y reemplazar por condiciones del servicio. **Precios y modelo de cobro: decisión pendiente de Christian; no inventar cifras.** Placeholder sugerido: *"Pagas por lo que envías. Sin cobro por cada persona de tu equipo."* solo si se confirma.

### 3.9 CÓMO TRABAJAMOS · (--i:8) `.how` → **REESCRIBIR**
- **Titular:** *Cómo te acompañamos.*
- Fichas: ~~Horas a la vista~~ → *Te enseñamos a usarlo* (tu equipo aprende con tu primera campaña) · *Entrega probada* → *Pruebas antes de enviar* (te mandas el mensaje a ti primero) · *Equipo capacitado* → *Tu equipo, un solo lugar* · *Sin pago por usuario* → **MANTENER** si el modelo de precios lo confirma (ver 3.8).
- Se elimina "Saben en qué se fue cada hora" y "asesoras".

### 3.10 CIERRE · `#cierre` (--i:9) → **REESCRIBIR**
- **Titular:** *Empieza con tus 100 clientes.*
- **Lead:** *Trae tu lista; en una sesión armamos tu primer mensaje y lo dejamos listo para salir.*
- `.next`: 1 *Nos cuentas qué vendes y a quién.* · 2 *Subimos tu lista y escribimos la primera campaña.* · 3 *La envías y atiendes las respuestas desde tu bandeja.*
- Botón: "Hagan sus números" → **"Calcula tu alcance"** (+ botón primario de contacto, destino por definir).

### 3.11 FOOTER → **REESCRIBIR**
- "C&Co · Propuesta para Tibisay Hoteles · Octubre 2026" → **"Pulso · Mensajería masiva y atención personalizada"**.
- "Pantallas y datos de ejemplo. Válida por 30 días." → **"Pantallas y datos de ejemplo."**

### 3.12 CALCULADORA · `dialog#calculadora` → **REESCRIBIR** (ver sección 5). Se mantiene `showModal`, cierre por clic fuera y `data-open-calc`.

### 3.13 BOTÓN FLOTANTE `#waFab` + CHAT INMERSIVO `#waOv` → **MANTENER la maquinaria, REESCRIBIR la piel**
- Se mantiene: aparición con `elastic.out` al empezar el desvanecido del hero, clon de `#dm .ph-msgs`, pausa de la demo de la página, foco/Escape/bloqueo de scroll, fallback CSS sin GSAP, pantalla completa en teléfono y panel centrado en escritorio.
- Se cambia: ícono SVG de WhatsApp → **burbuja de mensaje genérica**; color `#25D366`/`#20BD5A` y el pulso verde → color de marca; cabecera `#075E54` → la misma cabecera neutra de la demo (3.3), con "Tu Negocio" / "Mensaje de texto" en vez de "Tibisay Canaima" / "en línea"; avatar "TH" → "TN".
- `aria-label` del botón: "Probar la demo: abrir el chat de WhatsApp" → **"Probar la demo: abrir la conversación de ejemplo"**. Texto visible "Probar demo" se mantiene.

### 3.14 SCRIPTS
- **GSAP + ScrollTrigger (líneas 1919–1942): MANTENER intactos.**
- **Script de baraja/hero/FAB/chat (1943–2171): MANTENER**; solo se toca si el fix visual de la sección 7 lo requiere.
- **Script principal (1636–1917): REESCRIBIR datos**, no la estructura: hero (sin cambios de timing), puntos (100 y textos nuevos), Sankey (`ads` → grupos), heatmap (texto de `heatIns`), **eliminar** el bloque del calendario, `inbox`/`guests` (textos), calculadora (`impact()` nueva). La demo (`demo = …`) no cambia salvo que el generador cambie IDs.
- Se MANTIENEN: `prefers-reduced-motion` (CSS y JS), versión sin JS (`html:not(.js)`, `.nojs`, `.js-only`, hero con keyframes `hx-*`, demo con checkbox), impresión (`beforeprint`).

---

## 4. Guion de la conversación simulada (28 mensajes)

Remitente en pantalla: **Tu Negocio** (mensaje de texto). Clienta: **Ana**. Persona del equipo: **Laura**. Los mensajes automáticos se marcan con la etiqueta `.nm` "Automático"; los de Laura con "Laura · Tu Negocio" (clase `.nm.hu`). Sin botones, sin "escribiendo…", sin imágenes: se responde con números o con texto. Los mensajes de campaña caben en 160 caracteres (un SMS).

**Capítulo 1 · Sale la campaña** — *Hoy, 6:02 p. m.*
1. NEGOCIO (campaña) → Hola, Ana. Esta semana tienes 20% en tu próxima compra. Responde 1 para ver qué entra o 2 para hablar con alguien. BAJA para no recibir más.
2. CLIENTE → 1
3. NEGOCIO (automático) → ¡Listo! Esto es lo que entra en la promo: tunegocio.com/promo. Si algo te gusta, respóndeme aquí.
4. CLIENTE → me gusta el segundo. lo tienen en otro color?
5. NEGOCIO (automático) → Buena pregunta para Laura. Ya te la paso, te escribe en un momento.

**Capítulo 2 · Te atiende una persona** — *6:09 p. m.*
6. NEGOCIO (Laura) → Hola, Ana, soy Laura. Sí: lo tenemos en azul y en gris. ¿Cuál prefieres?
7. CLIENTE → azul. y si llevo dos, el descuento es para los dos?
8. NEGOCIO (Laura) → Sí, el 20% va en cada uno. Los dos te quedan en $72 en vez de $90.
9. CLIENTE → perfecto. hacen envíos?
10. NEGOCIO (Laura) → Sí, a domicilio, o lo retiras en la tienda sin costo. ¿Qué te queda mejor?
11. CLIENTE → lo retiro el sábado
12. NEGOCIO (Laura) → Hecho. Te los aparto a tu nombre hasta el sábado. ¿Cómo prefieres pagar?
13. CLIENTE → transferencia
14. NEGOCIO (Laura) → Te paso los datos en el siguiente mensaje. Cuando pagues, mándame el número de referencia y lo dejo confirmado.

**Capítulo 3 · Se cierra la venta** — *7:31 p. m.*
15. CLIENTE → listo, ya transferí. referencia 004821
16. NEGOCIO (Laura) → ¡Recibido, Ana! Pedido confirmado: 2 unidades en azul, $72, retiro el sábado.
17. CLIENTE → gracias Laura!!
18. NEGOCIO (Laura) → A ti. El sábado en la mañana te escribimos para recordártelo.

**Capítulo 4 · El día del retiro** — *Sábado, 9:00 a. m.*
19. NEGOCIO (automático) → Hola, Ana. Tu pedido ya está listo para retirar hoy, de 9 a 6. Te esperamos.
20. CLIENTE → paso a las 11
21. NEGOCIO (Laura) → Perfecto, te lo dejo en caja a tu nombre.
22. CLIENTE → ya lo tengo, quedó divino
23. NEGOCIO (Laura) → ¡Qué alegría! Cualquier cosa, escríbenos por aquí mismo.

**Capítulo 5 · Vuelve a comprar** — *Un mes después, 6:00 p. m.*
24. NEGOCIO (campaña) → Hola, Ana. Llegó lo nuevo y nuestros clientes lo ven primero. Responde 1 para verlo o 2 para hablar con Laura. BAJA para no recibir más.
25. CLIENTE → 2
26. NEGOCIO (automático) → Te paso con Laura, que ya te conoce.
27. NEGOCIO (Laura) → ¡Hola otra vez, Ana! ¿Te muestro lo nuevo en azul, como la vez pasada?
28. CLIENTE → sí! mándame lo que tengas

Notas de implementación:
- 28 burbujas de texto = mismas 28 `.wm` que hoy, pero sin los 9 `.typ`: la demo dura más. Estimado ~65–75 s; el generador recalcula `data-dur` y los `data-ini`.
- Separadores `.wa-day`: "Hoy" · "Sábado" · "Un mes después".
- Los mensajes 1 y 24 llevan pie pequeño (`.ft`) solo si se decide sacar "BAJA" del cuerpo; recomendación: dejarlo en el cuerpo (así es un SMS real).
- La demo muestra a **una** clienta; el panel y el ticker muestran que el mismo mensaje salió a 100 y que respondieron 10 (eso cuenta "masivo + personalizado").

---

## 5. Calculadora reconvertida · "Calcula tu alcance"

Misma ventana `dialog#calculadora`, mismas 3 filas de 2 campos (`.row2`) y mismas 4 tarjetas `.kpi` + texto `#o-txt`.

- **Título** (`#calcT`): *Calcula tu alcance.*
- **Copy:** *Cambia los números por los tuyos. Los porcentajes son supuestos, no promesas: los afinamos con tu primera campaña.*

**Inputs (6):**

| Campo | Valor por defecto | Notas |
|---|---|---|
| Clientes en tu base | 100 | número entero |
| Campañas al mes | 1 | |
| Les llega (%) | 95 | números que reciben el mensaje |
| Responden (%) | 10 | de los que les llega |
| Compran de los que responden (%) | 30 | depende de la atención |
| Venta promedio (USD) | 40 | |

**Outputs (4 KPI + frase):**

| KPI | Fórmula | Con el ejemplo de 100 clientes |
|---|---|---|
| Les llega | clientes × campañas × entrega | **95** mensajes |
| Te responden | les llega × respuesta | **9,5** conversaciones para atender |
| Ventas al mes *(destacada)* | responden × cierre | **2,9** ventas |
| Ingreso al mes *(destacada)* | ventas × venta promedio | **$114** (≈ $1.368 al año) |

- `#o-txt`: *Con estos supuestos, cada campaña a tus 100 clientes abre unas 10 conversaciones y cierra unas 3 ventas: unos $114 al mes. Sube la frecuencia o mejora la respuesta y mira cómo cambia.* Si ventas = 0: *Con estos supuestos no sale ninguna venta. Prueba subiendo cuántos responden.*
- Formato numérico `es-VE` (como hoy, función `fmt`/`f1`).
- Fuera: "Pauta al mes", "Pauta por reserva", "Cierre hoy/meta", "Más mensajes, misma pauta", "Valor por reserva", el título "De 300 mensajes y 6 reservas, a cuánto".
- Opcional (fase posterior, solo si hay precio definido): campo "Costo por mensaje" y KPI "Ingreso por cada $1 enviado". No mostrar costos inventados.

---

## 6. Strings y conceptos a eliminar sí o sí

Verificación final: un `grep -i` de cada término sobre `index.html` debe devolver **0 resultados** (excepto la línea honesta de WhatsApp, que debe aparecer **exactamente 1 vez**).

**Marca y lugar del cliente anterior:** Tibisay, Tibisay Hoteles, tibisayhoteles, Tibisay Canaima, "TH" (avatar), Canaima, Salto Ángel, Laguna (fin de semana), Puerto Ordaz, Ciudad Bolívar, avioneta, "Propuesta para", "piloto", "Válida por 30 días", "Octubre 2026", "reunión del 9 de octubre".

**Hotelería:** hotel, hoteles, huésped/huéspedes, reserva/reservas/reservan, habitación (familiar), cupo, noches, "2 adultos y un niño", temporada (en sentido hotelero), "viajero de afuera", "otro destino", "Paquete Salto Ángel", "Paquete familia", "Fechas que piden", "calendario de demanda", "Lista de espera", "Hospedado", "Tentativa", "Cotizado/Cotización" (en el sentido de reserva).

**Personas del caso anterior:** Andreína, Carolina Rondón, Familia Rondón, María Rondón, José Pérez, Carla, Luisa Guerra, Carlos Medina, Ana Velásquez, Ricardo Salas, "asesora(s)", "gerencia".

**Publicidad / Meta:** Meta, Instagram, anuncio(s), pauta, "Publicidad", "Enviar mensaje por WhatsApp", "Vino del anuncio", "Venta enviada a Meta", "firma de Meta", "la pauta aprende", "huella del clic", "Promo genérica" (como campaña de anuncios).

**WhatsApp (todo, salvo la línea honesta de 3.7):** WhatsApp (en copy, `aria-label`, nav, tags, títulos), ícono SVG de WhatsApp, `#25D366`, `#20BD5A`, `#075E54`, `#D9FDD3`, `#53BDEB` (doble check), "en línea", "escribiendo…", "Ventana 24 h", "plantilla aprobada", "WhatsApp comercial", botones de respuesta rápida, tarjeta de anuncio referido.

**Cifras del caso anterior:** "300" (mensajes y puntos), "6 de 300", "24 de 300", "100 cotizados", "24 reservas", "$1.000 al mes", "$4,38", "$4,48", "$3,55", "$9,55", "$42 por reserva", "$52", "$28", "$210", "$1.140", "$570", "$1.320", "$640", "$1.980", "$9.600", "$1.700", "$12.000", "$700", "23 huéspedes", "47 personas", "19 aceptaron otra fecha", "64%" (si sale de los datos hoteleros), "15–25%", "−10%", "$400 por reserva".

**Horas y forma de cobro anterior:** "32 horas", "72 horas", "24 horas", "16 horas", "144 h", "1 a 2 semanas", "unas 3 semanas", "6–7 semanas", "Una semana y 16 horas", "Se cobra la hora trabajada", "tarifa especial", "tope de 15%", "50% al empezar y 50% al entregar", "Horas a la vista", "en qué se fue cada hora", "Fase 1 / Fase 2 / Fase 3", "Diagnóstico" (como etapa cobrada).

**Visualización:** calendario de diciembre completo (HTML + JS + CSS) y cualquier texto con "diciembre".

**Restricciones de nicho:** la landing no puede mencionar ningún mercado concreto (ni el anterior ni ningún otro). Ejemplos solo con "tu negocio", "tus clientes", "tu tienda", "pedido", "unidades".

---

## 7. Criterios de aceptación del fix visual de la baraja

Contexto técnico (cómo funciona hoy): cada `.stk` es `position:sticky; top: calc(96px + i×14px)`; cada sección (menos el hero) tiene `max-height: calc(100dvh − 112px)`, `overflow-y:auto`, fondo `rgba(255,255,255,.94)` y, al quedar cubierta, el JS le aplica `scale` hasta 0,90 (origen arriba al centro) y un velo `.deck-shade` hasta 0,22 de opacidad. El filo visible de cada tarjeta recogida son ~14 px.

Causas probables del "texto fantasma" que el fix tiene que cerrar:
- **Fondo translúcido (.94):** el 6% de transparencia deja ver el texto de las tarjetas de abajo.
- **Scroll interno no reiniciado:** si el usuario bajó dentro de una tarjeta, el filo de 14 px muestra texto de la mitad del contenido, no el margen superior.
- **Margen superior justo:** con `padding-top:16px` y escala 0,9, el filo de 14 px deja ~15,6 px de contenido: cualquier tag, ascendente o sombra que suba un poco se asoma.
- **Altura que no cabe:** en 390×844 la tarjeta 9 arranca en 222 px y puede medir hasta 732 px → su final queda debajo de la pantalla y no se puede alcanzar con el scroll interno.

**Criterios (todos se verifican en 390×844 y en 1280×900, Chromium, con movimiento normal):**

1. **Filo limpio.** Con cada tarjeta i (1…8) totalmente recogida (P[i] = 1), la franja visible entre su borde superior y el borde superior de la tarjeta i+1 muestra solo fondo y borde: **cero glifos**. Prueba: ningún rectángulo de texto (`Range.getClientRects()` de los nodos de texto de la tarjeta i) se cruza con esa franja; y en la captura, la franja tiene varianza de color por fila menor a un umbral (solo degradado, sin trazos).
2. **Sin transparencia.** Ninguna tarjeta deja ver contenido de otra a través de su fondo: fondo efectivamente opaco (alfa 1) en todo el alto de la tarjeta. Prueba: con la tarjeta i+1 encima, una captura de su zona superior no cambia si se oculta (`visibility:hidden`) el contenido de la tarjeta i.
3. **Filo mínimo y parejo.** Todos los filos de la pila miden lo mismo (±1 px) y no más de 14 px en 390×844 (puede ser igual o algo mayor en 1280×900). La pila completa nunca tapa el titular de la tarjeta activa.
4. **Scroll interno controlado.** Al recogerse una tarjeta, lo que asoma es su cabecera (margen superior), aunque el usuario haya bajado dentro de ella. Al desplegarla (scroll hacia arriba) vuelve a verse completa, sin perder el contenido.
5. **Todo alcanzable.** Para cada tarjeta, `top_i + altura_visible_i ≤ alto de la ventana`: el final de cada tarjeta (incluido el cierre `--i:9` y su botón) se alcanza con el scroll interno o el de la página, en ambas resoluciones.
6. **Sin saltos.** Al bajar y al subir a velocidad normal y con fling: ninguna tarjeta cambia de posición o escala de golpe (diferencia entre frames consecutivos ≤ 2 px de `top` y ≤ 0,01 de escala, salvo el movimiento propio del scroll). Sin layout shift medible fuera del área que se desplaza (CLS ≈ 0). En 390×844, ocultar/mostrar la barra del navegador no hace rebotar la pila (el JS ya ignora cambios de alto < 150 px; la `max-height` en `dvh` tampoco debe provocar reflujo visible).
7. **Velo sobrio.** El oscurecido de las tarjetas recogidas no ensucia el filo: el filo se lee como borde claro, no como franja gris sucia (velo ≤ 0,22 y, si hace falta, que no cubra los 14 px superiores).
8. **Hero.** El hero termina de desvanecerse antes de que la tarjeta 1 lo cubra a la mitad; no queda texto del hero asomando detrás de la pila, y no recibe toques cuando está desvanecido (ya existe con `pointer-events`).
9. **Reversible.** Al subir hasta arriba del todo, todas las tarjetas quedan con `transform` vacío, velo en 0 y sin clase `.deck` (estado idéntico al de carga).
10. **Sin regresiones.** Con `prefers-reduced-motion: reduce` no hay baraja ni desvanecido (flujo normal). Sin JS, la página se lee completa (apilado solo CSS, hero estático). Al imprimir, todo en estado final. El botón flotante sigue apareciendo al empezar el desvanecido y el chat inmersivo abre, pausa la demo y cierra con Escape.

Método de verificación sugerido: Playwright con `/opt/meta-chromium/chrome` en headless (`--headless=new --no-sandbox --no-zygote --disable-gpu --disable-dev-shm-usage`), sirviendo el archivo con `context.route('**/*')` bajo un host falso (Chrome bloquea `127.0.0.1`) y respondiendo Google Fonts con vacío. Capturas en cada punto de recogida (P[i] = 1) de las 9 tarjetas, en ambas resoluciones, más una pasada de scroll continuo midiendo `getBoundingClientRect` por frame.

---

## 8. Resumen

1. La página se queda con toda su maquinaria (baraja, hero, demo animada, chat inmersivo, botón flotante, calculadora, movimiento reducido y sin-JS) y cambia todo su contenido hotelero por un servicio de mensajería masiva por texto + bandeja + CRM, con la marca **Pulso**.
2. La idea que atraviesa toda la página es una sola: *100 clientes reciben el mismo mensaje automático y una persona atiende a los que responden*; la demo de 28 mensajes la cuenta con Ana y Laura en 5 capítulos.
3. Se reescriben 10 de 10 tarjetas, se rescatan Sankey, heatmap, ventas, motivos y seguimiento como métricas de campaña, y se elimina el calendario; fuera horas, precios del caso anterior, Meta y cualquier nicho.
4. WhatsApp desaparece de la piel y del copy (verdes, checks, "en línea", botones rápidos) y queda solo una línea honesta que explica por qué la campaña sale por texto.
5. Riesgo principal de la fase 2: el generador `demo-whatsapp.mjs` no está en el repo; hay que recuperarlo o reescribirlo antes de tocar la demo, y el fix de la baraja se acepta solo con los 10 criterios de la sección 7 medidos en 390×844 y 1280×900.
