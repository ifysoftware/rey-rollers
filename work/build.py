#!/usr/bin/env python3
"""Genera el sitio estático de Rey Roller's en ../site.

  - Datos de productos: work/data/products.json
  - Fotos por producto: photos/<slug>/*.jpg|png|webp  (se optimizan solas al construir)
  - Salida: site/index.html y site/productos/<slug>/index.html
"""
import base64, io, json, os, shutil, glob
from html import escape
from urllib.parse import quote
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
WORK = os.path.join(ROOT, "work")
PHOTOS = os.path.join(ROOT, "photos")
WA = "56995628622"


def wa(msg): return f"https://wa.me/{WA}?text={quote(msg)}"
def rd(p): return open(p, encoding="utf8").read()


# ---------------------------------------------------------------- fotos de producto
def process_photos(slug, listed=()):
    """Devuelve [(grande, miniatura, w, h)] con rutas relativas a site/.
    Las fotos salen del campo `photos` del producto (las sube el cliente desde /admin y quedan en
    site/uploads/); si está vacío, se usan las de la carpeta photos/<slug>/. El orden del panel se respeta."""
    src = [os.path.join(SITE, p.lstrip("/")) for p in listed if os.path.isfile(os.path.join(SITE, p.lstrip("/")))]
    ordered = bool(src)
    if not src:
        src = sorted(f for ext in ("jpg", "jpeg", "png", "webp", "avif")
                     for f in glob.glob(os.path.join(PHOTOS, slug, f"*.{ext}")))
    out_dir = os.path.join(SITE, "assets", "img", "products", slug)
    if os.path.isdir(out_dir): shutil.rmtree(out_dir)
    res = []
    if not src: return res
    os.makedirs(out_dir)
    for i, f in enumerate(src, 1):
        im = Image.open(f).convert("RGB")
        big = im.copy(); big.thumbnail((1400, 1400), Image.LANCZOS)
        small = im.copy(); small.thumbnail((520, 520), Image.LANCZOS)
        big.save(os.path.join(out_dir, f"{i}.webp"), quality=78, method=6)
        small.save(os.path.join(out_dir, f"{i}-s.webp"), quality=72, method=6)
        res.append((f"assets/img/products/{slug}/{i}.webp", f"assets/img/products/{slug}/{i}-s.webp", big.width, big.height))
    return res


# ---------------------------------------------------------------- piezas
SPRITE = '''<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
    <symbol id="i-chev-l" viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></symbol>
    <symbol id="i-chev-r" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></symbol>
    <symbol id="i-ruler" viewBox="0 0 24 24"><path d="M3 17 17 3l4 4L7 21z"/><path d="M7 13l2 2M10 10l2 2M13 7l2 2"/></symbol>
    <symbol id="i-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></symbol>
    <symbol id="i-wrench" viewBox="0 0 24 24"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></symbol>
    <symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></symbol>
    <symbol id="i-awning" viewBox="0 0 24 24"><path d="M3 9l2-5h14l2 5H3z"/><path d="M3 9v1a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0V9"/><path d="M5 14v7M19 14v7"/></symbol>
    <symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6l-8-3z"/><path d="M9 12l2 2 4-4"/></symbol>
    <symbol id="i-home" viewBox="0 0 24 24"><path d="M3 11 12 3l9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></symbol>
    <symbol id="i-building" viewBox="0 0 24 24"><path d="M4 21V4h10v17"/><path d="M14 9h6v12"/><path d="M8 8h2M8 12h2M8 16h2M17 13v.01M17 17v.01"/></symbol>
    <symbol id="i-factory" viewBox="0 0 24 24"><path d="M3 21V11l6 4v-4l6 4V5h3v10h3v6H3z"/><path d="M7 18h.01M12 18h.01M17 18h.01"/></symbol>
    <symbol id="i-truck" viewBox="0 0 24 24"><path d="M1 6h13v10H1zM14 10h4l3 3v3h-7"/><circle cx="5.5" cy="18.5" r="1.8"/><circle cx="17.5" cy="18.5" r="1.8"/></symbol>
    <symbol id="i-wa" viewBox="0 0 24 24"><path d="M3 21l1.6-4.7A8.5 8.5 0 1 1 8 19.5L3 21z"/><path d="M9 9.2c.4 2.2 2.6 4.4 4.8 4.8l1.2-1.2a.8.8 0 0 1 1.1 0l1 .8a.8.8 0 0 1 .1 1.1 3.4 3.4 0 0 1-2.8 1.2 8.2 8.2 0 0 1-6.3-6.3 3.4 3.4 0 0 1 1.2-2.8.8.8 0 0 1 1.1.1l.8 1a.8.8 0 0 1 0 1.1z"/></symbol>
    <symbol id="i-ig" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5v.01"/></symbol>
    <symbol id="i-fb" viewBox="0 0 24 24"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8z"/></symbol>
    <symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></symbol>
    <symbol id="i-phone" viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></symbol>
    <symbol id="i-star" viewBox="0 0 24 24"><path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z" fill="currentColor" stroke="none"/></symbol>
    <symbol id="i-check" viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7"/></symbol>
  </defs>
</svg>'''

