/**
 * Year in Review - Neural Wrapped
 * Interactive animations and slide management
 */

document.addEventListener('DOMContentLoaded', function() {
  // State management
  let currentSlide = 0;
  const slides = document.querySelectorAll('.review-slide');
  const totalSlides = slides.length;
  const slidesWrapper = document.getElementById('slidesWrapper');
  const dots = document.querySelectorAll('.progress-dots .dot');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');

  // Touch handling
  let touchStartY = 0;
  let touchEndY = 0;
  let isTransitioning = false;

  // Initialize
  init();

  function init() {
    createParticles();
    setupEventListeners();
    updateSlide(0);

    // Delay initial animations
    setTimeout(() => {
      slides[0].classList.add('active');
      animateCounters(slides[0]);
    }, 500);
  }

  // Create floating particles
  function createParticles() {
    const container = document.getElementById('particles');
    const colors = ['#ff6b35', '#7c3aed', '#10b981', '#06b6d4', '#f59e0b', '#ec4899'];

    for (let i = 0; i < 30; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.left = Math.random() * 100 + '%';
      particle.style.background = colors[Math.floor(Math.random() * colors.length)];
      particle.style.animationDelay = Math.random() * 15 + 's';
      particle.style.animationDuration = (15 + Math.random() * 10) + 's';
      particle.style.width = (5 + Math.random() * 10) + 'px';
      particle.style.height = particle.style.width;
      container.appendChild(particle);
    }
  }

  // Event listeners
  function setupEventListeners() {
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown' || e.key === ' ') {
        e.preventDefault();
        nextSlide();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        prevSlide();
      }
    });

    // Touch events
    document.addEventListener('touchstart', (e) => {
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    document.addEventListener('touchend', (e) => {
      touchEndY = e.changedTouches[0].screenY;
      handleSwipe();
    }, { passive: true });

    // Mouse wheel
    document.addEventListener('wheel', (e) => {
      if (isTransitioning) return;

      if (e.deltaY > 50) {
        nextSlide();
      } else if (e.deltaY < -50) {
        prevSlide();
      }
    }, { passive: true });

    // Button clicks
    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);

    // Dot navigation
    dots.forEach((dot, index) => {
      dot.addEventListener('click', () => goToSlide(index));
    });
  }

  function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartY - touchEndY;

    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        nextSlide();
      } else {
        prevSlide();
      }
    }
  }

  function nextSlide() {
    if (isTransitioning || currentSlide >= totalSlides - 1) return;
    goToSlide(currentSlide + 1);
  }

  function prevSlide() {
    if (isTransitioning || currentSlide <= 0) return;
    goToSlide(currentSlide - 1);
  }

  function goToSlide(index) {
    if (isTransitioning || index === currentSlide || index < 0 || index >= totalSlides) return;

    isTransitioning = true;

    // Remove active class from current slide
    slides[currentSlide].classList.remove('active');

    // Update current slide
    currentSlide = index;

    // Transform slides wrapper
    slidesWrapper.style.transform = `translateY(-${currentSlide * 100}vh)`;

    // Update UI
    updateSlide(currentSlide);

    // Add active class after transition
    setTimeout(() => {
      slides[currentSlide].classList.add('active');
      animateCounters(slides[currentSlide]);
      animateWeekdayBars(slides[currentSlide]);

      // Trigger chart animation if on chart slide
      if (slides[currentSlide].classList.contains('slide-chart')) {
        initChart();
      }

      // Confetti on last slide
      if (currentSlide === totalSlides - 1) {
        triggerConfetti();
      }

      isTransitioning = false;
    }, 800);
  }

  function updateSlide(index) {
    // Update dots
    dots.forEach((dot, i) => {
      dot.classList.toggle('active', i === index);
    });

    // Update navigation buttons
    prevBtn.style.display = index === 0 ? 'none' : 'flex';
    nextBtn.style.display = index === totalSlides - 1 ? 'none' : 'flex';
  }

  // Animate counters
  function animateCounters(slide) {
    const counters = slide.querySelectorAll('.counter');

    counters.forEach(counter => {
      if (counter.dataset.animated) return;

      const target = parseInt(counter.dataset.target) || 0;
      const duration = 2000;
      const start = 0;
      const startTime = performance.now();

      function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = Math.round(start + (target - start) * easeOutQuart);

        counter.textContent = current.toLocaleString();

        if (progress < 1) {
          requestAnimationFrame(updateCounter);
        } else {
          counter.dataset.animated = 'true';
        }
      }

      requestAnimationFrame(updateCounter);
    });
  }

  // Animate weekday bars
  function animateWeekdayBars(slide) {
    const bars = slide.querySelectorAll('.bar-fill');
    if (bars.length === 0) return;

    const data = window.yearReviewData?.weekdayData || [];
    const maxValue = Math.max(...data, 1);

    bars.forEach((bar, index) => {
      const value = data[index] || 0;
      const height = (value / maxValue) * 100;

      setTimeout(() => {
        bar.style.setProperty('--bar-height', height + '%');
        bar.style.height = height + '%';
      }, index * 100);
    });
  }

  // Initialize chart
  function initChart() {
    const canvas = document.getElementById('monthlyChart');
    if (!canvas || canvas.dataset.initialized) return;

    const ctx = canvas.getContext('2d');
    const data = window.yearReviewData || {};

    // Gradient for bars
    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0.3)');

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.monthlyLabels || [],
        datasets: [{
          label: 'Entrenos',
          data: data.monthlyData || [],
          backgroundColor: gradient,
          borderRadius: 8,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 1500,
          easing: 'easeOutQuart'
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                return context.parsed.y + ' entrenos';
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.7)',
              font: {
                size: 10
              }
            }
          },
          y: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.7)',
              font: {
                size: 10
              },
              stepSize: 1
            },
            beginAtZero: true
          }
        }
      }
    });

    canvas.dataset.initialized = 'true';
  }

  // Confetti effect
  function triggerConfetti() {
    const colors = ['#ff6b35', '#7c3aed', '#10b981', '#f59e0b', '#ec4899', '#ffd700'];
    const confettiCount = 100;

    for (let i = 0; i < confettiCount; i++) {
      setTimeout(() => {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.width = (5 + Math.random() * 10) + 'px';
        confetti.style.height = confetti.style.width;
        confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
        confetti.style.animationDuration = (2 + Math.random() * 2) + 's';

        document.body.appendChild(confetti);

        // Remove after animation
        setTimeout(() => confetti.remove(), 4000);
      }, i * 20);
    }
  }

  // Preload next slide images (if any)
  function preloadSlideAssets(index) {
    if (index >= totalSlides) return;
    // Add any asset preloading logic here
  }

  // Visibility API - pause animations when tab is not visible
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      // Pause animations
      document.querySelectorAll('.particle').forEach(p => {
        p.style.animationPlayState = 'paused';
      });
    } else {
      // Resume animations
      document.querySelectorAll('.particle').forEach(p => {
        p.style.animationPlayState = 'running';
      });
    }
  });

  // ==========================================
  // SHARE FUNCTIONALITY
  // ==========================================

  // Download card as image
  const downloadBtn = document.getElementById('downloadCard');
  if (downloadBtn) {
    downloadBtn.addEventListener('click', downloadShareCard);
  }

  async function downloadShareCard() {
    const card = document.getElementById('shareCard');
    const btn = document.getElementById('downloadCard');

    if (!card || !window.html2canvas) {
      showToast('Error al generar imagen');
      return;
    }

    // Add loading state
    btn.classList.add('loading');

    try {
      // Wait for fonts and images to load
      await document.fonts.ready;

      const canvas = await html2canvas(card, {
        scale: 2, // Higher resolution
        backgroundColor: null,
        useCORS: true,
        allowTaint: true,
        logging: false,
        width: card.offsetWidth,
        height: card.offsetHeight,
      });

      // Convert to blob and download
      canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        const shareData = window.shareData || {};
        link.download = `neural-wrapped-${shareData.year || '2025'}.png`;
        link.href = url;
        link.click();
        URL.revokeObjectURL(url);

        showToast('Imagen descargada');
        btn.classList.remove('loading');
      }, 'image/png', 1.0);

    } catch (error) {
      console.error('Error generating image:', error);
      showToast('Error al generar imagen');
      btn.classList.remove('loading');
    }
  }

  // Social sharing functions
  const shareInstagram = document.getElementById('shareInstagram');
  const shareWhatsapp = document.getElementById('shareWhatsapp');
  const shareTwitter = document.getElementById('shareTwitter');
  const shareFacebook = document.getElementById('shareFacebook');

  if (shareInstagram) {
    shareInstagram.addEventListener('click', () => {
      // Instagram doesn't have direct web share, download image first
      downloadShareCard();
      showToast('Descarga la imagen y compartela en Instagram Stories');
    });
  }

  if (shareWhatsapp) {
    shareWhatsapp.addEventListener('click', () => {
      const data = window.shareData || {};
      const text = encodeURIComponent(
        `Este año entrene ${data.trainings} veces en Neural y queme ${data.calories} calorias. ${data.hashtag} neural.com.co`
      );
      window.open(`https://wa.me/?text=${text}`, '_blank');
    });
  }

  if (shareTwitter) {
    shareTwitter.addEventListener('click', () => {
      const data = window.shareData || {};
      const text = encodeURIComponent(
        `Mi ${data.year} en @NeuralGym: ${data.trainings} entrenamientos, ${data.calories} calorias quemadas, ${data.hours}h de dedicacion. ${data.hashtag}`
      );
      window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank');
    });
  }

  if (shareFacebook) {
    shareFacebook.addEventListener('click', () => {
      const url = encodeURIComponent(window.location.href);
      window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank');
    });
  }

  // Toast notification helper
  function showToast(message) {
    // Remove existing toasts
    document.querySelectorAll('.share-toast').forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = 'share-toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 3000);
  }

  // Native Web Share API (for mobile)
  async function nativeShare() {
    const data = window.shareData || {};

    if (navigator.share) {
      try {
        await navigator.share({
          title: `Mi ${data.year} en Neural`,
          text: `Este año entrene ${data.trainings} veces y queme ${data.calories} calorias. ${data.hashtag}`,
          url: window.location.href,
        });
      } catch (err) {
        console.log('Share cancelled or failed');
      }
    }
  }
});
