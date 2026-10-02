(() => {
  const root = document.querySelector('.theses-page');
  if (!root) return;
  const search = root.querySelector('.thesis-search');
  const input = root.querySelector('#thesis-query');
  const status = root.querySelector('#thesis-search-status');
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const cards = [...root.querySelectorAll('.thesis-card')].map(element => ({
    element, text: normalize(element.querySelector('.thesis-search-data').textContent)
  }));
  search.hidden = false;
  function update() {
    const terms = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      card.element.hidden = !terms.every(term => card.text.includes(term));
      if (!card.element.hidden) visible++;
    }
    for (const year of root.querySelectorAll('.thesis-year')) {
      year.hidden = ![...year.querySelectorAll('.thesis-card')].some(card => !card.hidden);
    }
    for (const degree of root.querySelectorAll('.thesis-degree')) {
      degree.hidden = ![...degree.querySelectorAll('.thesis-year')].some(year => !year.hidden);
    }
    status.textContent = terms.length ? `${visible} ${visible === 1 ? 'thesis' : 'theses'} found` : '';
  }
  input.addEventListener('input', update);
  update();
})();
