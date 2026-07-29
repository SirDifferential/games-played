from datetime import datetime
from collections import Counter
from html import escape
import csv
import sys


def entryToTableRow(entry):
	try:
		out = ''
		if isGoldEntry(entry):
			out = "<tr class='GOTY'>"
		else:
			out = '<tr>'
		out += '<td>' + entry['Game'] + '</td>'
		out += '<td>' + entry['Finished'].strftime('%Y-%m-%d') + '</td>'
		out += '<td>' + entry['Genre'] + '</td>'
		out += '<td>' + entry['Platform'] + '</td>'

		# Sanity check
		int(entry['Release date'])

		out += '<td>' + entry['Release date'] + '</td>'
		out += '<td>' + entry['Review'].replace('\\n', '<br>').replace("\\'", chr(34)) + '</td>'
		out += '</tr>\n'
	except Exception as e:
		print(e)
		print(entry)
		sys.exit(1)
	return out


def normalizeCategory(value):
	if value is None:
		return ''
	return value.strip()


def normalizePlatform(value):
	platform = normalizeCategory(value)
	if platform == '':
		return 'Unknown'
	return platform


def normalizeGenre(value):
	genre = normalizeCategory(value)
	if genre == '':
		return 'Unknown'
	return genre


def normalizeStore(value):
	store = normalizeCategory(value)
	if store == '':
		return 'Unknown'
	return store


def isGoldEntry(entry):
	value = entry.get('GOTY')
	if value is None:
		return False
	return str(value).strip() != ''


def countByPlatform(gameData):
	counter = Counter()
	for entry in gameData:
		counter[normalizePlatform(entry['Platform'])] += 1
	return sorted(counter.items(), key=lambda x: x[0].lower())


def countByGenre(gameData):
	counter = Counter()
	for entry in gameData:
		counter[normalizeGenre(entry['Genre'])] += 1
	return sorted(counter.items(), key=lambda x: (-x[1], x[0].lower()))


def buildStorePalette(gameData):
	storeCounts = Counter()
	for entry in gameData:
		storeCounts[normalizeStore(entry.get('Service'))] += 1

	sortedStores = sorted(storeCounts.items(), key=lambda x: (-x[1], x[0].lower()))
	selectedStores = [name for name, _ in sortedStores]

	palette = [
		'#4f81bd',
		'#f28e2b',
		'#59a14f',
		'#e15759',
		'#af7aa1',
		'#edc948',
		'#76b7b2',
		'#ff9da7',
		'#9c755f',
		'#bab0ab'
	]

	colors = {}
	for index, store in enumerate(selectedStores):
		colors[store] = palette[index % len(palette)]

	return selectedStores, colors


def buildPlatformPalette(gameData, maxPlatforms=8):
	platformCounts = Counter()
	for entry in gameData:
		platformCounts[normalizePlatform(entry['Platform'])] += 1

	sortedPlatforms = sorted(platformCounts.items(), key=lambda x: (-x[1], x[0].lower()))
	selectedPlatforms = [name for name, _ in sortedPlatforms[:maxPlatforms]]

	if len(sortedPlatforms) > maxPlatforms:
		selectedPlatforms.append('Other')

	palette = [
		'#4f81bd',
		'#f28e2b',
		'#59a14f',
		'#e15759',
		'#af7aa1',
		'#edc948',
		'#76b7b2',
		'#ff9da7',
		'#9c755f',
		'#bab0ab'
	]

	colors = {}
	for index, platform in enumerate(selectedPlatforms):
		colors[platform] = palette[index % len(palette)]

	return selectedPlatforms, colors


def buildGenrePalette(gameData):
	genreCounts = Counter()
	for entry in gameData:
		genreCounts[normalizeGenre(entry['Genre'])] += 1

	genres = sorted(genreCounts.items(), key=lambda x: (-x[1], x[0].lower()))
	order = [name for name, _ in genres]
	colors = {}

	for index, genre in enumerate(order):
		hue = (index * 137) % 360
		colors[genre] = 'hsl(' + str(hue) + ', 62%, 52%)'

	return order, colors


