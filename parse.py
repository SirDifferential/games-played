from dateutil import parser
import csv

def entryToTableRow(entry):
	out = "<tr>"
	out += "<td>" + entry["Game"] + "</td>"
	out += "<td>" + entry["Finished"].strftime("%Y-%m-%d") + "</td>"
	out += "<td>" + entry["Genre"] + "</td>"
	out += "<td>" + entry["Platform"] + "</td>"
	out += "<td>" + entry["Release date"] + "</td>"
	out += "<td>" + entry["Service"] + "</td>"
	out += "<td>" + entry["Review"].replace("\\n", "<br>").replace("\\'", '"') + "</td>"
	out += "</tr>\n"
	return out

# Read game data from CSV
fin = open("games-played.csv", "r")
data = fin.read().split("\n")
fin.close()

reader = csv.DictReader(data, quotechar='"')
gameData = ""
for row in reader:
	# Parse date to programmable time
	try:
		row["Finished"] = parser.parse(row["Finished"])
	except Exception as e:
		print(row)
	gameData += entryToTableRow(row)

# Read HTML template
fin = open("games-played.template", "r")
template = fin.read()
fin.close()

# Write generated HTML with data
htmldata = template.replace("REPLACE_TABLE_DATA", gameData)
fout = open("games-played.html", "w")
fout.write(htmldata)
fout.close()