SEAL = '''<svg class="seal" viewBox="0 0 140 140" role="img" aria-label="Sello de garantía: 3 años">
          <defs><path id="seal-ring" d="M70,70 m-47,0 a47,47 0 1,1 94,0 a47,47 0 1,1 -94,0"/></defs>
          <circle cx="70" cy="70" r="67" fill="#FA6801"/>
          <circle cx="70" cy="70" r="61" fill="none" stroke="#0B0B0C" stroke-width="1.4" stroke-dasharray="2 3.2"/>
          <circle cx="70" cy="70" r="38" fill="#0B0B0C"/>
          <text font-family="Plus Jakarta Sans, sans-serif" font-size="11" font-weight="800" fill="#0B0B0C" letter-spacing="1.5"><textPath href="#seal-ring" textLength="292" lengthAdjust="spacing">GARANTÍA OFICIAL • REY ROLLER'S •</textPath></text>
          <text x="70" y="82" text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif" font-size="38" font-weight="800" fill="#fff">3</text>
          <text x="70" y="97" text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif" font-size="10" font-weight="800" fill="#FA6801" letter-spacing="2.4">AÑOS</text>
        </svg>'''

LOADER = '''<!-- LOADING: solo el isotipo, 2 s. Funciona con CSS; el JS solo libera el scroll. -->
<div class="loader" id="loader" aria-hidden="true">
  <div class="loader__inner">
    <img class="loader__mark" src="assets/isotipo-white.svg" alt="" width="86" height="130">
    <span class="loader__bar"><i></i></span>
  </div>
</div>'''


def vcut(kind):
    """Cortes en V. dark-top / cream-top: valle o cima al inicio de una sección. dark-bottom: el banner entra en el hero."""
    paths = {
        "dark-top":   ('M0,4 L720,58 L1440,4 L1440,72 L0,72 Z', "#0B0B0C", "M0,4 L720,58 L1440,4", "top"),
        "cream-top":  ('M0,58 L720,4 L1440,58 L1440,72 L0,72 Z', "#F6F2EC", "M0,58 L720,4 L1440,58", "top"),
        "dark-bottom": ('M0,0 L1440,0 L1440,4 L720,58 L0,4 Z', "#0B0B0C", "M0,4 L720,58 L1440,4", "bottom"),
    }
    d, fill, line, pos = paths[kind]
    return (f'<div class="vcut vcut--{pos}" aria-hidden="true"><svg viewBox="0 0 1440 72" preserveAspectRatio="none">'
            f'<path d="{d}" fill="{fill}"/><path class="vcut__line" d="{line}"/></svg></div>')


