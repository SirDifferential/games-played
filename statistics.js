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

  var orderButtons = document.querySelectorAll('[data-year-order-button]');
  var modeButtons = document.querySelectorAll('[data-year-mode-button]');
  var yearlyViews = document.querySelectorAll('[data-year-order][data-year-mode]');
  var activeOrder = 'release';
  var activeMode = 'gold';

  function setButtonStates(buttons, attributeName, activeValue) {
    for (var buttonIndex = 0; buttonIndex < buttons.length; buttonIndex++) {
      var button = buttons[buttonIndex];
      var isActiveButton = button.getAttribute(attributeName) === activeValue;
      button.classList.toggle('active', isActiveButton);
      button.setAttribute('aria-pressed', isActiveButton ? 'true' : 'false');
    }
  }

  function activateYearlyView(orderMode, subdivisionMode) {
    activeOrder = orderMode;
    activeMode = subdivisionMode;
    clearPinnedTooltip();

    setButtonStates(orderButtons, 'data-year-order-button', activeOrder);
    setButtonStates(modeButtons, 'data-year-mode-button', activeMode);

    for (var viewIndex = 0; viewIndex < yearlyViews.length; viewIndex++) {
      var yearlyView = yearlyViews[viewIndex];
      var viewOrder = yearlyView.getAttribute('data-year-order');
      var viewMode = yearlyView.getAttribute('data-year-mode');
      var isActiveView = viewOrder === activeOrder && viewMode === activeMode;
      yearlyView.classList.toggle('chart-view-hidden', !isActiveView);
    }
  }

  for (var orderIndex = 0; orderIndex < orderButtons.length; orderIndex++) {
    orderButtons[orderIndex].addEventListener('click', function (event) {
      var orderMode = event.currentTarget.getAttribute('data-year-order-button');
      if (!orderMode) {
        return;
      }
      activateYearlyView(orderMode, activeMode);
    });
  }

  for (var modeIndex = 0; modeIndex < modeButtons.length; modeIndex++) {
    modeButtons[modeIndex].addEventListener('click', function (event) {
      var subdivisionMode = event.currentTarget.getAttribute('data-year-mode-button');
      if (!subdivisionMode) {
        return;
      }
      activateYearlyView(activeOrder, subdivisionMode);
    });
  }

  activateYearlyView(activeOrder, activeMode);
});
