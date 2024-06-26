#!/usr/bin/env python

# generate cv.md from inputs below and from html of talks (for easier formatting)

html_escape_table = {
    "<b>": "**",
    "</b>": "**",
    "<ul>": "",
    "</ul>": "",
    "  <li>": "*",
    " </li>": ""
    }


def replace_all(text):
    for i, j in html_escape_table.items():
        text = text.replace(i, j)
    return text


# YAML variables
md = """---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---
"""

md += """
{% include base_path %}

Education
======
* PhD in Materials Science and Mechanical Engineering, Harvard University, 2024
* MS in Materials Science and Mechanical Engineering, Harvard University, 2021
* BSc in Chemistry, Minor in Nuclear Science, Simon Fraser University, 2017

Professional experience
======
* 2024-current: Postdoctoral Fellow
  * Harvard University
  * School of Engineering and Applied Sciences
  * [Aziz Lab](https://aziz.seas.harvard.edu/)
  * Development of (electro)chemical open source software.

"""

# Skills
# ======
# * Skill 1
# * Skill 2
#   * Sub-skill 2.1
#   * Sub-skill 2.2
#   * Sub-skill 2.3
# * Skill 3

# Open source software
md += """
Open source software development
======
* `RFBzero`  [GitHub repo](https://github.com/ericfell/rfbzero)
  * Python package for microkinetic modeling of electrochemical cycling in redox flow batteries. Includes modules for different cycling protocols, organic electrolyte properties, and the option to include degradation mechanisms.
"""





md += """
Publications
======
<ul>{% for post in site.publications reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>

"""

md += """
Presentations
=====

"""

# talks formatting
talks_file = "../_pages/talks.html"

with open(talks_file, encoding='utf-8') as file:
    lines = file.readlines()

for line in lines[8:]:
    md += replace_all(line)

md += """
Teaching
======
* Teaching Fellow, Harvard ENG-SCI 181: Engineering Thermodynamics

"""

# Service and leadership
# ======
# *

# write to cv.md file in _pages
with open("../_pages/cv.md", 'w', encoding="utf-8") as f:
    f.write(md)






