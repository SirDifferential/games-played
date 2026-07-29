'use strict';

window.addEventListener('load', function () {
  var bars = document.querySelectorAll('.bar-chart .bar[data-tooltip]');
  if (bars.length === 0) {
    return;
  }

  var tooltip = document.createElement('div');
  tooltip.className = 'chart-tooltip';
  document.body.appendChild(tooltip);

  function moveTooltip(event) {
    tooltip.style.left = (event.clientX + 14) + 'px';
    tooltip.style.top = (event.clientY + 14) + 'px';
  }

  function showTooltip(event) {
    var label = event.currentTarget.getAttribute('data-tooltip');
    if (!label) {
      return;
    }

    tooltip.textContent = label;
    tooltip.classList.add('visible');
    moveTooltip(event);
  }

  function hideTooltip() {
    tooltip.classList.remove('visible');
  }

  for (var i = 0; i < bars.length; i++) {
    bars[i].addEventListener('mouseenter', showTooltip);
    bars[i].addEventListener('mousemove', moveTooltip);
    bars[i].addEventListener('mouseleave', hideTooltip);
  }
});