def buildLegend(items, colorMap, ariaLabel, imageMap=None):
	if len(items) == 0:
		return ''

	if imageMap is None:
		imageMap = {}

	legendItems = []
	for item in items:
		if item in imageMap:
			imagePath = imageMap[item]
			swatch = '<span class="legend-swatch legend-swatch-image" aria-hidden="true"><img src="' + escape(imagePath, quote=True) + '" alt=""></span>'
		else:
			color = colorMap[item]
			swatch = '<span class="legend-swatch" style="background-color: ' + color + ';" aria-hidden="true"></span>'
		label = '<span class="legend-label">' + escape(item) + '</span>'
		legendItems.append('<span class="legend-item">' + swatch + label + '</span>')

	return '<div class="chart-legend" role="list" aria-label="' + escape(ariaLabel, quote=True) + '">' + ''.join(legendItems) + '</div>'


def storeLogoAssets(storeOrder):
	storeToLogo = {
		'GOG': 'graphics/GOG.com_logo.png',
		'Free': 'graphics/gift.png',
		'Humble Bundle': 'graphics/humble-bundle-icon.png',
		'itch.io': 'graphics/itch.svg',
		'Kickstarter': 'graphics/kickstarter.png',
		'Retail': 'graphics/disk.png',
		'Shareware': 'graphics/money-bags.png',
		'Steam': 'graphics/Steam_icon_logo.svg'
	}
	fallbackLogo = 'graphics/circle-question-mark.svg'

	barLogos = {}
	legendImages = {}

	for store in storeOrder:
		logoPath = storeToLogo.get(store, fallbackLogo)

		barLogos[store] = logoPath
		legendImages[store] = logoPath

	return barLogos, legendImages


def platformLogoAssets(platformOrder):
	platformToLogo = {
		'Windows': 'graphics/Windows_Logo_(1992-2001).svg.webp',
		'Amiga': 'graphics/Commodore_Amiga_logo-03.svg',
		'Linux': 'graphics/Tux.svg.webp',
		'DOS': 'graphics/Msdos-icon.svg.webp',
		'SCUMMVM': 'graphics/ScummVM__Modern_Remastered__Logo.svg.webp',
		'NES': 'graphics/NES_logo.svg',
		'Sega Megadrive': 'graphics/SEGA_logo.svg.webp',
		'Commodore 64': 'graphics/Commodore_64.svg.webp'
	}

	barLogos = {}
	legendImages = {}

	for platform in platformOrder:
		logoPath = platformToLogo.get(platform)
		if logoPath is None:
			continue

		barLogos[platform] = logoPath
		legendImages[platform] = logoPath

	return barLogos, legendImages


def allocateSegmentHeights(order, counts, totalCount, totalHeight):
	if totalCount <= 0 or totalHeight <= 0:
		return {}

	indexed = {value: index for index, value in enumerate(order)}
	allocations = []
	usedHeight = 0

	for value in order:
		count = counts.get(value, 0)
		if count <= 0:
			continue

		exactHeight = (count / totalCount) * totalHeight
		baseHeight = int(exactHeight)
		remainder = exactHeight - baseHeight
		usedHeight += baseHeight
		allocations.append({
			'value': value,
			'height': baseHeight,
			'remainder': remainder,
			'count': count,
			'index': indexed[value]
		})

	remainingHeight = totalHeight - usedHeight
	allocations.sort(key=lambda x: (-x['remainder'], -x['count'], x['index']))

	for allocation in allocations:
		if remainingHeight <= 0:
			break
		allocation['height'] += 1
		remainingHeight -= 1

	heights = {}
	for allocation in allocations:
		heights[allocation['value']] = allocation['height']

	return heights


