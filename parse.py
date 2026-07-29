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
	return value.strip()


def isGoldEntry(entry):
	value = entry.get('GOTY')
	if value is None:
		return False
	return str(value).strip() != ''


def countByPlatform(gameData):
	counter = Counter()
	for entry in gameData:
		counter[normalizeCategory(entry['Platform'])] += 1
	return sorted(counter.items(), key=lambda x: x[0].lower())


def countByReleaseYear(gameData):
	counter = Counter()
	for entry in gameData:
		year = int(entry['Release date'])
		counter[year] += 1
	return sorted(counter.items(), key=lambda x: x[0], reverse=True)


def buildBarChart(dataPoints, className, ariaLabel, labelEvery=1):
	if len(dataPoints) == 0:
		return '<p>No data available.</p>'

	leftPad = 50
	rightPad = 16
	topPad = 16
	bottomPad = 58
	barWidth = 10
	barGap = 3
	plotHeight = 220
	plotWidth = len(dataPoints) * (barWidth + barGap) - barGap

	values = [count for _, count in dataPoints]
	maxCount = max(values)
	if maxCount == 0:
		maxCount = 1

	svgWidth = leftPad + plotWidth + rightPad
	svgHeight = topPad + plotHeight + bottomPad

	out = ''
	out += '<svg class="bar-chart ' + className + '" viewBox="0 0 ' + str(svgWidth) + ' ' + str(svgHeight) + '" preserveAspectRatio="xMidYMax meet" role="img" aria-label="' + escape(ariaLabel, quote=True) + '">\n'
	out += '<line class="axis" x1="' + str(leftPad) + '" y1="' + str(topPad) + '" x2="' + str(leftPad) + '" y2="' + str(topPad + plotHeight) + '"/>\n'
	out += '<line class="axis" x1="' + str(leftPad) + '" y1="' + str(topPad + plotHeight) + '" x2="' + str(leftPad + plotWidth) + '" y2="' + str(topPad + plotHeight) + '"/>\n'
	out += '<text x="' + str(leftPad - 6) + '" y="' + str(topPad + 4) + '" text-anchor="end">' + str(maxCount) + '</text>\n'
	out += '<text x="' + str(leftPad - 6) + '" y="' + str(topPad + plotHeight + 4) + '" text-anchor="end">0</text>\n'

	for index, item in enumerate(dataPoints):
		xLabel = str(item[0])
		count = item[1]
		barHeight = int((count / maxCount) * plotHeight)
		x = leftPad + index * (barWidth + barGap)
		y = topPad + plotHeight - barHeight

		label = 'game'
		if count != 1:
			label = 'games'
		tooltip = xLabel + ': ' + str(count) + ' ' + label
		out += '<rect class="bar" x="' + str(x) + '" y="' + str(y) + '" width="' + str(barWidth) + '" height="' + str(barHeight) + '" data-tooltip="' + escape(tooltip, quote=True) + '" aria-label="' + escape(tooltip, quote=True) + '"></rect>\n'

		if index == 0 or index == len(dataPoints) - 1 or index % labelEvery == 0:
			labelX = x + (barWidth / 2)
			labelY = topPad + plotHeight + 15
			out += '<text x="' + str(labelX) + '" y="' + str(labelY) + '" text-anchor="start" transform="rotate(60 ' + str(labelX) + ' ' + str(labelY) + ')">' + escape(xLabel) + '</text>\n'

	out += '</svg>'
	return out


