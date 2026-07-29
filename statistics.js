'use strict';

window.addEventListener('load', function () {
  var bars = document.querySelectorAll('.bar-chart .bar[data-tooltip]');
  var tooltip = document.createElement('div');
  tooltip.className = 'chart-tooltip';
  document.body.appendChild(tooltip);
  var pinnedBar = null;

  function placeTooltip(x, y) {
    var padding = 8;
    var width = tooltip.offsetWidth;
    var height = tooltip.offsetHeight;
    var maxLeft = window.innerWidth - width - padding;
    var maxTop = window.innerHeight - height - padding;

    var left = x;
    var top = y;

    if (left > maxLeft) {
      left = maxLeft;
    }
    if (top > maxTop) {
      top = maxTop;
    }
    if (left < padding) {
      left = padding;
    }
    if (top < padding) {
      top = padding;
    }

    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
  }

  function moveTooltipToElement(element) {
    var rect = element.getBoundingClientRect();
    placeTooltip(rect.right + 10, rect.top + 10);
  }

  function moveTooltip(event) {
    placeTooltip(event.clientX + 14, event.clientY + 14);
  }

  function showTooltip(event) {
    var label = event.currentTarget.getAttribute('data-tooltip');
    if (!label) {
      return;
    }

    tooltip.textContent = label;
    tooltip.classList.add('visible');
    if (typeof event.clientX === 'number' && typeof event.clientY === 'number') {
      moveTooltip(event);
    } else {
      moveTooltipToElement(event.currentTarget);
    }
  }

  function hideTooltip() {
    tooltip.classList.remove('visible');
  }

  function clearPinnedTooltip() {
    pinnedBar = null;
    hideTooltip();
  }

  function togglePinnedTooltip(event) {
    event.preventDefault();

    if (pinnedBar === event.currentTarget) {
      clearPinnedTooltip();
      return;
    }

    pinnedBar = event.currentTarget;
    showTooltip(event);
    moveTooltipToElement(event.currentTarget);
  }

  function maybeHideTooltip() {
    if (pinnedBar) {
      return;
    }
    hideTooltip();
  }

  function onBarKeyDown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      togglePinnedTooltip(event);
    }
  }

  for (var i = 0; i < bars.length; i++) {
    bars[i].addEventListener('mouseenter', showTooltip);
    bars[i].addEventListener('mousemove', moveTooltip);
    bars[i].addEventListener('mouseleave', maybeHideTooltip);
    bars[i].addEventListener('focus', showTooltip);
    bars[i].addEventListener('blur', maybeHideTooltip);
    bars[i].addEventListener('click', togglePinnedTooltip);
    bars[i].addEventListener('keydown', onBarKeyDown);
  }

  document.addEventListener('click', function (event) {
    if (event.target.closest('.bar-chart .bar[data-tooltip]')) {
      return;
    }
    clearPinnedTooltip();
  });

  var viewButtons = document.querySelectorAll('[data-played-view-button]');
  var views = document.querySelectorAll('[data-played-view]');

  function activatePlayedView(viewName) {
    clearPinnedTooltip();

    for (var buttonIndex = 0; buttonIndex < viewButtons.length; buttonIndex++) {
      var button = viewButtons[buttonIndex];
      var isActiveButton = button.getAttribute('data-played-view-button') === viewName;
      button.classList.toggle('active', isActiveButton);
      button.setAttribute('aria-pressed', isActiveButton ? 'true' : 'false');
    }

    for (var viewIndex = 0; viewIndex < views.length; viewIndex++) {
      var view = views[viewIndex];
      var isActiveView = view.getAttribute('data-played-view') === viewName;
      view.classList.toggle('chart-view-hidden', !isActiveView);
    }
  }

  for (var buttonIndex = 0; buttonIndex < viewButtons.length; buttonIndex++) {
    viewButtons[buttonIndex].addEventListener('click', function (event) {
      var viewName = event.currentTarget.getAttribute('data-played-view-button');
      if (!viewName) {
        return;
      }
      activatePlayedView(viewName);
    });
  }
});