def yearChartScaffold(yearCounts, chartClassName, labelPrefix):
	startYear = min(yearCounts.keys())
	endYear = datetime.now().year
	years = list(range(startYear, endYear + 1))

	leftPad = 50
	rightPad = 16
	topPad = 16
	bottomPad = 58
	barWidth = 10
	barGap = 3
	plotHeight = 220
	plotWidth = len(years) * (barWidth + barGap) - barGap

	svgWidth = leftPad + plotWidth + rightPad
	svgHeight = topPad + plotHeight + bottomPad

	return {
		'years': years,
		'endYear': endYear,
		'leftPad': leftPad,
		'topPad': topPad,
		'barWidth': barWidth,
		'barGap': barGap,
		'plotHeight': plotHeight,
		'plotWidth': plotWidth,
		'svgOpen': '<svg class="bar-chart ' + chartClassName + '" viewBox="0 0 ' + str(svgWidth) + ' ' + str(svgHeight) + '" preserveAspectRatio="xMidYMax meet" role="img" aria-label="Games by ' + labelPrefix + ' from ' + str(startYear) + ' to ' + str(endYear) + '">\n'
	}


def buildGoldYearChart(gameData, yearExtractor, chartClassName, labelPrefix, noDataMessage, displayCountOverrides=None):
	totalCounts = Counter()
	goldCounts = Counter()

	for entry in gameData:
		year = yearExtractor(entry)
		totalCounts[year] += 1
		if isGoldEntry(entry):
			goldCounts[year] += 1

	if len(totalCounts) == 0:
		return '<p>' + noDataMessage + '</p>'

	if displayCountOverrides is None:
		displayCountOverrides = {}

	scaffold = yearChartScaffold(totalCounts, chartClassName, labelPrefix)
	years = scaffold['years']
	endYear = scaffold['endYear']
	leftPad = scaffold['leftPad']
	topPad = scaffold['topPad']
	barWidth = scaffold['barWidth']
	barGap = scaffold['barGap']
	plotHeight = scaffold['plotHeight']
	plotWidth = scaffold['plotWidth']

	displayCounts = {}
	for year in years:
		realCount = totalCounts.get(year, 0)
		displayCount = displayCountOverrides.get(year, realCount)
		displayCounts[year] = max(0, displayCount)

	maxCount = max([displayCounts[year] for year in years])
	if maxCount == 0:
		maxCount = 1

	out = ''
	out += scaffold['svgOpen']
	out += '<line class="axis" x1="' + str(leftPad) + '" y1="' + str(topPad) + '" x2="' + str(leftPad) + '" y2="' + str(topPad + plotHeight) + '"/>\n'
	out += '<line class="axis" x1="' + str(leftPad) + '" y1="' + str(topPad + plotHeight) + '" x2="' + str(leftPad + plotWidth) + '" y2="' + str(topPad + plotHeight) + '"/>\n'
	out += '<text x="' + str(leftPad - 6) + '" y="' + str(topPad + 4) + '" text-anchor="end">' + str(maxCount) + '</text>\n'
	out += '<text x="' + str(leftPad - 6) + '" y="' + str(topPad + plotHeight + 4) + '" text-anchor="end">0</text>\n'

	for index, year in enumerate(years):
		realCount = totalCounts.get(year, 0)
		displayCount = displayCounts[year]
		goldCount = goldCounts.get(year, 0)

		totalBarHeight = 0
		if displayCount > 0:
			totalBarHeight = max(1, int((displayCount / maxCount) * plotHeight))

		x = leftPad + index * (barWidth + barGap)
		barTop = topPad + plotHeight - totalBarHeight

		gamesLabel = 'game'
		if realCount != 1:
			gamesLabel = 'games'

		tooltip = str(year) + ': ' + str(realCount) + ' ' + gamesLabel + ', ' + str(goldCount) + ' gold'
		if displayCount != realCount:
			tooltip += ' (rendered as ' + str(displayCount) + ')'

		adjustedClass = ''
		if displayCount != realCount:
			adjustedClass = ' bar-adjusted'

		goldBarHeight = 0
		if goldCount > 0 and totalBarHeight > 0:
			goldBarHeight = int((goldCount / maxCount) * plotHeight)
			goldBarHeight = max(2, goldBarHeight)
			goldBarHeight = min(totalBarHeight, goldBarHeight)

		nonGoldBarHeight = totalBarHeight - goldBarHeight

		if nonGoldBarHeight > 0:
			nonGoldY = barTop + goldBarHeight
			out += '<rect class="bar bar-base' + adjustedClass + '" x="' + str(x) + '" y="' + str(nonGoldY) + '" width="' + str(barWidth) + '" height="' + str(nonGoldBarHeight) + '" rx="2" ry="2" data-tooltip="' + escape(tooltip, quote=True) + '" aria-label="' + escape(tooltip, quote=True) + '"></rect>\n'

		if goldBarHeight > 0:
			out += '<rect class="bar bar-gold' + adjustedClass + '" x="' + str(x) + '" y="' + str(barTop) + '" width="' + str(barWidth) + '" height="' + str(goldBarHeight) + '" rx="2" ry="2" data-tooltip="' + escape(tooltip, quote=True) + '" aria-label="' + escape(tooltip, quote=True) + '"></rect>\n'

		if index == 0 or year == endYear or year % 5 == 0:
			labelX = x + (barWidth / 2)
			labelY = topPad + plotHeight + 15
			out += '<text x="' + str(labelX) + '" y="' + str(labelY) + '" text-anchor="start" transform="rotate(60 ' + str(labelX) + ' ' + str(labelY) + ')">' + str(year) + '</text>\n'

	out += '</svg>'
	return out


