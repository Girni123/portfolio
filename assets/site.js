/* portfolio.girnstein.studio – kleine Interaktionen, ohne Bibliotheken */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  // Header bekommt Hintergrund beim Scrollen
  var header = document.querySelector('.header');
  function onScroll() { header.classList.toggle('is-scrolled', window.scrollY > 40); }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Mobiles Menü
  var toggle = document.querySelector('.menu-toggle');
  var menu = document.getElementById('menu');
  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
    menu.hidden = !open;
    document.body.style.overflow = open ? 'hidden' : '';
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !menu.hidden) toggle.click();
  });

  // Text einfliegen: Überschriften mit data-split wortweise animieren
  if (!reduce) {
    document.querySelectorAll('[data-split]').forEach(function (el) {
      var i = 0;
      (function walk(node) {
        Array.prototype.slice.call(node.childNodes).forEach(function (child) {
          if (child.nodeType === 3) {
            var frag = document.createDocumentFragment();
            child.textContent.split(/(\s+)/).forEach(function (part) {
              if (!part) return;
              if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
              var outer = document.createElement('span');
              outer.className = 'split-word';
              var inner = document.createElement('span');
              inner.style.setProperty('--i', i++);
              inner.textContent = part;
              outer.appendChild(inner);
              frag.appendChild(outer);
            });
            node.replaceChild(frag, child);
          } else if (child.nodeType === 1 && child.tagName !== 'BR') {
            if (child.classList.contains('accent')) {
              var wrap = document.createElement('span');
              wrap.className = 'split-word';
              child.parentNode.replaceChild(wrap, child);
              child.style.setProperty('--i', i++);
              wrap.appendChild(child);
            } else walk(child);
          }
        });
      })(el);
      el.setAttribute('aria-label', el.textContent.replace(/\s+/g, ' ').trim());
    });
  }

  // Sanftes Einblenden beim Scrollen
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('is-in'); });
  }

  // Uhrzeit Köln
  var clock = document.querySelector('.clock');
  if (clock) {
    var fmt = new Intl.DateTimeFormat('de-DE', { hour: '2-digit', minute: '2-digit', second: '2-digit', timeZone: 'Europe/Berlin' });
    var tick = function () { clock.textContent = fmt.format(new Date()); };
    tick();
    setInterval(tick, 1000);
  }

  // Filter auf /work/
  var filter = document.querySelector('.filter');
  if (filter) {
    var cards = document.querySelectorAll('.page--wide .grid .card');
    var apply = function (key, push) {
      filter.querySelectorAll('.filter__btn').forEach(function (b) {
        b.setAttribute('aria-pressed', String(b.dataset.filter === key));
      });
      cards.forEach(function (c) {
        c.hidden = !(key === 'all' || c.dataset.cat === key);
        if (!c.hidden) c.classList.add('is-in');
      });
      if (push) history.replaceState(null, '', key === 'all' ? location.pathname : '#' + key);
    };
    filter.addEventListener('click', function (e) {
      var b = e.target.closest('.filter__btn');
      if (b) apply(b.dataset.filter, true);
    });
    var initial = location.hash.slice(1);
    if (initial === 'tech' || initial === 'creative') apply(initial, false);
  }

  // YouTube erst nach Klick laden (Datenschutz)
  document.querySelectorAll('.video[data-yt]').forEach(function (box) {
    box.querySelector('.video__play').addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + box.dataset.yt + '?autoplay=1&rel=0&modestbranding=1&playsinline=1';
      f.title = 'YouTube-Video';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      box.innerHTML = '';
      box.appendChild(f);
    });
  });

  // Eigener Mauszeiger (nur Maus, nicht bei reduzierter Bewegung)
  var cursor = document.querySelector('.cursor');
  if (cursor && finePointer && !reduce) {
    var label = cursor.querySelector('.cursor__label');
    var x = -100, y = -100, cx = -100, cy = -100, raf = null;
    var loop = function () {
      cx += (x - cx) * 0.22; cy += (y - cy) * 0.22;
      cursor.style.transform = 'translate3d(' + cx + 'px,' + cy + 'px,0)';
      raf = (Math.abs(x - cx) + Math.abs(y - cy) > 0.3) ? requestAnimationFrame(loop) : null;
    };
    document.addEventListener('mousemove', function (e) {
      x = e.clientX; y = e.clientY;
      cursor.classList.add('is-on');
      if (!raf) raf = requestAnimationFrame(loop);
    }, { passive: true });
    document.addEventListener('mouseleave', function () { cursor.classList.remove('is-on'); });
    document.addEventListener('mouseover', function (e) {
      var t = e.target.closest('a, button, [data-cursor]');
      var txt = t && t.getAttribute('data-cursor');
      cursor.classList.toggle('is-link', !!t && !txt);
      cursor.classList.toggle('has-label', !!txt);
      label.textContent = txt || '';
    });
  }
})();
