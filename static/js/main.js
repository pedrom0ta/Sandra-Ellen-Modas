// botão "voltar ao topo": aparece após rolar a página e sobe suavemente ao clicar
const backToTop = document.getElementById('backToTop');
if (backToTop) {
  const toggleBackToTop = () => {
    backToTop.classList.toggle('show', window.scrollY > 400);
  };
  window.addEventListener('scroll', toggleBackToTop, { passive: true });
  toggleBackToTop();
  backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// scroll reveal
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
}, { threshold: .15 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

// mobile burger: menu lateral com overlay, ícone animado e links com transição suave
const burger = document.querySelector('.burger');
const navLinks = document.querySelector('nav.links');
const navOverlay = document.querySelector('.nav-overlay');

function closeMenu() {
  burger.classList.remove('active');
  navLinks.classList.remove('active');
  navOverlay.classList.remove('active');
  document.body.classList.remove('menu-open');
  burger.setAttribute('aria-expanded', 'false');
}

function openMenu() {
  burger.classList.add('active');
  navLinks.classList.add('active');
  navOverlay.classList.add('active');
  document.body.classList.add('menu-open');
  burger.setAttribute('aria-expanded', 'true');
}

if (burger && navLinks && navOverlay) {
  burger.addEventListener('click', () => {
    navLinks.classList.contains('active') ? closeMenu() : openMenu();
  });
  navOverlay.addEventListener('click', closeMenu);
  navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeMenu();
  });
  window.addEventListener('resize', () => {
    if (window.innerWidth > 980) closeMenu();
  });
}

// filtro da vitrine (busca + chips de marca/categoria) na home
const catalogGrid = document.getElementById('productGrid');
if (catalogGrid) {
  const searchInput = document.getElementById('searchInput');
  const brandFilters = document.getElementById('brandFilters');
  const catFilters = document.getElementById('catFilters');
  const emptyState = document.getElementById('catalogEmptyState');
  const cards = Array.from(catalogGrid.querySelectorAll('.product-card'));

  function applyCatalogFilters() {
    const activeBrand = brandFilters ? brandFilters.querySelector('.chip.active')?.dataset.val || 'Todas' : 'Todas';
    const activeCat = catFilters ? catFilters.querySelector('.chip.active')?.dataset.val || 'Todas' : 'Todas';
    const query = (searchInput?.value || '').trim().toLowerCase();
    let visibleCount = 0;

    cards.forEach(card => {
      const matchBrand = activeBrand === 'Todas' || card.dataset.brand === activeBrand;
      const matchCat = activeCat === 'Todas' || card.dataset.category === activeCat;
      const matchQuery = !query || (card.dataset.name || '').includes(query);
      const visible = matchBrand && matchCat && matchQuery;
      card.style.display = visible ? '' : 'none';
      if (visible) visibleCount++;
    });

    if (emptyState) emptyState.style.display = visibleCount ? 'none' : 'block';
  }

  function setupChips(container) {
    if (!container) return;
    container.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', () => {
        container.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        applyCatalogFilters();
      });
    });
  }

  setupChips(brandFilters);
  setupChips(catFilters);
  searchInput?.addEventListener('input', applyCatalogFilters);
}

// galeria da página de produto: trilha deslizante com animação + miniaturas + setas + pontos + arraste real (toque e mouse)
(function () {
  const mainWrap = document.querySelector('.gallery-main');
  const mainImg = mainWrap ? mainWrap.querySelector('img') : null;
  const thumbs = Array.from(document.querySelectorAll('.gallery-thumbs img'));
  if (!mainWrap || !mainImg || !thumbs.length) return;

  const slideUrls = thumbs.map(t => t.dataset.full || t.src);
  const total = slideUrls.length;
  let current = 0;
  let dotsEl = null;

  // monta a trilha: uma faixa horizontal com uma imagem por slide
  const track = document.createElement('div');
  track.className = 'gallery-track';

  slideUrls.forEach((src, i) => {
    const slide = document.createElement('div');
    slide.className = 'gallery-slide';
    const img = document.createElement('img');
    img.src = src;
    img.alt = mainImg.alt || '';
    img.draggable = false;
    if (i === 0) {
      // reaproveita a imagem original (mesma tag) para não perder o alt/estado inicial
      slide.appendChild(mainImg);
      mainImg.src = src;
    } else {
      slide.appendChild(img);
    }
    track.appendChild(slide);
  });
  mainWrap.appendChild(track);

  function render(animate) {
    track.style.transition = animate ? '' : 'none';
    track.style.transform = `translateX(-${current * 100}%)`;
    thumbs.forEach((t, i) => t.classList.toggle('active', i === current));
    if (dotsEl) {
      Array.from(dotsEl.children).forEach((d, i) => d.classList.toggle('active', i === current));
    }
  }

  function goTo(index) {
    current = (index + total) % total;
    render(true);
  }

  // setas e pontos só fazem sentido com mais de uma foto
  if (total > 1) {
    const prevBtn = document.createElement('button');
    prevBtn.type = 'button';
    prevBtn.className = 'gallery-arrow gallery-arrow-prev';
    prevBtn.setAttribute('aria-label', 'Foto anterior');
    prevBtn.innerHTML = '&#10094;';
    prevBtn.addEventListener('click', () => goTo(current - 1));

    const nextBtn = document.createElement('button');
    nextBtn.type = 'button';
    nextBtn.className = 'gallery-arrow gallery-arrow-next';
    nextBtn.setAttribute('aria-label', 'Próxima foto');
    nextBtn.innerHTML = '&#10095;';
    nextBtn.addEventListener('click', () => goTo(current + 1));

    dotsEl = document.createElement('div');
    dotsEl.className = 'gallery-dots';
    slideUrls.forEach((_, i) => {
      const dot = document.createElement('span');
      dot.className = 'dot';
      dot.addEventListener('click', () => goTo(i));
      dotsEl.appendChild(dot);
    });

    mainWrap.append(prevBtn, nextBtn, dotsEl);
  }

  thumbs.forEach((thumb, i) => {
    thumb.addEventListener('click', () => goTo(i));
  });

  render(false);

  // arraste real: a foto acompanha o dedo/mouse durante o movimento
  let dragging = false;
  let startX = 0;
  let deltaX = 0;
  let wrapWidth = mainWrap.getBoundingClientRect().width;

  function dragStart(x) {
    if (total < 2) return;
    dragging = true;
    startX = x;
    deltaX = 0;
    wrapWidth = mainWrap.getBoundingClientRect().width;
    track.style.transition = 'none';
  }

  function dragMove(x) {
    if (!dragging) return;
    deltaX = x - startX;
    track.style.transform = `translateX(calc(-${current * 100}% + ${deltaX}px))`;
  }

  function dragEnd() {
    if (!dragging) return;
    dragging = false;
    const movedRatio = deltaX / wrapWidth;
    if (movedRatio < -0.15) {
      goTo(current + 1);
    } else if (movedRatio > 0.15) {
      goTo(current - 1);
    } else {
      render(true); // volta suavemente para a posição atual
    }
  }

  mainWrap.addEventListener('touchstart', e => dragStart(e.touches[0].clientX), { passive: true });
  mainWrap.addEventListener('touchmove', e => dragMove(e.touches[0].clientX), { passive: true });
  mainWrap.addEventListener('touchend', dragEnd);

  mainWrap.addEventListener('mousedown', e => { dragStart(e.clientX); e.preventDefault(); });
  window.addEventListener('mousemove', e => dragMove(e.clientX));
  window.addEventListener('mouseup', dragEnd);
})();