SERVICES = [
    ("i-ruler", "Fabricación a Medida", "Confeccionamos cortinas roller (Screen, Blackout, Dúo/Noche & Día), cortinas verticales y persianas de aluminio y madera, desarrolladas según medidas exactas y requerimientos específicos de cada espacio."),
    ("i-sun", "Asesoría y Medición Técnica", "Realizamos visitas en terreno para evaluar orientación solar, niveles de privacidad y eficiencia térmica, recomendando el sistema y la tela más adecuada para cada ambiente."),
    ("i-wrench", "Instalación Profesional", "Ejecutamos instalaciones con altos estándares de alineación, fijación y terminaciones, garantizando funcionamiento preciso y presentación impecable."),
    ("i-bolt", "Automatización y Motorización", "Incorporamos sistemas motorizados y automatizados que optimizan confort y funcionalidad, permitiendo el control remoto o integración con soluciones de domótica."),
    ("i-awning", "Toldos Proyectantes", "Fabricación e instalación de sistemas de protección solar exterior, manuales o motorizados, diseñados para ampliar y proteger terrazas y espacios al aire libre."),
    ("i-shield", "Servicio Técnico y Postventa", "Mantenimiento, reparación, cambio de telas y modernización de sistemas existentes, asegurando continuidad y durabilidad en el tiempo."),
]
AREAS = [
    ("i-home", "Residencial", "Casas y departamentos: privacidad, confort térmico y una estética pensada para cada ambiente del hogar."),
    ("i-building", "Corporativo", "Oficinas, clínicas, comercios e instituciones: control de luz y deslumbramiento con una imagen profesional."),
    ("i-factory", "Industrial", "Plantas, flotas y recintos de operación: soluciones robustas y a gran escala, con instalación coordinada."),
]
CLIENTS_FEATURED = [("carozzi", "Carozzi"), ("culligan", "Culligan"), ("heal", "Heal Sport Therapy & Wellness")]
CLIENTS_MORE = [("odontologia", "Odontología Los Dominicos", "#ffffff"), ("dicaer", "Buses Dicaer", "#e5e5e5"), ("santiago", "Municipalidad de Santiago", "#005ea6")]


def pcard(p, photos, prefix, mini=False):
    slug, name = p["slug"], p["name"]
    href = f'{prefix}productos/{slug}/'
    tag = f'<span class="pcard__tag{" pcard__tag--eco" if p["group"] == "eco" else ""}">{escape(p["tag"])}</span>' if p["tag"] and not mini else ""
    if p["group"] == "more" and p["tag"]: tag = f'<span class="pcard__tag pcard__tag--new">{escape(p["tag"])}</span>'
    img = ""
    if photos:
        g, s, w, h = photos[0]
        img = f'<img src="{prefix}{s}" alt="{escape(name)} instalado por Rey Roller\'s" width="{min(w,520)}" height="{round(min(w,520)*h/w)}" loading="lazy" decoding="async">'
    cls = "pcard pcard--mini" if mini else "pcard"
    if p["group"] == "eco": cls += " pcard--eco"
    return f'''
        <article class="{cls} reveal">
          <a class="pcard__media" href="{href}" tabindex="-1" aria-hidden="true">{img}{tag}</a>
          <div class="pcard__body">
            <h3><a href="{href}">{escape(name)}</a></h3>
            <p>{escape(p["short"])}</p>
            <a class="link" href="{href}">Ver producto <svg class="ico"><use href="#i-arrow"/></svg></a>
          </div>
        </article>'''


def gallery_html(p, photos, prefix):
    if not photos:
        return ('<div class="gallery__ph"><div class="gallery__phmain"><img src="%sassets/isotipo-white.svg" alt="" width="86" height="130"><p>Fotos del producto próximamente</p></div>'
                '<div class="gallery__phrow"><span></span><span></span><span></span></div></div>' % prefix)
    g, s, w, h = photos[0]
    main = f'<div class="gallery__main"><img id="galMain" src="{prefix}{g}" alt="{escape(p["name"])}" width="{w}" height="{h}" decoding="async"></div>'
    if len(photos) == 1: return main
    th = "".join(f'<button type="button" class="{"is-on" if i == 0 else ""}" data-src="{prefix}{g_}" aria-label="Ver foto {i+1}"><img src="{prefix}{s_}" alt="" width="160" height="120" loading="lazy"></button>'
                 for i, (g_, s_, w_, h_) in enumerate(photos))
    return main + f'<div class="gallery__thumbs">{th}</div>'


import hashlib
def _h(p): return hashlib.md5(open(p,'rb').read()).hexdigest()[:8]
VER={}