def buildStackedYearChart(gameData, yearExtractor, categoryExtractor, categoryOrder, categoryColors, chartClassName, labelPrefix, noDataMessage, displayCountOverrides=None, otherBucket=None, categoryLogoImages=None, clipIdPrefix='chart'):
	totalCounts = Counter()
	categoryCountsByYear = {}
	selectedCategories = set(categoryOrder)

	if categoryLogoImages is None:
		categoryLogoImages = {}

	for entry in gameData:
		year = yearExtractor(entry)
		category = categoryExtractor(entry)

		if otherBucket is not None and category not in selectedCategories:
			category = otherBucket
		elif category not in selectedCategories:
			continue

		totalCounts[year] += 1
		if year not in categoryCountsByYear:
			categoryCountsByYear[year] = Counter()
		categoryCountsByYear[year][category] += 1

	if len(totalCounts) == 0:
		return '<p>' + noDataMessage + '</p>'

	if displayCountOverrides is None:
		displayCountOverrides = {}

	scaffold = yearChartScaffold(totalCounts, chartClassName, labelPrefix)
	years = scaffold['years']
	endYear = scaffold['endYear']
	leftPad = scaffold['leftPad']
	topPad = scaffold['topPad']
	barWidth = scaffold['barWidth']
	barGap = scaffold['barGap']
	plotHeight = scaffold['plotHeight']
	plotWidth = scaffold['plotWidth']

	displayCounts = {}
	for year in years:
		realCount = totalCounts.get(year, 0)
		displayCount = displayCountOverrides.get(year, realCount)
		displayCounts[year] = max(0, displayCount)

	maxCount = max([displayCounts[year] for year in years])
	if maxCount == 0:
		maxCount = 1

	out = ''
	out += scaffold['svgOpen']
	defsOut = ''
	logoSegmentId = 0
	out += '<line class="axis" x1="' + str(leftPad) + '" y1="' + str(topPad) + '" x2="' + str(leftPad) + '" y2="' + str(topPad + plotHeight) + '"/>\n'
	out += '<line class="axis" x1="' + str(leftPad) + '" y1="' + str(topPad + plotHeight) + '" x2="' + str(leftPad + plotWidth) + '" y2="' + str(topPad + plotHeight) + '"/>\n'
	out += '<text x="' + str(leftPad - 6) + '" y="' + str(topPad + 4) + '" text-anchor="end">' + str(maxCount) + '</text>\n'
	out += '<text x="' + str(leftPad - 6) + '" y="' + str(topPad + plotHeight + 4) + '" text-anchor="end">0</text>\n'

	for index, year in enumerate(years):
		realCount = totalCounts.get(year, 0)
		displayCount = displayCounts[year]
		yearCategoryCounts = categoryCountsByYear.get(year, Counter())

		totalBarHeight = 0
		if displayCount > 0:
			totalBarHeight = max(1, int((displayCount / maxCount) * plotHeight))

		x = leftPad + index * (barWidth + barGap)
		segmentHeights = allocateSegmentHeights(categoryOrder, yearCategoryCounts, realCount, totalBarHeight)
		currentY = topPad + plotHeight

		for category in categoryOrder:
			segmentHeight = segmentHeights.get(category, 0)
			if segmentHeight <= 0:
				continue

			categoryCount = yearCategoryCounts.get(category, 0)
			segmentY = currentY - segmentHeight
			gamesLabel = 'game'
			if categoryCount != 1:
				gamesLabel = 'games'

			tooltip = str(year) + ' - ' + category + ': ' + str(categoryCount) + ' ' + gamesLabel + ' of ' + str(realCount)
			if displayCount != realCount:
				tooltip += ' (year rendered as ' + str(displayCount) + ')'
			categoryAttr = escape(category, quote=True)

			color = categoryColors.get(category, '#4f81bd')
			logoPath = categoryLogoImages.get(category)
			if logoPath is not None:
				clipId = clipIdPrefix + '-logo-clip-' + str(logoSegmentId)
				logoSegmentId += 1
				defsOut += '<clipPath id="' + clipId + '"><rect x="' + str(x) + '" y="' + str(segmentY) + '" width="' + str(barWidth) + '" height="' + str(segmentHeight) + '" rx="2" ry="2"></rect></clipPath>'

				out += '<rect class="bar bar-segment bar-logo-segment" x="' + str(x) + '" y="' + str(segmentY) + '" width="' + str(barWidth) + '" height="' + str(segmentHeight) + '" rx="2" ry="2" style="fill: #f4f5f7;" data-tooltip="' + escape(tooltip, quote=True) + '" data-segment-category="' + categoryAttr + '" aria-label="' + escape(tooltip, quote=True) + '" tabindex="0"></rect>\n'

				tileSize = barWidth
				tileY = segmentY
				out += '<g class="bar-logo-tiles" clip-path="url(#' + clipId + ')" data-segment-category="' + categoryAttr + '" pointer-events="none">'
				while tileY < segmentY + segmentHeight:
					out += '<image href="' + escape(logoPath, quote=True) + '" x="' + str(x) + '" y="' + str(tileY) + '" width="' + str(barWidth) + '" height="' + str(tileSize) + '" preserveAspectRatio="xMidYMid meet"></image>'
					tileY += tileSize
				out += '</g>\n'
			else:
				out += '<rect class="bar bar-segment" x="' + str(x) + '" y="' + str(segmentY) + '" width="' + str(barWidth) + '" height="' + str(segmentHeight) + '" rx="2" ry="2" style="fill: ' + color + ';" data-tooltip="' + escape(tooltip, quote=True) + '" data-segment-category="' + categoryAttr + '" aria-label="' + escape(tooltip, quote=True) + '" tabindex="0"></rect>\n'
			currentY = segmentY

		if index == 0 or year == endYear or year % 5 == 0:
			labelX = x + (barWidth / 2)
			labelY = topPad + plotHeight + 15
			out += '<text x="' + str(labelX) + '" y="' + str(labelY) + '" text-anchor="start" transform="rotate(60 ' + str(labelX) + ' ' + str(labelY) + ')">' + str(year) + '</text>\n'

	if defsOut != '':
		out = out.replace(scaffold['svgOpen'], scaffold['svgOpen'] + '<defs>' + defsOut + '</defs>\n', 1)

	out += '</svg>'
	return out


