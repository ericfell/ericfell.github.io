#!/usr/bin/env python

# # Publications markdown generator for academicpages
# 
# Takes bibtex of publications and converts them for use with [academicpages.github.io](academicpages.github.io).
# Can use Jupyter notebook ([see more info here](http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html)).
# 
# The core python code is also in `pubsFromBibs.py`. 
# Run either from the `markdown_generator` folder after replacing updating the publist dictionary with:
# * bib file names
# * specific venue keys based on your bib file preferences
# * any specific pre-text for specific files
# * Collection Name (future feature)
# 
# TODO: Make this work with other databases of citations, 
# TODO: Merge this with the existing TSV parsing solution

import os
from time import strptime

from pybtex.database.input import bibtex
import html
import re


# todo: incorporate different collection types rather than a catch all publications, requires other changes to template
# publist = {
#     "proceeding": {
#         "file" : "proceedings.bib",  # replace with .bib name
#         "venuekey": "booktitle",
#         "venue-pretext": "In the proceedings of ",
#         "collection" : {"name":"publications",
#                         "permalink":"/publication/"}
#
#     },
publist = {
    "journal": {
        "file": "publications.bib",  # include path to your .bib file, if in another directory
        "venuekey": "journal",
        "venue-pretext": "",
        "collection": {"name": "publications", "permalink": "/publication/"}
    } 
}

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    "--": "&ndash;",
    }


def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)


for pubsource in publist:
    parser = bibtex.Parser()
    bibdata = parser.parse_file(publist[pubsource]["file"])
    raw_bib = bibdata.to_string('bibtex').split("\n@article")

    # loop through the individual references in a given bibtex file
    for idx, bib_id in enumerate(bibdata.entries):
        # reset default date
        pub_year = "1900"
        pub_month = "01"
        pub_day = "01"

        b = bibdata.entries[bib_id].fields
        
        try:
            pub_year = f'{b["year"]}'

            # todo: this hack for month and day needs some cleanup
            if "month" in b.keys(): 
                if len(b["month"]) < 3:
                    pub_month = "0"+b["month"]
                    pub_month = pub_month[-2:]
                elif b["month"] not in range(12):
                    tmnth = strptime(b["month"][:3],'%b').tm_mon   
                    pub_month = "{:02d}".format(tmnth) 
                else:
                    pub_month = str(b["month"])
            if "day" in b.keys(): 
                pub_day = str(b["day"])
                
            pub_date = pub_year+"-"+pub_month+"-"+pub_day
            
            # strip out {} as needed (some bibtex entries that maintain formatting)
            clean_title = b["title"].replace("{", "").replace("}", "").replace("\\", "").replace(" ", "-")

            url_slug = re.sub("\\[.*\\]|[^a-zA-Z0-9_-]", "", clean_title)
            url_slug = url_slug.replace("--", "-")

            md_filename = (str(pub_date) + "-" + url_slug + ".md").replace("--", "-")
            html_filename = (str(pub_date) + "-" + url_slug).replace("--", "-")

            # Build Citation from text
            citation = ""

            # add authors to citation
            for author in bibdata.entries[bib_id].persons["author"]:

                first_name = author.first_names[0]
                middle_name = None if not author.middle_names else author.middle_names[0]
                # uncomment below if pre-last names exist i.e. 'van ...'
                # prelast_name = None if not author.prelast_names else author.prelast_names[0]
                last_name = " ".join([str(x) for x in author.last_names])
                full_name = first_name + " " + " ".join(filter(None, (middle_name, last_name)))

                # add bold highlighting for primary author
                if full_name == "Eric M. Fell":
                    full_name = "<b>Eric M. Fell</b>"

                citation = citation + " " + full_name + ", "

            # citation manuscript title
            citation = citation + "\"" + html_escape(b["title"].replace("{", "").replace("}", "").replace("\\", "")) + ".\""

            # add venue logic depending on citation type i.e. Journal name
            venue = publist[pubsource]["venue-pretext"] + b[publist[pubsource]["venuekey"]].replace("{", "").replace("}", "").replace("\\", "")
            # if "&" in venue:
            #     print(venue)
            #     venue = venue.replace("\&", "&amp;")
            # else:
            #     venue = venue.replace("\\", "")

            citation = citation + " " + html_escape(venue)
            # add publication year to citation
            # OG citation = citation + ", " + pub_year + "."
            citation = citation + ", " + f'{b["volume"]}, ' + f'{b["pages"]}, (' + pub_year + ")."

            # YAML variables
            md = "---\ntitle: \"" + html_escape(b["title"].replace("{", "").replace("}", "").replace("\\", "")) + '"\n'
            
            md += """collection: """ + publist[pubsource]["collection"]["name"]

            md += """\npermalink: """ + publist[pubsource]["collection"]["permalink"] + html_filename
            
            note = False
            if "note" in b.keys():
                if len(str(b["note"])) > 5:
                    md += "\nexcerpt: '" + html_escape(b["note"]) + "'"
                    note = True
            else:
                # gives option to add further text to generated .md
                md += """\nexcerpt: ''"""

            md += "\ndate: " + str(pub_date) 

            md += "\nvenue: '" + html_escape(venue) + "'"
            #md += "\nvenue: '" + venue + "'"
            
            url = False
            if "url" in b.keys():
                if len(str(b["url"])) > 5:
                    md += "\npaperurl: '" + b["url"] + "'"
                    url = True

            final_citation = html_escape(citation)
            if "&amp;amp;" in final_citation:
                final_citation = final_citation.replace("&amp;amp;", "&amp;")
            if "--" in final_citation:
                final_citation = final_citation.replace("--", "&ndash;")

            #md += "\ncitation: '" + html_escape(citation) + "'"
            md += "\ncitation: '" + final_citation + "'"

            md += "\n---"

            # Markdown description for individual page
            if note:
                md += "\n" + html_escape(b["note"]) + "\n"

            if url:
                md += "\n[Access paper here](" + b["url"] + "){:target=\"_blank\"}\n"

                md += "\nBibTeX citation\n"
                # generate markdown bash cell of bibtex citation
                add_bib = str(raw_bib[idx]).replace("\\\\", "\\")
                # adds a comma after final .bib entry in the bash markdown cell
                add_bib = add_bib.replace("\"\n", "\",\n")
                md += "\n```bash \n@article" + add_bib + "```\n"

            else:
                md += "\nUse [Google Scholar](https://scholar.google.com/scholar?q="+html.escape(clean_title.replace("-", "+"))+"){:target=\"_blank\"} for full citation"

            md_filename = os.path.basename(md_filename)

            with open("../_publications/" + md_filename, 'w', encoding="utf-8") as f:
                f.write(md)
            print(f'SUCCESSFULLY PARSED {bib_id}: \"', b["title"][:60], "..."*(len(b['title']) > 60), "\"")
        # field may not exist for a reference
        except KeyError as e:
            print(f'WARNING Missing Expected Field {e} from entry {bib_id}: \"', b["title"][:30], "..."*(len(b['title']) > 30), "\"")
            continue
