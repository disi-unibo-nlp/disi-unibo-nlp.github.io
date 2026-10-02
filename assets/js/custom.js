document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('navigation-toggle');
  const menu = document.getElementById('navMenu');
  const setNavigation = (open) => {
    toggle.classList.toggle('is-active', open);
    menu.classList.toggle('is-active', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  };
  if (toggle && menu) {
    toggle.addEventListener('click', () => setNavigation(toggle.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape') { setNavigation(false); } });
  }
  const search = document.getElementById('publication-search');
  if (!search) return;
  const year = document.getElementById('year-dropdown');
  const type = document.getElementById('type-dropdown');
  const venue = document.getElementById('venue-dropdown');
  const items = [...document.querySelectorAll('.publication-item')];
  const update = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    items.forEach(item => {
      const text = (item.querySelector('.publication-title').textContent + ' ' + item.querySelector('.authors').textContent).toLocaleLowerCase();
      item.hidden = !(
        (year.value === 'all' || item.dataset.year === year.value) &&
        (type.value === 'all' || item.dataset.type === type.value) &&
        (venue.value === 'all' || item.dataset.venue === venue.value) &&
        text.includes(query)
      );
      if (!item.hidden) count++;
    });
    document.querySelectorAll('.publication-group').forEach(group => { group.hidden = ![...group.querySelectorAll('.publication-item')].some(item => !item.hidden); });
    document.getElementById('publication-count').textContent = count;
    document.getElementById('publication-empty').hidden = count !== 0;
  };
  search.addEventListener('input', update);
  year.addEventListener('change', update);
  type.addEventListener('change', update);
  venue.addEventListener('change', update);
  document.getElementById('reset-publications').addEventListener('click', () => {
    search.value = '';
    year.value = 'all';
    type.value = 'all';
    venue.value = 'all';
    update();
    search.focus();
  });
  // Direct links from research highlights reveal the referenced publication.
  if (location.hash) {
    const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target) { const abstract = target.querySelector('details'); if (abstract) abstract.open = true; }
  }
  update();
});

(() => {
  const details = document.querySelector('.home-research-details');
  if (!details) return;

  const desktop = window.matchMedia('(min-width: 1024px)');

  const update = () => {
    details.open = desktop.matches;
  };

  update();
  desktop.addEventListener('change', update);

  // Su desktop le aree devono rimanere visibili.
  details.addEventListener('toggle', () => {
    if (desktop.matches && !details.open) details.open = true;
  });
})();


(() => {
  const reducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  );

  if (
    reducedMotion.matches ||
    !('IntersectionObserver' in window)
  ) return;

  const elements = [...document.querySelectorAll([
    '.home-section .section-heading',
    '.research-card',
    '.news-card',
    '.catalog-card',
    '.person-card',
    '.deadline-card',
    '.thesis-card',
    '.publication-item',
    '.contact-panel'
  ].join(','))];

  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;

      const element = entry.target;
      if (element.closest('[hidden]')) continue;

      const siblings = [...element.parentElement.children];
      const index = siblings.indexOf(element);

      element.style.setProperty(
        '--motion-delay',
        `${Math.min(index, 2) * 55}ms`
      );

      element.classList.add('motion-entered');
      observer.unobserve(element);
    }
  }, {
    threshold: 0,
    rootMargin: '0px 0px -24px 0px'
  });

  elements.forEach(element => observer.observe(element));

  reducedMotion.addEventListener('change', event => {
    if (!event.matches) return;

    observer.disconnect();
    elements.forEach(element => {
      element.classList.remove('motion-entered');
    });
  });
})();

(() => {
  const typeSelect = document.querySelector('#type-dropdown');
  const venueSelect = document.querySelector('#venue-dropdown');
  const resetButton = document.querySelector('#reset-publications');

  if (!typeSelect || !venueSelect) return;

  function syncVenueGroups() {
    venueSelect.querySelectorAll('[data-venue-type]').forEach(group => {
      group.disabled =
        typeSelect.value !== 'all' &&
        group.dataset.venueType !== typeSelect.value;
    });

    const selectedGroup =
      venueSelect.selectedOptions[0]?.closest('optgroup');

    // Rimuove una venue incompatibile con il tipo selezionato.
    if (selectedGroup?.disabled) {
      venueSelect.value = 'all';
      venueSelect.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

  typeSelect.addEventListener('change', syncVenueGroups);
  resetButton?.addEventListener('click', syncVenueGroups);

  syncVenueGroups();
})();

(() => {
  const stage = document.querySelector('.home-logo-stage');
  if (!stage || stage.dataset.logoInitialized) return;

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return;
  }

  const images = [...stage.querySelectorAll('img')];
  if (images.length !== 2) return;

  stage.dataset.logoInitialized = 'true';
  stage.classList.add('logo-loading');

  function waitForImage(image) {
    return new Promise((resolve, reject) => {
      if (image.complete) {
        if (image.naturalWidth > 0) {
          resolve();
        } else {
          reject(new Error('Logo could not be loaded'));
        }
        return;
      }

      image.addEventListener('load', resolve, { once: true });
      image.addEventListener('error', reject, { once: true });
    }).then(() => {
      if (typeof image.decode === 'function') {
        return image.decode().catch(() => {});
      }
    });
  }

  Promise.all(images.map(waitForImage))
    .then(() => {
      requestAnimationFrame(() => {
        stage.classList.remove('logo-loading');
        stage.classList.add('logo-ready');
      });
    })
    .catch(() => {
      stage.classList.remove('logo-loading');
    });
})();