def buildYearlyChartSwitcher(chartsByOrderAndMode, systemsLegend, storeLegend):
	out = ''
	out += '<div class="year-chart-switchers">'
	out += '<div class="played-year-switcher" role="tablist" aria-label="Year ordering">'
	out += '<button class="chart-mode-button active" type="button" data-year-order-button="release" aria-pressed="true">By release year</button>'
	out += '<button class="chart-mode-button" type="button" data-year-order-button="played" aria-pressed="false">By played year</button>'
	out += '</div>'
	out += '<div class="played-year-switcher" role="tablist" aria-label="Year subdivision">'
	out += '<button class="chart-mode-button active" type="button" data-year-mode-button="gold" aria-pressed="true">Games + Gold</button>'
	out += '<button class="chart-mode-button" type="button" data-year-mode-button="systems" aria-pressed="false">Systems</button>'
	out += '<button class="chart-mode-button" type="button" data-year-mode-button="store" aria-pressed="false">Store</button>'
	out += '<button class="chart-mode-button" type="button" data-year-mode-button="genres" aria-pressed="false">Genres</button>'
	out += '</div>'
	out += '</div>'

	for orderMode in ['release', 'played']:
		for subdivisionMode in ['gold', 'systems', 'store', 'genres']:
			chartContent = chartsByOrderAndMode[orderMode][subdivisionMode]
			if subdivisionMode == 'systems':
				chartContent = systemsLegend + chartContent
			if subdivisionMode == 'store':
				chartContent = storeLegend + chartContent

			classes = 'yearly-view chart-view-hidden'
			if orderMode == 'release' and subdivisionMode == 'gold':
				classes = 'yearly-view'

			out += '<div class="' + classes + '" data-year-order="' + orderMode + '" data-year-mode="' + subdivisionMode + '">' + chartContent + '</div>'

	return out


