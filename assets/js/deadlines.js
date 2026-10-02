(() => {
  const root = document.querySelector('.deadlines-page');
  if (!root) return;

  const toolbar = root.querySelector('.deadline-toolbar');
  const input = root.querySelector('#deadline-search');
  const status = root.querySelector('#deadline-search-status');
  const empty = root.querySelector('.deadline-empty');
  const buttons = [...root.querySelectorAll('[data-deadline-filter]')];

  const normalize = text => String(text ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase();

  const cards = [...root.querySelectorAll('.deadline-card')].map(element => ({
    element,
    text: normalize(
      element.querySelector('.deadline-search-data')?.textContent
      ?? element.textContent
    ),
    topics: (element.dataset.deadlineTopics ?? '')
      .split(',')
      .map(topic => topic.trim().toUpperCase())
      .filter(Boolean)
  }));

  let selected = 'ALL';
  let frame;

  function alignRows() {
    // Rimuove le vecchie altezze prima di misurare.
    cards.forEach(({ element }) => {
      element.style.minHeight = '';

      element.querySelectorAll('[data-deadline-slot]').forEach(slot => {
        slot.style.minHeight = '';
      });
    });

    for (const grid of root.querySelectorAll('.deadline-cards')) {
      const rows = new Map();

      // Considera soltanto le schede visibili.
      for (const card of grid.querySelectorAll('.deadline-card')) {
        if (card.hidden || !card.getClientRects().length) continue;

        const top = Math.round(card.getBoundingClientRect().top);

        if (!rows.has(top)) rows.set(top, []);
        rows.get(top).push(card);
      }

      for (const row of rows.values()) {
        for (const name of [
          'header',
          'description',
          'location',
          'dates',
          'topics'
        ]) {
          const slots = row
            .map(card =>
              card.querySelector(`[data-deadline-slot="${name}"]`)
            )
            .filter(Boolean);

          if (!slots.length) continue;

          const height = Math.ceil(Math.max(
            ...slots.map(slot => slot.getBoundingClientRect().height)
          ));

          if (height > 0) {
            slots.forEach(slot => {
              slot.style.minHeight = `${height}px`;
            });
          }
        }
      }
    }
  }

  function scheduleAlignment() {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(alignRows);
  }

  function filter() {
    const terms = normalize(input?.value ?? '')
      .trim()
      .split(/\s+/)
      .filter(Boolean);

    let shown = 0;

    cards.forEach(card => {
      const topicMatch =
        selected === 'ALL' || card.topics.includes(selected);

      const searchMatch =
        terms.every(term => card.text.includes(term));

      card.element.hidden = !(topicMatch && searchMatch);

      if (!card.element.hidden) shown++;
    });

    for (const section of root.querySelectorAll('.deadline-section')) {
      const visible = [...section.querySelectorAll('.deadline-card')]
        .filter(card => !card.hidden).length;

      section.hidden = visible === 0;

      const count = section.querySelector('.deadline-section-count');
      if (count) count.textContent = visible;
    }

    if (empty) empty.hidden = shown !== 0;

    if (status) {
      status.textContent =
        `${shown} ${shown === 1 ? 'conference' : 'conferences'}`;
    }

    scheduleAlignment();
  }

  input?.addEventListener('input', filter);

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      selected = button.dataset.deadlineFilter.trim().toUpperCase();

      buttons.forEach(item => {
        item.setAttribute('aria-pressed', String(item === button));
      });

      filter();
    });
  });

  window.addEventListener('resize', scheduleAlignment);

  if (document.fonts) {
    document.fonts.ready.then(scheduleAlignment);
  }

  if ('ResizeObserver' in window) {
    let previousWidth;

    new ResizeObserver(entries => {
      const width = entries[0].contentRect.width;

      if (width !== previousWidth) {
        previousWidth = width;
        scheduleAlignment();
      }
    }).observe(root);
  }

  if (toolbar) toolbar.hidden = false;

  buttons.forEach(button => {
    button.setAttribute(
      'aria-pressed',
      String(button.dataset.deadlineFilter === 'ALL')
    );
  });

  filter();
})();