def releaseYearChart(gameData):
	totalCounts = Counter()
	goldCounts = Counter()
	for entry in gameData:
		year = int(entry['Release date'])
		totalCounts[year] += 1
		if isGoldEntry(entry):
			goldCounts[year] += 1

	if len(totalCounts) == 0:
		return '<p>No release-year data available.</p>'

	startYear = min(totalCounts.keys())
	endYear = datetime.now().year
	years = list(range(startYear, endYear + 1))
	totals = [totalCounts.get(year, 0) for year in years]
	maxCount = max(totals)
	if maxCount == 0:
		maxCount = 1

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

	out = ''
	out += '<svg class="bar-chart release-year-chart" viewBox="0 0 ' + str(svgWidth) + ' ' + str(svgHeight) + '" preserveAspectRatio="xMidYMax meet" role="img" aria-label="Games by release year from ' + str(startYear) + ' to ' + str(endYear) + '">\n'
	out += '<line class="axis" x1="' + str(leftPad) + '" y1="' + str(topPad) + '" x2="' + str(leftPad) + '" y2="' + str(topPad + plotHeight) + '"/>\n'
	out += '<line class="axis" x1="' + str(leftPad) + '" y1="' + str(topPad + plotHeight) + '" x2="' + str(leftPad + plotWidth) + '" y2="' + str(topPad + plotHeight) + '"/>\n'
	out += '<text x="' + str(leftPad - 6) + '" y="' + str(topPad + 4) + '" text-anchor="end">' + str(maxCount) + '</text>\n'
	out += '<text x="' + str(leftPad - 6) + '" y="' + str(topPad + plotHeight + 4) + '" text-anchor="end">0</text>\n'

	for index, year in enumerate(years):
		totalCount = totalCounts.get(year, 0)
		goldCount = goldCounts.get(year, 0)
		totalBarHeight = 0
		if totalCount > 0:
			totalBarHeight = max(1, int((totalCount / maxCount) * plotHeight))

		x = leftPad + index * (barWidth + barGap)
		barTop = topPad + plotHeight - totalBarHeight

		gamesLabel = 'game'
		if totalCount != 1:
			gamesLabel = 'games'
		tooltip = str(year) + ': ' + str(totalCount) + ' ' + gamesLabel + ', ' + str(goldCount) + ' gold'

		goldBarHeight = 0
		if goldCount > 0 and totalBarHeight > 0:
			goldBarHeight = int((goldCount / maxCount) * plotHeight)
			goldBarHeight = max(2, goldBarHeight)
			goldBarHeight = min(totalBarHeight, goldBarHeight)

		nonGoldBarHeight = totalBarHeight - goldBarHeight

		if nonGoldBarHeight > 0:
			nonGoldY = barTop + goldBarHeight
			out += '<rect class="bar bar-base" x="' + str(x) + '" y="' + str(nonGoldY) + '" width="' + str(barWidth) + '" height="' + str(nonGoldBarHeight) + '" data-tooltip="' + escape(tooltip, quote=True) + '" aria-label="' + escape(tooltip, quote=True) + '"></rect>\n'

		if goldBarHeight > 0:
			out += '<rect class="bar bar-gold" x="' + str(x) + '" y="' + str(barTop) + '" width="' + str(barWidth) + '" height="' + str(goldBarHeight) + '" data-tooltip="' + escape(tooltip, quote=True) + '" aria-label="' + escape(tooltip, quote=True) + '"></rect>\n'

		if index == 0 or year == endYear or year % 5 == 0:
			labelX = x + (barWidth / 2)
			labelY = topPad + plotHeight + 15
			out += '<text x="' + str(labelX) + '" y="' + str(labelY) + '" text-anchor="start" transform="rotate(60 ' + str(labelX) + ' ' + str(labelY) + ')">' + str(year) + '</text>\n'

	out += '</svg>'
	return out


def platformChart(gameData):
	platformData = countByPlatform(gameData)
	return buildBarChart(platformData, 'platform-chart', 'Games by platform', labelEvery=1)


def countByGenre(gameData):
	counter = Counter()
	for entry in gameData:
		counter[normalizeCategory(entry['Genre'])] += 1
	return sorted(counter.items(), key=lambda x: (-x[1], x[0].lower()))


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
for x in gameData:
	gameDataStr += entryToTableRow(x)

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
releaseYearChartSvg = releaseYearChart(gameData)

fin = open('statistics.template', 'r')
statisticsTemplate = fin.read()
fin.close()

statisticsHtml = (
	statisticsTemplate
	.replace('REPLACE_PLATFORM_ROWS', platformRows)
	.replace('REPLACE_RELEASE_YEAR_CHART', releaseYearChartSvg)
	.replace('REPLACE_GENRE_ROWS', genreRows)
)

fout = open('statistics.html', 'w')
fout.write(statisticsHtml)
fout.close()
