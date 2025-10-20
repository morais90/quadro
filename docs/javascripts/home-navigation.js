let navigationCleanup = null;

/**
 * Initializes fullscreen section navigation with smooth scrolling.
 * Supports wheel, touch, and keyboard navigation between sections.
 */
function initSectionNavigation() {
  if (navigationCleanup) {
    navigationCleanup();
  }

  const container = document.querySelector('.md-main');
  if (!container) return;

  const sections = document.querySelectorAll('.quadro-section');
  if (sections.length === 0) return;

  const ANIMATION_DURATION_MS = 1000;
  const WHEEL_DELTA_THRESHOLD = 5;
  const WHEEL_COOLDOWN_MS = 100;
  const SWIPE_MIN_DISTANCE_PX = 50;
  const SWIPE_MAX_DURATION_MS = 500;
  const EASING = progress => (Math.sin((progress - 0.5) * Math.PI) + 1) / 2;

  let currentSection = 0;
  let isNavigating = false;
  let animationFrame = null;

  /**
   * @returns {number}
   */
  function getClosestSection() {
    const scrollTop = container.scrollTop;
    let closest = 0;
    let minDist = Infinity;

    sections.forEach((section, i) => {
      const dist = Math.abs(section.offsetTop - scrollTop);
      if (dist < minDist) {
        minDist = dist;
        closest = i;
      }
    });

    return closest;
  }

  /**
   * @param {number} index
   */
  function scrollToSection(index) {
    if (index < 0 || index >= sections.length || isNavigating) return;

    isNavigating = true;
    const start = container.scrollTop;
    const target = sections[index].offsetTop;
    const distance = target - start;
    const startTime = performance.now();

    function animate(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / ANIMATION_DURATION_MS, 1);

      container.scrollTop = start + distance * EASING(progress);

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      } else {
        currentSection = index;
        isNavigating = false;
        animationFrame = null;
      }
    }

    if (animationFrame) {
      cancelAnimationFrame(animationFrame);
    }

    animationFrame = requestAnimationFrame(animate);
  }

  /**
   * @param {number} direction
   */
  function navigate(direction) {
    if (isNavigating) return;

    const target = currentSection + direction;
    if (target >= 0 && target < sections.length) {
      scrollToSection(target);
    }
  }

  let wheelTimeout = null;
  let wheelInertia = false;

  /**
   * @param {WheelEvent} e
   */
  function onWheel(e) {
    if (e.target.closest('canvas')) return;

    e.preventDefault();

    if (isNavigating || wheelInertia) return;

    if (Math.abs(e.deltaY) > WHEEL_DELTA_THRESHOLD) {
      const direction = e.deltaY > 0 ? 1 : -1;
      navigate(direction);

      wheelInertia = true;
      clearTimeout(wheelTimeout);
      wheelTimeout = setTimeout(() => {
        wheelInertia = false;
      }, WHEEL_COOLDOWN_MS);
    }
  }

  let touchStartY = 0;
  let touchStartTime = 0;

  /**
   * @param {TouchEvent} e
   */
  function onTouchStart(e) {
    if (e.target.closest('canvas')) return;
    touchStartY = e.touches[0].clientY;
    touchStartTime = Date.now();
  }

  /**
   * @param {TouchEvent} e
   */
  function onTouchEnd(e) {
    if (e.target.closest('canvas') || isNavigating) return;

    const touchEndY = e.changedTouches[0].clientY;
    const distance = touchStartY - touchEndY;
    const duration = Date.now() - touchStartTime;

    if (Math.abs(distance) > SWIPE_MIN_DISTANCE_PX && duration < SWIPE_MAX_DURATION_MS) {
      navigate(distance > 0 ? 1 : -1);
    }
  }

  /**
   * @param {HTMLElement} element
   * @returns {boolean}
   */
  function isInteractiveElement(element) {
    const tag = element.tagName;
    return tag === 'INPUT' ||
           tag === 'TEXTAREA' ||
           tag === 'SELECT' ||
           element.isContentEditable;
  }

  /**
   * @param {KeyboardEvent} e
   */
  function onKeyDown(e) {
    if (isNavigating) return;

    switch(e.key) {
      case 'ArrowDown':
      case 'PageDown':
      case ' ':
        if (e.key === ' ' && isInteractiveElement(e.target)) return;
        e.preventDefault();
        navigate(1);
        break;
      case 'ArrowUp':
      case 'PageUp':
        e.preventDefault();
        navigate(-1);
        break;
      case 'Home':
        e.preventDefault();
        scrollToSection(0);
        break;
      case 'End':
        e.preventDefault();
        scrollToSection(sections.length - 1);
        break;
    }
  }

  container.addEventListener('wheel', onWheel, { passive: false });
  container.addEventListener('touchstart', onTouchStart, { passive: true });
  container.addEventListener('touchend', onTouchEnd, { passive: true });
  document.addEventListener('keydown', onKeyDown);

  currentSection = getClosestSection();
  scrollToSection(currentSection);

  navigationCleanup = () => {
    container.removeEventListener('wheel', onWheel);
    container.removeEventListener('touchstart', onTouchStart);
    container.removeEventListener('touchend', onTouchEnd);
    document.removeEventListener('keydown', onKeyDown);

    if (animationFrame) {
      cancelAnimationFrame(animationFrame);
      animationFrame = null;
    }

    if (wheelTimeout) {
      clearTimeout(wheelTimeout);
      wheelTimeout = null;
    }

    isNavigating = false;
    wheelInertia = false;
    navigationCleanup = null;
  };
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSectionNavigation);
} else {
  initSectionNavigation();
}

if (typeof document$ !== 'undefined') {
  document$.subscribe(() => {
    initSectionNavigation();
  });
}
