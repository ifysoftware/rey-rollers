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

  /* ---- Comparador Blackout / Sunscreen ---- */
  var cmp = d.getElementById('cmp'), range = d.getElementById('cmpRange');
  if (cmp && range) {
    var touch = function () { cmp.classList.add('touched'); };
    range.addEventListener('input', function () { cmp.style.setProperty('--pos', range.value + '%'); touch(); });
    ['pointerdown', 'keydown', 'touchstart'].forEach(function (ev) { range.addEventListener(ev, touch, { passive: true }); });
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
