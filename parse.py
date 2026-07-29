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


def genreColor(index):
	hue = (index * 137) % 360
	return 'hsl(' + str(hue) + ', 62%, 52%)'


def buildGenrePalette(gameData):
	genreCounts = Counter()
	for entry in gameData:
		genreCounts[normalizeGenre(entry['Genre'])] += 1

	genres = sorted(genreCounts.items(), key=lambda x: (-x[1], x[0].lower()))
	order = [name for name, _ in genres]
	colors = {}

	for index, genre in enumerate(order):
		colors[genre] = genreColor(index)

	return order, colors


def buildLegend(items, colorMap, ariaLabel):
	if len(items) == 0:
		return ''

	legendItems = []
	for item in items:
		color = colorMap[item]
		swatch = '<span class="legend-swatch" style="background-color: ' + color + ';" aria-hidden="true"></span>'
		label = '<span class="legend-label">' + escape(item) + '</span>'
		legendItems.append('<span class="legend-item">' + swatch + label + '</span>')

	return '<div class="chart-legend" role="list" aria-label="' + escape(ariaLabel, quote=True) + '">' + ''.join(legendItems) + '</div>'


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
			out += '<rect class="bar bar-base' + adjustedClass + '" x="' + str(x) + '" y="' + str(nonGoldY) + '" width="' + str(barWidth) + '" height="' + str(nonGoldBarHeight) + '" data-tooltip="' + escape(tooltip, quote=True) + '" aria-label="' + escape(tooltip, quote=True) + '"></rect>\n'

		if goldBarHeight > 0:
			out += '<rect class="bar bar-gold' + adjustedClass + '" x="' + str(x) + '" y="' + str(barTop) + '" width="' + str(barWidth) + '" height="' + str(goldBarHeight) + '" data-tooltip="' + escape(tooltip, quote=True) + '" aria-label="' + escape(tooltip, quote=True) + '"></rect>\n'

		if index == 0 or year == endYear or year % 5 == 0:
			labelX = x + (barWidth / 2)
			labelY = topPad + plotHeight + 15
			out += '<text x="' + str(labelX) + '" y="' + str(labelY) + '" text-anchor="start" transform="rotate(60 ' + str(labelX) + ' ' + str(labelY) + ')">' + str(year) + '</text>\n'

	out += '</svg>'
	return out


def buildStackedYearChart(gameData, yearExtractor, categoryExtractor, categoryOrder, categoryColors, chartClassName, labelPrefix, noDataMessage, displayCountOverrides=None, otherBucket=None):
	totalCounts = Counter()
	categoryCountsByYear = {}
	selectedCategories = set(categoryOrder)

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

			color = categoryColors.get(category, '#4f81bd')
			out += '<rect class="bar bar-segment" x="' + str(x) + '" y="' + str(segmentY) + '" width="' + str(barWidth) + '" height="' + str(segmentHeight) + '" style="fill: ' + color + ';" data-tooltip="' + escape(tooltip, quote=True) + '" aria-label="' + escape(tooltip, quote=True) + '" tabindex="0"></rect>\n'
			currentY = segmentY

		if index == 0 or year == endYear or year % 5 == 0:
			labelX = x + (barWidth / 2)
			labelY = topPad + plotHeight + 15
			out += '<text x="' + str(labelX) + '" y="' + str(labelY) + '" text-anchor="start" transform="rotate(60 ' + str(labelX) + ' ' + str(labelY) + ')">' + str(year) + '</text>\n'

	out += '</svg>'
	return out


def releaseYearChart(gameData):
	return buildGoldYearChart(
		gameData,
		lambda entry: int(entry['Release date']),
		'release-year-chart',
		'release year',
		'No release-year data available.'
	)


def playedYearGoldChart(gameData):
	return buildGoldYearChart(
		gameData,
		lambda entry: entry['Finished'].year,
		'played-year-chart',
		'played year',
		'No played-year data available.',
		{1995: 40}
	)


def playedYearSystemsChart(gameData, platformOrder, platformColors):
	return buildStackedYearChart(
		gameData,
		lambda entry: entry['Finished'].year,
		lambda entry: normalizePlatform(entry['Platform']),
		platformOrder,
		platformColors,
		'played-year-chart',
		'played year',
		'No played-year data available.',
		{1995: 40},
		'Other'
	)


def playedYearGenresChart(gameData, genreOrder, genreColors):
	return buildStackedYearChart(
		gameData,
		lambda entry: entry['Finished'].year,
		lambda entry: normalizeGenre(entry['Genre']),
		genreOrder,
		genreColors,
		'played-year-chart',
		'played year',
		'No played-year data available.',
		{1995: 40}
	)


def buildPlayedYearSwitcher(goldSvg, systemsSvg, genresSvg, systemsLegend):
	out = ''
	out += '<div class="played-year-switcher" role="tablist" aria-label="Played year visualization mode">'
	out += '<button class="chart-mode-button active" type="button" data-played-view-button="gold" aria-pressed="true">Games + Gold</button>'
	out += '<button class="chart-mode-button" type="button" data-played-view-button="systems" aria-pressed="false">Systems</button>'
	out += '<button class="chart-mode-button" type="button" data-played-view-button="genres" aria-pressed="false">Genres</button>'
	out += '</div>'
	out += '<div class="played-year-view" data-played-view="gold">' + goldSvg + '</div>'
	out += '<div class="played-year-view chart-view-hidden" data-played-view="systems">' + systemsLegend + systemsSvg + '</div>'
	out += '<div class="played-year-view chart-view-hidden" data-played-view="genres">' + genresSvg + '</div>'
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
fin = open('games-played.template', 'r')
template = fin.read()
fin.close()

# Write generated HTML with data
htmldata = template.replace('REPLACE_TABLE_DATA', gameDataStr).replace('REPLACE_GAME_COUNT', str(len(gameData)))
fout = open('games-played.html', 'w')
fout.write(htmldata)
fout.close()

platformRows = statisticsRows(countByPlatform(gameData))
genreRows = statisticsRows(countByGenre(gameData))

platformOrder, platformColors = buildPlatformPalette(gameData)
platformLegend = buildLegend(platformOrder, platformColors, 'Platform colors')
genreOrder, genreColors = buildGenrePalette(gameData)

releaseYearChartSvg = releaseYearChart(gameData)
playedYearGoldSvg = playedYearGoldChart(gameData)
playedYearSystemsSvg = playedYearSystemsChart(gameData, platformOrder, platformColors)
playedYearGenresSvg = playedYearGenresChart(gameData, genreOrder, genreColors)
playedYearSwitcher = buildPlayedYearSwitcher(playedYearGoldSvg, playedYearSystemsSvg, playedYearGenresSvg, platformLegend)

fin = open('statistics.template', 'r')
statisticsTemplate = fin.read()
fin.close()

statisticsHtml = (
	statisticsTemplate
	.replace('REPLACE_PLATFORM_ROWS', platformRows)
	.replace('REPLACE_RELEASE_YEAR_CHART', releaseYearChartSvg)
	.replace('REPLACE_PLAYED_YEAR_DYNAMIC', playedYearSwitcher)
	.replace('REPLACE_GENRE_ROWS', genreRows)
)

fout = open('statistics.html', 'w')
fout.write(statisticsHtml)
fout.close()
