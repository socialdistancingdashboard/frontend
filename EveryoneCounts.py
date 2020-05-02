# -*- coding: utf-8 -*-

import streamlit as st

from pages import dashboard
# MAIN MENU HTML (this needs to be the first markdown block for the css to work!)
st.markdown('''
<a id="top"></a>
<div id="nav-container">
    <div id="logo">
        <img src="https://blog.everyonecounts.de/wp-content/uploads/2020/04/logo_with_medium_text-1980x434.png" alt="EveryoneCounts - Das Social Distancing Dashboard" />
    </div>
    <div id="nav">
        <a href="" id="dashboard">Dashboard</a>
        <a href="https://blog.everyonecounts.de/die-daten/">Die Daten</a>
        <a href="https://blog.everyonecounts.de/das-team/">Das Team</a>
        <a href="https://blog.everyonecounts.de/das-projekt/">Das Projekt</a>
        <a href="https://blog.everyonecounts.de/presseschau/">Presseschau</a>
    </div>
</div>
''', unsafe_allow_html=True)

 
# MAIN MENU CSS
st.markdown("""
<style type="text/css">


@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;800&display=swap');

*{
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, sans-serif;
}

div.decoration{
  display:none;
}

.main>.block-container {
  width:100vw;
  max-width:100vw !important;
  padding-top:30px !important;;
}
.element-container  {
    text-align: center;

}

.element-container>.Widget,
.element-container>.stMarkdown {
    min-width:200px;
    max-width:700px;
    width:700px;
    margin-left:auto !important;
    margin-right:auto !important;
    text-align: left;
}

fullScreenFrame {

  
}
.stVegaLiteChart {
    min-width:200px;
    max-width:700px;
    width:80%;
    margin:auto !important;
    padding:0px;
}

.image-container{
    max-width:600px;
    margin:auto;
}

.main>.block-container>div>div.element-container:first-child {
  max-width:100vw;
}
.main>.block-container>div>div.element-container:first-child div.stMarkdown{
  max-width:100vw;
}

#nav-container{
  max-width:93vw;
  margin:auto;
  flex-wrap: wrap;
  display:flex;
  align-items: center;
  justify-content: space-between;
}
#nav,#logo{
  margin:0px;
}

#nav{
  max-width:100vw;
  display: flex;
  flex-wrap: wrap;
  align-content:space-between;
}

#nav a{
  background:#FCBFCF;
  padding:10px;
  border-radius:4px;
  color:black;
  text-decoration:none;
  box-shadow:#ccc 0px 1px 3px;
  margin-left: 0.8em;
  margin-top:0.8em;
  

}
#nav a#dashboard {
  background:#F63366;
	color:white;
}

#nav a:hover{
  background:#F89;
}


#logo img{
  max-width:100%;
  width:410px;
}



</style>
""", unsafe_allow_html=True)

# additional css
st.markdown("""
<style type='text/css'>
    img {
        max-width: 99%;
        border-radius:5px;
    }
    
    ul {
        line-height:1.4em;
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
    #MainMenu.dropdown {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


# Insert custom CSS
# - prevent horizontal scrolling on mobile
# - restrict images to container width
# - restrict altair plots to container width
# - make inputs better visible
st.markdown("""
    <style type='text/css'>
        .block-container>div {
            width:100% !important;
            overflow:hidden !important;
        }
        .image-container {
            width: 99%;
        }
        img {
            max-width: 99%;
            margin:auto;
        }
        .stSelectbox div[data-baseweb="select"]>div,
        .stMultiSelect div[data-baseweb="select"]>div{
            border:1px solid #fcbfcf;
        }
    </style>
""", unsafe_allow_html=True)


# DASHBOARD
st.markdown("""
    <h1 style="font-size:5rem; font-weight:bold; text-align:center;color:#000;">Dashboard</h1>
""", unsafe_allow_html=True)
dashboard.dashboard()

# FOOTER
st.markdown("""
<hr>

    
<div id="footer">
    <div>
    <a href="https://blog.everyonecounts.de/impressum/">Impressum</a>
    </div>
    <div>
    <a href="https://twitter.com/DistancingDash">Twitter</a>
    <a href="https://github.com/socialdistancingdashboard/">Github</a> 
    <a href="mailto:kontakt@everyonecounts.de">E-Mail</a>
    <a href="https://blog.everyonecounts.de/">Blog</a>
    </div>
    <div><a href="#top">Nach oben &uarr;</a></div>
</div>
<hr>

<style type="text/css">
#footer{
  display:flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  width:100%;
}
p>a, li>a, #footer div a {
    color: #e22658 !important; 
}
#footer div a{
    margin-right:8px;
    margin-left:8px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)