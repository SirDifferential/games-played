from datetime import datetime
import csv
import sys

def entryToTableRow(entry):
	try:
		out = ""
		if entry["GOTY"] != None:
			out = "<tr class=\"GOTY\">"
		else:
			out = "<tr>"
		out += "<td>" + entry["Game"] + "</td>"
		out += "<td>" + entry["Finished"].strftime("%Y-%m-%d") + "</td>"
		out += "<td>" + entry["Genre"] + "</td>"
		out += "<td>" + entry["Platform"] + "</td>"

		# Sanity check
		int(entry["Release date"])

		out += "<td>" + entry["Release date"] + "</td>"
		out += "<td>" + entry["Service"] + "</td>"
		out += "<td>" + entry["Review"].replace("\\n", "<br>").replace("\\'", '"') + "</td>"
		out += "</tr>\n"
	except Exception as e:
		print(e)
		print(entry)
		sys.exit(1)
	return out

# Read game data from CSV
fin = open("games-played.csv", "r")
data = fin.read().split("\n")
fin.close()

reader = csv.DictReader(data, quotechar='"')
gameData = []
row = ""

try:
	for row in reader:
		# Parse date to programmable time
		row["Finished"] = datetime.strptime(row["Finished"], "%d.%m.%Y")
		gameData.append(row)
except Exception as e:
	print(e)
	print(row)
	sys.exit(1)

gameData.sort(key=lambda x: x["Finished"], reverse=True)
gameDataStr = ""
for x in gameData:
	gameDataStr += entryToTableRow(x)

# Read HTML template
fin = open("games-played.template", "r")
template = fin.read()
fin.close()

# Write generated HTML with data
htmldata = template.replace("REPLACE_TABLE_DATA", gameDataStr).replace("REPLACE_GAME_COUNT", str(len(gameData)))
fout = open("games-played.html", "w")
fout.write(htmldata)
fout.close()
