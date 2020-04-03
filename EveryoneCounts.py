# -*- coding: utf-8 -*-
# Copyright 2018-2019 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An example of showing geographic data."""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime
import urllib
import json
import requests
from PIL import Image
from io import BytesIO

from pages import dashboard
from pages import dashboard_pages



# sidebar header
st.sidebar.image('images/logo_with_medium_text.png', use_column_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# sidebar menu
menuitems = {'Dashboard':1,
             'Die Daten':2,
             'Das Projekt':3,
             'Das Team':4
            }
menu = st.sidebar.radio('',list(menuitems.keys()), index=0)

# hack in some css to style the menu
# note: unsafe_allow_html is planned to be deprecated in future streamlit
# double braces for .format to work
st.markdown("""
    <style type='text/css'>
        div.row-widget.stRadio div[role='radiogroup']>label{{
            background:#FCBFCF;
            margin-bottom:2px;
            padding: 3px 10px 3px 3px;
            width:100%;
        }}
        div.row-widget.stRadio div[role='radiogroup']>label:nth-child({selected}){{
            background:#F63366 !important;
        }}
            div.row-widget.stRadio div[role='radiogroup']>label:nth-child({selected}) *{{
            color:white;
        }}
            div.row-widget.stRadio div[role='radiogroup']>label:hover{{
            background:#F89;
        }}
            div.row-widget.stRadio div[role='radiogroup']>label>div:first-child{{
            display:none;
        }}
        #MainMenu.dropdown {{
            display: none;
        }}
    </style>
    """.format(selected=menuitems[menu]), unsafe_allow_html=True)


# additional css
st.markdown("""
    <style type='text/css'>
        img {
            max-width: 99%;
            border-radius:5px;
        }
        
        /* improve visibility of collapsed menu button on mobile */
        .open-iconic[data-glyph="chevron-right"]:after {
            content: "Menü";
            margin-top:-3px;
            margin-left:5px;
            vertical-align: middle;
        }
        .open-iconic[data-glyph="chevron-right"] {
            vertical-align: middle;
            opacity:1 !important;
        }
        .--collapsed button {
            background: #F0F2F6;
            box-shadow: #fff 0px 0px 10px;
            border: 1px solid white;
        }
    </style>
    """, unsafe_allow_html=True)


# sidebar footer
st.sidebar.markdown("""


--- 

""", unsafe_allow_html=True)
st.sidebar.subheader("weitere Infos")
st.sidebar.markdown('''
- [@DistancingDash](https://twitter.com/distancingdash/)
- [Youtube](https://www.youtube.com/watch?v=pDgcbE-c31c&feature=youtu.be)
- [Devpost](https://devpost.com/software/12-social-distancing-dashboard)
- [Github](https://github.com/socialdistancingdashboard)
''')

st.sidebar.subheader("Pressestimmen")
st.sidebar.markdown('''
- [Tagesspiegel](https://www.tagesspiegel.de/wirtschaft/hackathon-im-netz-programmierer-tuefteln-an-loesungen-gegen-die-corona-krise/25670548.html)
- [SWR](https://www.swr.de/swraktuell/wie-deutschland-das-coronavirus-hackt-wirvsvirus-hackathon-100.html)
- [WDR](https://www1.wdr.de/nachrichten/themen/coronavirus/verkehr-innenstadt-corona-100.html)
- [Tagesthemen](https://www.youtube.com/watch?v=gXxTrZAFx04&t=1560)
- [Tagesschau](https://www.youtube.com/watch?v=donUKy8IGZw)
- [tagesschau.de](https://www.tagesschau.de/investigativ/ndr-wdr/datenanalyse-oeffentliches-leben-corona-101.html)
- [NDR](https://www.ndr.de/nachrichten/info/Corona-Besonders-die-Hamburger-befolgen-die-Kontaktsperre,coronavirus1006.html)
- [Mitteldeutsche Zeitung](https://twitter.com/seem28/status/1245239792390090752)
- [Kommune21](https://www.kommune21.de/meldung_33697)
''')

st.sidebar.subheader("Kontakt")
st.sidebar.markdown('''
- [@DistancingDash](https://twitter.com/distancingdash/)
- [kontakt@everyonecounts.de](mailto:kontakt@everyonecounts.de)
''')

# main content
if menuitems[menu]==1:
    dashboard.dashboard()
elif menuitems[menu]==2:
    dashboard_pages.st_markdown('pages/about_our_data.md')
elif menuitems[menu]==3:
    dashboard_pages.st_markdown('pages/about_us.md')
elif menuitems[menu]==4:
    dashboard_pages.st_markdown('pages/das_team.md')
    pass
#elif menu=='Impressum':
#    dashboard_pages.impressum()