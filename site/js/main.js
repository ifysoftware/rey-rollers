/* Rey Roller's — comportamiento. Sin dependencias. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Loader (solo en el inicio): 2 s en total. El CSS lo sube solo; aquí solo se libera el scroll ---- */
  var loader = d.getElementById('loader');
  if (loader) {
    root.classList.add('is-locked');
    setTimeout(function () { root.classList.remove('is-locked'); loader.remove(); }, 2000);
  }

  /* ---- Nav: fondo al hacer scroll (el logo completo está siempre visible) ---- */
  var nav = d.getElementById('nav');
  function onScroll() { nav.classList.toggle('is-solid', window.scrollY > 24); }
  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });

  /* ---- Menú móvil ---- */
  var burger = d.getElementById('burger'), menu = d.getElementById('menu');
  function closeMenu() {
    menu.classList.remove('is-open'); burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', 'Abrir menú'); if (!loader || !d.body.contains(loader)) root.classList.remove('is-locked');
  }
  burger.addEventListener('click', function () {
    var open = menu.classList.toggle('is-open');
    burger.setAttribute('aria-expanded', open); burger.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    root.classList.toggle('is-locked', open);
  });
  menu.addEventListener('click', function (e) { if (e.target.closest('a')) closeMenu(); });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });

  /* ---- Aparición al hacer scroll ---- */
  var rev = d.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } });
    }, { threshold: .12, rootMargin: '0px 0px -6% 0px' });
    rev.forEach(function (el, i) { el.style.setProperty('--d', (i % 4) * 70 + 'ms'); io.observe(el); });
  } else { rev.forEach(function (el) { el.classList.add('in'); }); }

  /* ---- Enlace activo según sección (solo en el inicio) ---- */
  var links = [].slice.call(d.querySelectorAll('.nav__menu a[href^="#"]:not(.btn)'));
  var map = {}; links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
  if ('IntersectionObserver' in window && links.length) {
    var spy = new IntersectionObserver(function (es) {
      es.forEach(function (x) {
        if (x.isIntersecting) { links.forEach(function (a) { a.classList.remove('is-active'); }); var a = map[x.target.id]; if (a) a.classList.add('is-active'); }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(map).forEach(function (id) { var s = d.getElementById(id); if (s) spy.observe(s); });
  }

  /* ---- Comparador: la cortina baja y se compara Blackout / Sunscreen ---- */
  var cmp = d.getElementById('cmp');
  if (cmp) {
    var scene = d.getElementById('cmpScene'), knob = d.getElementById('cmpKnob'), range = d.getElementById('cmpRange'), link = d.getElementById('cmpLink');
    var tabs = cmp.querySelectorAll('.cmp__tab');
    var FAB = {
      black: { l: 0, v: 0, p: 1, name: 'Roller Blackout', href: 'productos/roller-blackout/' },
      sun: { l: 0.35, v: 0.8, p: 0.45, name: 'Roller Sunscreen', href: 'productos/roller-sunscreen/' }
    };
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var fab = 'sun', dd = 1, raf = 0, touched = false;
    var $ = function (id) { return d.getElementById(id); };
    var words = function (v, set) { for (var i = 0; i < set.length; i++) { if (v >= set[i][0]) return set[i][1]; } return set[set.length - 1][1]; };
    var W_LUZ = [[0.96, 'Toda la luz'], [0.6, 'Mucha luz'], [0.2, 'Luz filtrada'], [0.03, 'Muy poca'], [0, 'Sin luz']];
    var W_VISTA = [[0.96, 'Completa'], [0.6, 'Se mantiene'], [0.2, 'Parcial'], [0.03, 'Casi nula'], [0, 'Sin vista']];
    var W_PRIV = [[0.9, 'Máxima'], [0.3, 'Parcial'], [0.03, 'Baja'], [0, 'Ninguna']];
    function meter(key, val, W) {
      $('m' + key + 'Bar').style.setProperty('--w', Math.round(val * 100) + '%');
      $('m' + key + 'V').textContent = Math.round(val * 100) + '%';
      $('m' + key + 'T').textContent = words(val, W);
    }
    function render() {
      var f = FAB[fab];
      cmp.style.setProperty('--d', dd);
      range.value = Math.round(dd * 100);
      meter('Luz', (1 - dd) + dd * f.l, W_LUZ);
      meter('Vista', (1 - dd) + dd * f.v, W_VISTA);
      meter('Priv', dd * f.p, W_PRIV);
    }
    function stop() { if (raf) { cancelAnimationFrame(raf); raf = 0; } }
    function go(to, ms, done) {
      stop();
      if (reduce || ms <= 0) { dd = to; render(); if (done) done(); return; }
      var from = dd, t0 = performance.now();
      (function step(t) {
        var k = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - k, 3);
        dd = from + (to - from) * e; render();
        if (k < 1) raf = requestAnimationFrame(step); else { raf = 0; if (done) done(); }
      })(t0);
    }
    function touch() { touched = true; cmp.classList.add('touched'); stop(); }
    function setFab(next) {
      if (next === fab) return;
      fab = next; cmp.setAttribute('data-fabric', fab);
      tabs.forEach(function (t) { t.setAttribute('aria-pressed', t.getAttribute('data-fabric') === fab ? 'true' : 'false'); });
      link.href = FAB[fab].href; link.firstChild.nodeValue = 'Ver ' + FAB[fab].name + ' ';
      go(0, 450, function () { go(1, 1500); });   /* sube y vuelve a bajar con la tela elegida */
    }
    tabs.forEach(function (t) { t.addEventListener('click', function () { touched = true; cmp.classList.add('touched'); setFab(t.getAttribute('data-fabric')); }); });
    range.addEventListener('input', function () { touch(); dd = range.value / 100; render(); });

    /* arrastrar la manilla */
    var drag = false;
    function move(e) {
      var r = scene.getBoundingClientRect();
      dd = Math.max(0, Math.min(1, (e.clientY - r.top) / (r.height * 0.94)));
      render();
    }
    knob.addEventListener('pointerdown', function (e) { drag = true; touch(); knob.setPointerCapture(e.pointerId); e.preventDefault(); });
    knob.addEventListener('pointermove', function (e) { if (drag) move(e); });
    ['pointerup', 'pointercancel'].forEach(function (ev) { knob.addEventListener(ev, function () { drag = false; }); });
    knob.addEventListener('keydown', function (e) {
      var step = e.key === 'ArrowDown' ? 0.08 : e.key === 'ArrowUp' ? -0.08 : 0;
      if (step) { touch(); dd = Math.max(0, Math.min(1, dd + step)); render(); e.preventDefault(); }
    });

    /* al entrar en pantalla la cortina baja sola */
    render();
    if (!reduce && 'IntersectionObserver' in window) {
      dd = 0; render();
      var io = new IntersectionObserver(function (ents) {
        if (ents[0].isIntersecting) { io.disconnect(); cmp.classList.add('in'); if (!touched) setTimeout(function () { if (!touched) go(1, 2600); }, 500); }
      }, { threshold: 0.45 });
      io.observe(scene);
    } else { cmp.classList.add('in'); }
  }

  /* ---- Galería de producto ---- */
  var gal = d.querySelector('[data-gallery]');
  if (gal) {
    var big = gal.querySelector('#galMain'), btns = [].slice.call(gal.querySelectorAll('.gallery__thumbs button'));
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        big.src = b.getAttribute('data-src');
        btns.forEach(function (x) { x.classList.toggle('is-on', x === b); });
      });
    });
  }

  /* ---- Carrusel de testimonios ---- */
  var track = d.getElementById('track'), dots = d.getElementById('dots');
  if (track) {
    var cards = [].slice.call(track.children), idx = 0, timer, hover = false;
    cards.forEach(function (_, i) {
      var b = d.createElement('button'); b.type = 'button'; b.setAttribute('aria-label', 'Ir al testimonio ' + (i + 1));
      b.addEventListener('click', function () { go(i, true); }); dots.appendChild(b);
    });
    var paint = function () { [].forEach.call(dots.children, function (b, i) { b.classList.toggle('is-on', i === idx); }); };
    var go = function (i, user) {
      idx = (i + cards.length) % cards.length;
      track.scrollTo({ left: cards[idx].offsetLeft - cards[0].offsetLeft, behavior: reduce ? 'auto' : 'smooth' });
      paint(); if (user) restart();
    };
    var raf; track.addEventListener('scroll', function () {
      cancelAnimationFrame(raf); raf = requestAnimationFrame(function () {
        var x = track.scrollLeft, best = 0, bd = 1e9;
        cards.forEach(function (c, i) { var dd = Math.abs(c.offsetLeft - cards[0].offsetLeft - x); if (dd < bd) { bd = dd; best = i; } });
        if (best !== idx) { idx = best; paint(); }
      });
    }, { passive: true });
    d.getElementById('prev').addEventListener('click', function () { go(idx - 1, true); });
    d.getElementById('next').addEventListener('click', function () { go(idx + 1, true); });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(idx + 1, true); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(idx - 1, true); }
    });
    var restart = function () { clearInterval(timer); if (!reduce) timer = setInterval(function () { if (!hover && !d.hidden) go(idx + 1); }, 6000); };
    ['mouseenter', 'focusin', 'touchstart'].forEach(function (ev) { track.addEventListener(ev, function () { hover = true; }, { passive: true }); });
    ['mouseleave', 'focusout', 'touchend'].forEach(function (ev) { track.addEventListener(ev, function () { hover = false; }, { passive: true }); });
    paint(); restart();
  }

  /* ---- Carrusel de logos: se repite lo necesario para llenar el ancho y hacer el bucle ---- */
  var logos = d.getElementById('logos');
  if (logos && !reduce) {
    var base = [].slice.call(logos.children);
    for (var r = 0; r < 4; r++) base.forEach(function (li) { logos.appendChild(li.cloneNode(true)); });
    [].slice.call(logos.children).slice(base.length).forEach(function (li) { li.setAttribute('aria-hidden', 'true'); var im = li.querySelector('img'); im.alt = ''; });
    var all = [].slice.call(logos.children);
    all.forEach(function (li) { logos.appendChild(li.cloneNode(true)); });
    [].slice.call(logos.children).slice(all.length).forEach(function (li) { li.setAttribute('aria-hidden', 'true'); li.querySelector('img').alt = ''; });
  }

  var y = d.getElementById('year'); if (y) y.textContent = new Date().getFullYear();
})();
