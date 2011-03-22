#!/usr/bin/env python
from py2deb import Py2deb
from glob import glob

version="0.1.9"

p=Py2deb("wilocate")
p.author="Emilio Pinna"
p.mail="emilio.pinn@gmail.com"
p.description="""    
Wireless networks detection and geolocation tool.
"""
p.url = "http://code.google.com/p/wilocate/"
p.depends="bash, sudo, python-wxgtk2.6, python"
p.license="gpl"
p.section="utils"
p.arch="all"

p["/usr/share/applications"]=["install/wilocate.desktop|wilocate.desktop"]
p["/usr/share/wilocate"]=glob("wilocate.py") + glob("core/*") + glob("html/*.html") + glob("html/css/*.css") + glob("html/img/*") + glob("html/js/*.js")
#p["/usr/share/wilocate/core"]=glob("core/*")
#p["/usr/share/wilocate/html"]=glob("html/*.html")
#p["/usr/share/wilocate/html/css"]=glob("html/css/*.css")
#p["/usr/share/wilocate/html/img"]=glob("html/img/*")
#p["/usr/share/wilocate/html/js"]=glob("html/js/*.js")

p["/usr/bin"]=["install/wilocate|wilocate"]


p.generate(version,rpm=True,src=True)