def build():
    VER['css']=_h(os.path.join(SITE,'css','styles.css')); VER['js']=_h(os.path.join(SITE,'js','main.js'))
    data = json.load(open(os.path.join(WORK, "data", "products.json"), encoding="utf8"))["products"]
    photos = {p["slug"]: process_photos(p["slug"], p.get("photos") or []) for p in data}
    page = rd(os.path.join(WORK, "templates", "page.html"))
    home = rd(os.path.join(WORK, "templates", "home_main.html"))
    prod = rd(os.path.join(WORK, "templates", "product_main.html"))

    # LQIP del hero
    h = Image.open(os.path.join(SITE, "assets/img/hero/hero-640.webp")).convert("RGB").resize((24, 14), Image.LANCZOS)
    b = io.BytesIO(); h.save(b, "WEBP", quality=40)
    lqip = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()

    def mk(group, prefix="", mini=False, items=None):
        return "".join(pcard(p, photos[p["slug"]], prefix, mini) for p in (items or [x for x in data if x["group"] == group]))

    # -------- testimonios (marcadores hasta tener las reseñas reales)
    testi = "".join(f'''
          <figure class="tcard" role="group" aria-roledescription="diapositiva" aria-label="{n} de 7">
            <div class="tcard__top">
              <span class="stars" role="img" aria-label="5 estrellas">{'<svg class="ico"><use href="#i-star"/></svg>' * 5}</span>
              <span class="tcard__g"><b>G</b> Reseña en Google</span>
            </div>
            <blockquote data-placeholder>Reseña {n} de 7: aquí va el comentario real de Google del cliente, tal como fue publicado.</blockquote>
            <figcaption><span class="avatar" aria-hidden="true">{n}</span><span><b>Nombre del cliente</b><small>Cliente verificado en Google</small></span></figcaption>
          </figure>''' for n in range(1, 8))

    featured = "".join(f'''
      <li class="trust__tile trust__tile--{f}"><img src="assets/img/client-{f}.webp" alt="{n}" loading="lazy" decoding="async"></li>''' for f, n in CLIENTS_FEATURED)
    marquee = "".join(f'''
      <li class="logo-tile" style="--tile:{bg}"><img src="assets/img/client-{f}.webp" alt="{n}" height="72" loading="lazy" decoding="async"></li>''' for f, n, bg in CLIENTS_MORE)

    services = "".join(f'''
        <li class="feature reveal"><span class="feature__ico"><svg class="ico"><use href="#{i}"/></svg></span><h3>{t}</h3><p>{d}</p></li>''' for i, t, d in SERVICES)
    areas = "".join(f'''
        <article class="area reveal"><span class="area__ico"><svg class="ico"><use href="#{i}"/></svg></span><h3>{t}</h3><p>{d}</p></article>''' for i, t, d in AREAS)

    home_html = (home
        .replace("{{VCUT_BANNER}}", vcut("dark-bottom")).replace("{{VCUT_ABOUT}}", vcut("dark-top"))
        .replace("{{VCUT_PRODUCTS}}", vcut("cream-top")).replace("{{VCUT_CMP}}", vcut("dark-top"))
        .replace("{{VCUT_ECO}}", vcut("cream-top")).replace("{{VCUT_AREAS}}", vcut("dark-top"))
        .replace("{{VCUT_FIDEL}}", vcut("cream-top"))
        .replace("{{PRODUCTS_MAIN}}", mk("main")).replace("{{PRODUCTS_MORE}}", mk("more", mini=True))
        .replace("{{PRODUCTS_ECO}}", mk("eco", mini=True))
        .replace("{{SERVICES}}", services).replace("{{AREAS}}", areas)
        .replace("{{TESTIMONIALS}}", testi).replace("{{CLIENTS_FEATURED}}", featured).replace("{{CLIENTS_MARQUEE}}", marquee)
        .replace("{{LQIP}}", lqip))

    head_home = '''<link rel="preload" as="image" type="image/avif" imagesrcset="assets/img/hero/hero-640.avif 640w, assets/img/hero/hero-960.avif 960w, assets/img/hero/hero-1280.avif 1280w, assets/img/hero/hero-1600.avif 1600w, assets/img/hero/hero-2048.avif 2048w" imagesizes="100vw" fetchpriority="high">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"HomeAndConstructionBusiness","name":"Rey Roller's","slogan":"Expertos en cortinas","description":"Fabricación e instalación de cortinas roller, persianas y toldos a medida.","telephone":"+56995628622","areaServed":{"@type":"Country","name":"Chile"},"address":{"@type":"PostalAddress","addressLocality":"Santiago","addressCountry":"CL"}}
</script>'''

    def wrap(main, prefix, title, desc, body_class, loader, head_extra, wa_general, wa_visit):
        return (page.replace("{{MAIN}}", main).replace("{{TITLE}}", escape(title)).replace("{{DESC}}", escape(desc, quote=True))
                .replace("{{BODY_CLASS}}", body_class).replace("{{LOADER}}", loader).replace("{{HEAD_EXTRA}}", head_extra)
                .replace("{{SPRITE}}", SPRITE).replace("{{SEAL}}", SEAL).replace("{{VCUT_FOOT}}", vcut("dark-top"))
                .replace("{{WA_GENERAL}}", wa_general).replace("{{WA_VISITA}}", wa_visit).replace("{{V_CSS}}", VER["css"]).replace("{{V_JS}}", VER["js"]).replace("{{P}}", prefix))

    wg, wv = wa("Hola Rey Roller's, quiero cotizar un proyecto."), wa("Hola Rey Roller's, quiero agendar una visita técnica.")
    open(os.path.join(SITE, "index.html"), "w", encoding="utf8").write(
        wrap(home_html.replace("{{P}}", ""), "", "Rey Roller's — Expertos en Cortinas | Santiago, Chile",
             "Cortinas roller, persianas y toldos a medida en Santiago. Asesoría técnica, instalación profesional, motorización y 3 años de garantía. Envíos a todo Chile.",
             "page-home", LOADER, head_home, wg, wv))

    # -------- páginas de producto
    shutil.rmtree(os.path.join(SITE, "productos"), ignore_errors=True)
    for i, p in enumerate(data):
        P = "../../"
        same = [x for x in data if x["group"] == p["group"] and x["slug"] != p["slug"]]
        others = [x for x in data if x["group"] == "main" and x["slug"] != p["slug"]] if len(same) < 3 else same
        idx = next((k for k, x in enumerate(others) if data.index(x) > i), 0)
        related = [others[(idx + k) % len(others)] for k in range(min(4, len(others)))]
        m = (prod.replace("{{NAME}}", escape(p["name"])).replace("{{TAG}}", escape(p["tag"] or "Rey Roller's"))
             .replace("{{SHORT}}", escape(p["short"])).replace("{{DESCRIPTION}}", escape(p["description"]))
             .replace("{{BULLETS}}", "".join(f'<li><svg class="ico"><use href="#i-check"/></svg>{escape(x)}</li>' for x in p["bullets"]))
             .replace("{{IDEAL}}", "".join(f"<li>{escape(x)}</li>" for x in p["ideal"]))
             .replace("{{GALLERY}}", gallery_html(p, photos[p["slug"]], P))
             .replace("{{RELATED}}", "".join(pcard(r, photos[r["slug"]], P, True) for r in related))
             .replace("{{WA_PRODUCT}}", wa(f"Hola Rey Roller's, quiero cotizar: {p['name']}"))
             .replace("{{VCUT_PBODY}}", vcut("cream-top")).replace("{{P}}", P))
        out = os.path.join(SITE, "productos", p["slug"]); os.makedirs(out)
        open(os.path.join(out, "index.html"), "w", encoding="utf8").write(
            wrap(m, P, f"{p['name']} — Rey Roller's", f"{p['name']}: {p['short']} Fabricación e instalación en Santiago, envíos a todo Chile y 3 años de garantía.",
                 "page-product", "", "", wg.replace("{{P}}", P), wv))
    print("OK: index + %d productos" % len(data), "| fotos:", {k: len(v) for k, v in photos.items() if v})


if __name__ == "__main__":
    build()