def playedYearGenreHeatmap(gameData):
	if len(gameData) == 0:
		return '<p>No played year data available.</p>'

	countsByYearGenre = {}
	yearCounts = Counter()
	genreCounts = Counter()

	for entry in gameData:
		year = entry['Finished'].year
		genre = normalizeGenre(entry.get('Genre'))

		yearCounts[year] += 1
		genreCounts[genre] += 1

		if year not in countsByYearGenre:
			countsByYearGenre[year] = Counter()
		countsByYearGenre[year][genre] += 1

	years = list(range(min(yearCounts.keys()), max(yearCounts.keys()) + 1))
	genres = [name for name, _ in sorted(genreCounts.items(), key=lambda x: (-x[1], x[0].lower()))]

	maxCellCount = 0
	for year in years:
		for genre in genres:
			maxCellCount = max(maxCellCount, countsByYearGenre.get(year, Counter()).get(genre, 0))

	if maxCellCount <= 0:
		maxCellCount = 1
	colorScaleMax = min(maxCellCount, 8)
	if colorScaleMax <= 0:
		colorScaleMax = 1

	def cellColor(count):
		if count <= 0:
			return '#fff4ee'

		ratio = min(count, colorScaleMax) / colorScaleMax
		if ratio < 0.4:
			local = ratio / 0.4
			hue = int(6 + local * 16)
			saturation = int(82 + local * 8)
			lightness = int(93 - local * 35)
			return 'hsl(' + str(hue) + ', ' + str(saturation) + '%, ' + str(lightness) + '%)'
		if ratio < 0.75:
			local = (ratio - 0.4) / 0.35
			hue = int(22 + local * 18)
			saturation = int(90 + local * 6)
			lightness = int(58 - local * 18)
			return 'hsl(' + str(hue) + ', ' + str(saturation) + '%, ' + str(lightness) + '%)'

		local = (ratio - 0.75) / 0.25
		hue = int(40 + local * 14)
		saturation = int(96 - local * 6)
		lightness = int(40 + local * 18)
		return 'hsl(' + str(hue) + ', ' + str(saturation) + '%, ' + str(lightness) + '%)'

	cellSize = 12
	cellGap = 2
	rowHeight = cellSize + cellGap
	columnWidth = cellSize + cellGap
	leftPad = max(56, min(170, max([len(name) for name in genres]) * 5 + 6))
	topPad = 76
	rightPad = 20
	bottomPad = 18

	gridWidth = len(years) * columnWidth - cellGap
	gridHeight = len(genres) * rowHeight - cellGap

	svgWidth = leftPad + gridWidth + rightPad
	svgHeight = topPad + gridHeight + bottomPad

	out = ''
	out += '<svg class="played-genre-heatmap" viewBox="0 0 ' + str(svgWidth) + ' ' + str(svgHeight) + '" preserveAspectRatio="xMinYMin meet" role="img" aria-label="Heatmap of played genres by year">\n'
	out += '<rect x="0" y="0" width="' + str(svgWidth) + '" height="' + str(svgHeight) + '" fill="#fff"></rect>\n'

	for yearIndex, year in enumerate(years):
		x = leftPad + yearIndex * columnWidth + int(cellSize / 2)
		if yearIndex == 0 or year == years[-1] or year % 2 == 0:
			labelY = topPad - 10
			out += '<text class="heatmap-year-label" x="' + str(x) + '" y="' + str(labelY) + '" text-anchor="start" transform="rotate(-50 ' + str(x) + ' ' + str(labelY) + ')">' + str(year) + '</text>\n'

	for genreIndex, genre in enumerate(genres):
		y = topPad + genreIndex * rowHeight
		out += '<text class="heatmap-genre-label" x="' + str(leftPad - 8) + '" y="' + str(y + 9) + '" text-anchor="end">' + escape(genre) + '</text>\n'

		for yearIndex, year in enumerate(years):
			x = leftPad + yearIndex * columnWidth
			count = countsByYearGenre.get(year, Counter()).get(genre, 0)
			tooltip = str(year) + ' - ' + genre + ': ' + str(count)
			if count == 1:
				tooltip += ' game'
			else:
				tooltip += ' games'

			out += '<rect class="heatmap-cell" x="' + str(x) + '" y="' + str(y) + '" width="' + str(cellSize) + '" height="' + str(cellSize) + '" fill="' + cellColor(count) + '" data-tooltip="' + escape(tooltip, quote=True) + '" tabindex="0"></rect>\n'

	legendX = leftPad
	legendY = 20
	legendSteps = 5
	legendCellWidth = 24

	out += '<text class="heatmap-legend-label" x="' + str(legendX) + '" y="' + str(legendY - 9) + '" text-anchor="start">Games per year/genre cell</text>\n'
	for step in range(legendSteps):
		if legendSteps == 1:
			value = 0
		else:
			value = int(round((step / (legendSteps - 1)) * colorScaleMax))
		x = legendX + step * (legendCellWidth + 4)
		out += '<rect class="heatmap-cell" x="' + str(x) + '" y="' + str(legendY) + '" width="' + str(legendCellWidth) + '" height="10" fill="' + cellColor(value) + '"></rect>\n'
		out += '<text class="heatmap-legend-tick" x="' + str(x) + '" y="' + str(legendY + 24) + '" text-anchor="start">' + str(value) + '</text>\n'

	out += '</svg>'
	return out


