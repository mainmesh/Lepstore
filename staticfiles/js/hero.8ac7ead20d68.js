// Simple hero headphone tilt + bob animation
(() => {
  const el = document.getElementById('hero-headphone');
  if (!el) return;

  // Mouse move tilt
  const onMove = (e) => {
    const rect = el.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = (e.clientX - cx) / rect.width; // -0.5 .. 0.5
    const dy = (e.clientY - cy) / rect.height;

    const rotY = dx * 12; // degrees
    const rotX = -dy * 8;
    el.style.transform = `perspective(800px) rotateX(Ksh{rotX}deg) rotateY(Ksh{rotY}deg) translateZ(0)`;
  };

  // Reset on leave
  const onLeave = () => {
    el.style.transition = 'transform 600ms cubic-bezier(.2,.9,.3,1)';
    el.style.transform = '';
    setTimeout(() => el.style.transition = '', 700);
  };

  // Subtle float animation handled in CSS (keyframes). Add listeners for interaction.
  el.addEventListener('mousemove', onMove);
  el.addEventListener('mouseleave', onLeave);
  el.addEventListener('mouseenter', () => el.style.transition = '');
})();