def statisticsRows(items):
	out = ''
	for key, count in items:
		out += '<tr><td>' + escape(str(key)) + '</td><td>' + str(count) + '</td></tr>\n'
	return out


# Read game data from CSV
fin = open('games-played.csv', 'r')
data = fin.read().split('\n')
fin.close()

reader = csv.DictReader(data, quotechar='"')
gameData = []
row = ''

try:
	for row in reader:
		# Parse date to programmable time
		row['Finished'] = datetime.strptime(row['Finished'], '%d.%m.%Y')
		gameData.append(row)
except Exception as e:
	print(e)
	print(row)
	sys.exit(1)

gameData.sort(key=lambda x: x['Finished'], reverse=True)
gameDataStr = ''
for entry in gameData:
	gameDataStr += entryToTableRow(entry)

# Read HTML template
fin = open('list.template', 'r')
template = fin.read()
fin.close()

# Write generated HTML with data
htmldata = template.replace('REPLACE_TABLE_DATA', gameDataStr).replace('REPLACE_GAME_COUNT', str(len(gameData)))
fout = open('list.html', 'w')
fout.write(htmldata)
fout.close()

platformRows = statisticsRows(countByPlatform(gameData))
genreRows = statisticsRows(countByGenre(gameData))

platformOrder, platformColors = buildPlatformPalette(gameData)
platformBarLogos, platformLegendImages = platformLogoAssets(platformOrder)
platformLegend = buildLegend(platformOrder, platformColors, 'Platform colors', platformLegendImages)
storeOrder, storeColors = buildStorePalette(gameData)
storeBarLogos, storeLegendImages = storeLogoAssets(storeOrder)
storeLegend = buildLegend(storeOrder, storeColors, 'Store colors', storeLegendImages)
genreOrder, genreColors = buildGenrePalette(gameData)

chartsByOrderAndMode = {}
for orderMode, yearExtractor, displayOverrides in [
	('release', lambda entry: int(entry['Release date']), None),
	('played', lambda entry: entry['Finished'].year, {1995: 40})
]:
	labelPrefix = orderMode + ' year'
	noDataMessage = 'No ' + labelPrefix + ' data available.'

	chartsByOrderAndMode[orderMode] = {
		'gold': buildGoldYearChart(
			gameData,
			yearExtractor,
			'year-chart',
			labelPrefix,
			noDataMessage,
			displayOverrides
		),
		'systems': buildStackedYearChart(
			gameData,
			yearExtractor,
			lambda entry: normalizePlatform(entry['Platform']),
			platformOrder,
			platformColors,
			'year-chart',
			labelPrefix,
			noDataMessage,
			displayOverrides,
			'Other',
			platformBarLogos,
			'systems-' + orderMode
		),
		'store': buildStackedYearChart(
			gameData,
			yearExtractor,
			lambda entry: normalizeStore(entry.get('Service')),
			storeOrder,
			storeColors,
			'year-chart',
			labelPrefix,
			noDataMessage,
			displayOverrides,
			None,
			storeBarLogos,
			'store-' + orderMode
		),
		'genres': buildStackedYearChart(
			gameData,
			yearExtractor,
			lambda entry: normalizeGenre(entry['Genre']),
			genreOrder,
			genreColors,
			'year-chart',
			labelPrefix,
			noDataMessage,
			displayOverrides,
			None,
			None,
			'genres-' + orderMode
		)
	}
yearlyChartSwitcher = buildYearlyChartSwitcher(chartsByOrderAndMode, platformLegend, storeLegend)
playedGenreHeatmap = playedYearGenreHeatmap(gameData)

fin = open('statistics.template', 'r')
statisticsTemplate = fin.read()
fin.close()

statisticsHtml = (
	statisticsTemplate
	.replace('REPLACE_PLATFORM_ROWS', platformRows)
	.replace('REPLACE_YEARLY_DYNAMIC', yearlyChartSwitcher)
	.replace('REPLACE_PLAYED_GENRE_HEATMAP', playedGenreHeatmap)
	.replace('REPLACE_GENRE_ROWS', genreRows)
)

fout = open('statistics.html', 'w')
fout.write(statisticsHtml)
fout.close()
