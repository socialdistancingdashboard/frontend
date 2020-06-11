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
from .get_airquality_desc import get_airquality_desc

@st.cache(ttl=43200) # time-to-live: 12h
def load_topojson():
    #url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'
    url_topojson = 'https://images.everyonecounts.de/germany.json'
    r = requests.get(url_topojson)
    jsondump = r.json()
    county_names = []
    county_ids = []
    for county in jsondump["objects"]["counties"]["geometries"]:
        county_names.append(county["properties"]["name"] + " (" + county["properties"]["districtType"]+")")
        county_ids.append(county["id"])
    state_names = []
    state_ids = []
    for state in jsondump["objects"]["states"]["geometries"]:
        state_names.append(state["properties"]["name"])
        state_ids.append(state["id"])
    return county_names, county_ids, state_names, state_ids

@st.cache(ttl=43200) # time-to-live: 12h
def load_real_data():
    response = requests.get('https://im6qye3mc3.execute-api.eu-central-1.amazonaws.com/prod')
    jsondump = response.json()["body"]
    county_names, county_ids,_,_ = load_topojson()
    id_to_name = {cid:county_names[idx] for idx,cid in enumerate(county_ids)}
    
    # get names for all scores
    scorenames = []
    for (date, row) in list(jsondump.items()):
        for cid, scores in row.items():
            for key in scores.keys():
                if key not in scorenames:
                    scorenames.append(key)
    scorenames = [key for key in scorenames if '_score' in key]
    
    # prepare lists
    scorevalues = {scorename:[] for scorename in scorenames}
    ids = []
    names = []
    dates = []
    
    # loop over data
    for (date, row) in list(jsondump.items()):
        for cid, scores in row.items():
            try:
                names.append(id_to_name[cid])
            except:
                continue
            ids.append(cid)
            dates.append(date)
            for scorename in scorenames:
                if scorename in scores:
                    scorevalue = scores[scorename]*100
                else:
                    scorevalue = None
                scorevalues[scorename].append(scorevalue)
            
    
    # create dataframe
    df_scores = pd.DataFrame({
        "id": ids, 
        "name": names, 
        "date": dates
    })
    
    # add scores (but not all)
    hidden_scores = [
                    "zug_score",
                    "bus_score",
                    "national_score",
                    "suburban_score",
                    "regional_score",
                    "nationalExpress_score"
                    ] # hacky way to filter out certain scores
    scorenames = [s for s in scorenames if s not in hidden_scores]
    
    for scorename in scorenames:
        df_scores[scorename] = scorevalues[scorename]
    df_scores = df_scores.replace([np.inf, -np.inf], np.nan)
    
    df_scores["airquality_desc"] = df_scores.apply(lambda x: get_airquality_desc(x["airquality_score"]),axis=1)
    
    return df_scores, scorenames
    
@st.cache(ttl=43200) # time-to-live: 12h
def get_map(df_scores,selected_score,selected_score_axis, selected_score_desc, use_states,latest_date):
    #url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'
    url_topojson = 'https://images.everyonecounts.de/germany.json'
    MAPHEIGHT = 640
    if use_states:
        features = 'states'
        sw = 1
    else:
        features = 'counties'
        sw = 0.2
        # overlay state boundaries with thicker lines
        data_topojson_remote_states = alt.topo_feature(url=url_topojson, feature='states')
        overlaymap = alt.Chart(data_topojson_remote_states).mark_geoshape(
            fill=None,
            stroke='white',
            strokeWidth=1.5
        ).properties(width='container',height = MAPHEIGHT)
    data_topojson_remote = alt.topo_feature(url=url_topojson, feature=features)
   
    basemap = alt.Chart(data_topojson_remote).mark_geoshape(
            fill='lightgray',
            stroke='white',
            strokeWidth=sw
        ).properties(width='container',height = MAPHEIGHT)
        
    title= {
        "text": ["", selected_score_desc], # use two lines as hack so the umlauts at Ö are not cut off
        "subtitle": "EveryoneCounts.de",
        "color": "black",
        "subtitleColor": "lightgray",
        "subtitleFontSize":12,
        "subtitleFontWeight":"normal",
        "fontSize":15,
        "lineHeight":5,
    }
    
    # COLORS
    if selected_score=="webcam_score":
        colorscale = alt.Scale(scheme='blues')
        color=alt.Color(selected_score+':Q', 
                                title=selected_score_axis, 
                                scale=colorscale,
                                legend=None)
    elif selected_score=="airquality_score":
        colorscale = alt.Scale(domain=(200, 0),scheme='redyellowgreen')
        color=alt.Color('airquality_score:Q', 
                                title=selected_score_axis, 
                                scale=colorscale,
                                legend=None)
    else:
        colorscale = alt.Scale(domain=(200, 0), scheme='redyellowgreen')
        color=alt.Color(selected_score+':Q', 
                                title=selected_score_axis, 
                                scale=colorscale,
                                legend=None)
    
    # TOOLTIPS
    if use_states:
        titlestr = "Bundesland"
    else:
        titlestr = "Landkreis"
    
    tooltip=[alt.Tooltip("name:N", title=titlestr),
             alt.Tooltip(selected_score+":Q", title=selected_score_axis)]
    if selected_score=="airquality_score":
        tooltip.append(alt.Tooltip("airquality_desc:N", title="Beschreibung"))
    
    
    df_scores_lookup = df_scores[(df_scores["date"] == str(latest_date)) & (df_scores[selected_score] >= 0)]
    
    layer = alt.Chart(data_topojson_remote).mark_geoshape(
            stroke='white',
            strokeWidth=sw
        ).encode(
            color=color,
            tooltip=tooltip
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores_lookup, 'id', [selected_score])
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores_lookup, 'id', ['name'])
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores_lookup, 'id', ['airquality_desc'])
        ).properties(
            width='container',
            height = MAPHEIGHT,
            title=title
        )
    
    if use_states:
        c = alt.layer(basemap, layer).configure_view(strokeOpacity=0)
    else:
        c = alt.layer(basemap, layer, overlaymap).configure_view(strokeOpacity=0)
    return c
    
@st.cache(ttl=43200) # time-to-live: 12h
def get_timeline_plots(df_scores, selected_score, selected_score_axis, selected_score_desc, use_states, countys):
    
    title= {
        "text": ["", selected_score_desc], # use two lines as hack so the umlauts at Ö are not cut off
        "subtitle": "EveryoneCounts.de",
        "color": "black",
        "subtitleColor": "lightgray",
        "subtitleFontSize":12,
        "subtitleFontWeight":"normal",
        "fontSize":15,
        "lineHeight":5,
    }
    if use_states:
        titlestr = "Bundesland"
        scheme='category20'
    else:
        titlestr = "Landkreis"
        scheme='category10'
    
    if len(countys) > 0 and not use_states:
        # Landkreise
        df_scores = df_scores[df_scores["name"].isin(countys)].dropna(axis=1, how="all")
        df_scores = df_scores[["name", "date", selected_score]].dropna()
    elif use_states:
        pass
    else:
        return None # county mode, nothing selected
    
    # altair selectors    
    highlight = alt.selection_single(empty="none", fields=['name'], on='mouseover', nearest=True, clear="mouseout")
    highlight_circles = alt.selection_single(empty="none", fields=['date','name'], on='mouseover', nearest=True, clear="mouseout")    
    
    # charts
    base = alt.Chart(df_scores[["name", "date", selected_score]].dropna()).encode(
            x=alt.X('date:T', axis=alt.Axis(title='Datum', format=("%d %b"))),
            y=alt.Y(selected_score+':Q', title=selected_score_axis),
            color=alt.Color('name', title=titlestr, scale=alt.Scale(scheme=scheme), legend=alt.Legend(orient="bottom",columns=2)),
            tooltip=[
                alt.Tooltip("name:N", title=titlestr),
                alt.Tooltip(selected_score+":Q", title=selected_score_axis),
                alt.Tooltip("date:T", title="Datum", format=("%A %d %B")),
                ]
        )
    
    points = base.mark_circle().encode(
        opacity=alt.value(1),
        size=alt.condition(~highlight_circles, alt.value(40), alt.value(300)),
        ).add_selection(
            highlight
        ).add_selection(
            highlight_circles
        ).properties(
            width='container',
            height=450,
            title=title
        )
        
    lines = base.mark_line().encode(
        size=alt.condition(~highlight, alt.value(2), alt.value(6)),
        opacity=alt.condition(~highlight, alt.value(0.5), alt.value(1))
        )
        
    if selected_score in ["airquality_score","webcam_score","tomtom_score"]:
        return points+lines
    else:
        # add horizontal rule at 100%
        rule = alt.Chart(df_scores).mark_rule(color='lightgray').encode(
            y="a:Q"
        ).transform_calculate(
            a="100"
        )
        return rule+points+lines

@st.cache(ttl=43200,allow_output_mutation=True) # time-to-live: 12h
def get_histograms(df_scores_in,selected_score,selected_score_desc,selected_score_axis):
    
    # prepare dataframe
    df_scores = df_scores_in.copy()
    df_scores = df_scores[["date","name",selected_score]] # throw other scores away
    df_scores = df_scores.dropna(axis=0,how="any") # remove rows with NaN
    
    df_scores=df_scores.groupby(["name","date"]).mean().reset_index() # daily average in case of multiple datapoints per day
    df_scores["date"] = pd.to_datetime(df_scores["date"]) # make sure date column is datetime
    df_scores["date_str"] = df_scores["date"].apply(lambda x: x.strftime("%Y-%m-%d")) # date string column
     
    # use a date_id for lookup purposes
    dates = sorted(list(set(df_scores["date_str"])))
    date2idx = {i:v for v,i in enumerate(dates)}
    def date2id(x):
        try:
            return date2idx[x]
        except:
            return np.nan
    df_scores["date_id"] = df_scores["date_str"].apply(lambda x: date2id(str(x)))
    
    # median datframe
    df_median = df_scores.groupby("date").median().reset_index()
    
    maxval = max(df_scores[selected_score])
    maxval = 10*np.ceil(maxval/10)
    
    # plot title
    title= {
        "text": ["", "{}".format(selected_score_desc)], # use two lines as hack so the umlauts at Ö are not cut off
        "subtitle": "EveryoneCounts.de",
        "color": "black",
        "subtitleColor": "lightgray",
        "subtitleFontSize":12,
        "subtitleFontWeight":"normal",
        "fontSize":15,
        "lineHeight":5,
    }
    
    # special treatment for webcam score b/c it uses absolute values
    if selected_score=="webcam_score":
        scale=alt.Scale(domain=(1.05*maxval, 0),scheme="blues")
    else:
        scale=alt.Scale(domain=(200, 0),scheme="redyellowgreen")
    
    if selected_score=="tomtom_score":
        bin = alt.Bin(extent=[0, max(50,maxval)], step=max(50,maxval)/20)
    else:
        bin = alt.Bin(extent=[0, max(200,maxval)], step=max(200,maxval)/20)
    
    # Here comes the magic: a selector!
    selector = alt.selection_single(empty="none", fields=['date_id'], on='mouseover', nearest=True, init={'date_id': len(dates)-2})
    
    #--- Altair charts from here on ---#
    # Histogram chart
    chart = alt.Chart(df_scores).mark_bar(
            #clip=True
        ).encode(
        alt.X(
            selected_score+":Q",
            title=selected_score_axis,
            bin=bin
            ),
        alt.Y(
            'count():Q',
            title="Anzahl Landkreise",
            ),
        color = alt.Color(
            selected_score+":Q", 
            scale=scale,
            legend=None,
            ),
        ).transform_filter(
            selector
        ).properties(
            width='container',
            height=300,
            title=title
        )
    
    # Rule at 100%
    rule100 = alt.Chart(df_scores).mark_rule(color='lightgray',size=3).encode(
            x="a:Q"
        ).transform_calculate(
            a="100"
        )
    
    # Rule for the median
    rulemedian = alt.Chart(df_median).mark_rule(color='#F63366').encode(
        x=selected_score+":Q",
        size=alt.value(3),
        tooltip=[alt.Tooltip(selected_score+':Q', title="Median")]
    ).transform_filter(
            selector
    )
    
    # median plot
    median_points =alt.Chart(df_median).mark_point(
            filled=True, 
            size=150,
            color="gray",
        ).encode(
            alt.X("date:T", axis=alt.Axis(title='Datum', format=("%d %b"))),
            alt.Y(selected_score+':Q', title="Median "+selected_score_axis)
        ).properties(
                width='container',
                height=180,
                title= {
                    "text": "Wähle ein Datum:", 
                    "color": "black",
                    "fontWeight":"normal",
                    "fontSize":12
                }
        )
    selectorchart = alt.Chart(df_median).mark_point().encode(
        x='date:T',
        opacity=alt.value(0),
        tooltip=[
                alt.Tooltip("date:T", title="Datum", format=("%A %d %B")),
                alt.Tooltip(selected_score+":Q", title="Median")
                ]
        ).add_selection(
            selector
        )
    median_line =alt.Chart(df_median).mark_line(
            point=False,
            color="gray",
            size=1
        ).encode(
            alt.X("date:T"),
            alt.Y(selected_score+':Q'),
        ).properties(
            width='container',
        )
    median_selected =alt.Chart(df_median).mark_point(
            filled=True, 
            size=400,
            color="#F63366",
            opacity=0.7
        ).encode(
            alt.X("date:T"),
            alt.Y(selected_score+':Q'),
        ).properties(
            width='container',
        ).transform_filter(
            selector
        )
    median_selected_rule =alt.Chart(df_median).mark_rule(
            point=False,
            color="gray",
            size=1,
            opacity=1
        ).encode(
            alt.X("date:T"),
        ).properties(
            width='container',
        ).transform_filter(
            selector
        )
    median_selected_rule2 =alt.Chart(df_median).mark_rule(
            point=False,
            color="#F63366",
            size=1,
            opacity=1
        ).encode(
            alt.Y(selected_score+":Q"),
        ).properties(
            width='container',
        ).transform_filter(
            selector
        )
    
    if selected_score in ["airquality_score","webcam_score","tomtom_score"]:
        chart_top = chart+rulemedian
    else:
        chart_top = rule100+chart+rulemedian
    chart_bottom = median_selected_rule+median_line+median_points+median_selected+median_selected_rule2+selectorchart
    return chart_top & chart_bottom



def detail_score_selector(df_scores_in, scorenames_desc, scorenames_axis, allow_county_select, allow_detail_select, key, default_detail_index=0, default_score="hystreet_score"):
    df_scores = df_scores_in.copy()
    
    # get counties
    county_names, county_ids, state_names, state_ids = load_topojson()
    id_to_name = {cid:county_names[idx] for idx,cid in enumerate(county_ids)}
    state_id_to_name = {cid:state_names[idx] for idx,cid in enumerate(state_ids)}
    state_name_to_id = {state_names[idx]:cid for idx,cid in enumerate(state_ids)}
    
    st_desc = st.empty()
    
    # LEVEL OF DETAIL SELECT
    if allow_detail_select:
        use_states_select  = st.radio('Detailgrad:', 
                                        ('Bundesländer', 'Landkreise'), 
                                        index =default_detail_index,
                                        key = key
                                        )
    else:
        use_states_select =  'Landkreise'
    use_states = use_states_select == 'Bundesländer'
    
    # SCORE SELECT
    sorted_desc = sorted(list(scorenames_desc.values()))
    selected_score_desc = st.selectbox(
        'Datenquelle:', sorted_desc, 
        index = sorted_desc.index(scorenames_desc[default_score]), # default value in sorted list
        key = key
    )
    inverse_scorenames_desc = {scorenames_desc[key]:key for key in scorenames_desc.keys()}
    selected_score = inverse_scorenames_desc[selected_score_desc]
    if selected_score == "webcam_score":
        selected_score_axis = scorenames_axis[selected_score] + ' pro Stunde' # absolute values
    elif selected_score == "airquality_score":
        selected_score_axis = scorenames_axis[selected_score] + ' (AQI)' # absolute values
    else:
        selected_score_axis = scorenames_axis[selected_score] + ' (%)'
    
    latest_date = pd.Series(df_scores[df_scores[selected_score] > 0]["date"]).values[-1]

    # COUNTY SELECT
    if (not use_states) and allow_county_select:
        available_countys = [value for value in county_names if value in df_scores[df_scores[selected_score] >= 0]["name"].values]
        if len(available_countys) > 1:
            default=available_countys[:2]
        else:
            default = []
        countys = st.multiselect('Wähle Landkreise aus:',
                                    options = available_countys, 
                                    default=default,
                                    key = key
                                )
    else:
        countys = []
    
    # Show additional information text for certain scores
    desc = ""
    if selected_score in ["webcam_score","airquality_score","tomtom_score"]:
        desc += '''
                
        Für diesen Datensatz besitzen wir leider keine Referenz-Daten vor der COVID-Pandemie, daher werden **Absolutwerte** angezeigt und Werte zwischen {regionen}n lassen sich nicht vergleichen.
        '''.format(regionen=use_states_select)
    if selected_score == "airquality_score":
        desc += '''
                
        Die Daten kommen vom [World Air Quality Project](https://aqicn.org/here/de/) und die Skala richtet sich nach dem ["Air Quality Index" (AQI)](https://aqicn.org/scale/de/).
        '''
    elif selected_score == "tomtom_score":
        desc += '''
                
        Die Daten stammen vom [TomTom Traffic Index](https://www.tomtom.com/). Die Prozentangaben beschreiben die Zeit, die man aufgrund der Verkehrslage länger unterwegs ist als auf einer komplett freien Straße. Ein Wert von 50% bedeutet also, dass man für einen Trip, der normalerweise 30 Minuten dauern würde, aufgrund der Verkehrslage 15 Minuten mehr benötigt, nämlich 45 Minuten. ([Quelle](https://www.tomtom.com/en_gb/traffic-index/about/))
        '''
    st_desc.markdown(desc,unsafe_allow_html=True)
        
     # Prepare df_scores according to Landkreis/Bundesland selection
    if use_states:
        # aggregate state data
        df_scores['state_id'] = df_scores.apply(lambda x: str(x['id'])[:2],axis=1) # get state id (first two letters of county id)
        df_scores['name'] = df_scores.apply(lambda x: state_id_to_name[x['state_id']],axis=1) # get state name
        df_scores = df_scores.groupby(['name','date']).mean() # group by state and date, calculate mean scores
        df_scores = df_scores.round(1) #round
        df_scores['id'] = df_scores.apply(lambda x: state_name_to_id[x.name[0]],axis=1) # re-add state indices
        df_scores = df_scores.replace([np.inf, -np.inf], np.nan) # remove infs
        df_scores = df_scores.reset_index() # make index columns into regular columns
        df_scores["airquality_desc"] = df_scores.apply(lambda x: get_airquality_desc(x["airquality_score"]),axis=1)

    df_scores["date"] = pd.to_datetime(df_scores["date"])
    df_scores = df_scores.round(1)
    
    return (df_scores,selected_score, selected_score_desc, selected_score_axis, use_states, use_states_select, countys, latest_date)



def dashboard():
    ''' Main code to display the streamlit dashboard '''

    # get score data
    df_scores_full, scorenames = load_real_data()
   
    # descriptive names for each score
    scorenames_desc_manual = {
        "gmap_score":"Menschen an Haltestellen des ÖPNV",
        "gmap_supermarket_score":"Besucher in Supermärkten",
        "hystreet_score":"Fußgänger in Innenstädten",
        "zug_score":"DB Züge",
        "bike_score":"Fahrradfahrer",
        "bus_score":"ÖPV Busse",
        "national_score":"ÖPV IC-Züge",
        "suburban_score":"ÖPV Nahverkehr",
        "regional_score":"ÖPV Regionalzüge",
        "nationalExpress_score":"ÖPV ICE-Züge",
        "webcam_score":"Fußgänger auf öffentlichen Webcams",
        "tomtom_score":"Autoverkehr",
        "airquality_score":"Luftqualität"
        }
    # very short axis labels for each score
    scorenames_axis_manual = {
        "gmap_score":"Menschen",
        "gmap_supermarket_score":"Besucher",
        "hystreet_score":"Fußgänger",
        "zug_score":"Züge",
        "bike_score":"Fahrradfahrer",
        "bus_score":"Busse",
        "national_score":"IC-Züge",
        "suburban_score":"Nahverkehr",
        "regional_score":"Regionalzüge",
        "nationalExpress_score":"ICE-Züge",
        "webcam_score":"Fußgänger",
        "tomtom_score":"Traffic Index",
        "airquality_score":"Luftqualität"
        }
    
    # for scores not in the hardcoded list above
    # default to their scorename as a fallback
    scorenames_desc = {}
    scorenames_axis = {}
    for scorename in scorenames:
        if scorename in scorenames_desc_manual:
            scorenames_desc[scorename] = scorenames_desc_manual[scorename]
        else:
            scorenames_desc[scorename] = scorename
        if scorename in scorenames_axis_manual:
            scorenames_axis[scorename] = scorenames_axis_manual[scorename]
        else:
            scorenames_axis[scorename] = scorename
    
    
    st.markdown('''
        Die Maßnahmen gegen COVID19 wie Kontaktverbote und geschlossene Geschäfte haben große Änderungen in unserem Alltag mit sich gebracht. Wir sehen dies jeden Tag wenn wir vor die Haustür gehen. Aber wie ist die Lage im Rest des Landes? Wird Social Distancing überall gleich strikt befolgt? Sinkt die Zurückhaltung am Wochenende oder bei guten Wetter? Sind tatsächlich mehr/weniger Menschen im Park unterwegs? Diese Fragen sind sehr schwer direkt zu beantworten, aber wir können versuchen, **indirekt** Erkentnisse darüber zu gewinnen indem wir verschiedene Indikatoren betrachten.

        Dazu setzen wir auf unterschiedliche Datenquellen, um ein möglichst umfassendes Bild zu zeichnen. 
        Wo es möglich ist, berechnen wir einen einfach verständlichen relativen Wert. Dabei entspricht **100%  dem Normal-Wert vor der COVID19-Pandemie**, also bevor die Bürger zu Social Distancing aufgerufen wurden. Ein kleiner Wert weist darauf hin, dass in unserer Datenquelle eine Verringerung der Aktivität gemessen wurde. Wenn eine relative Angabe nicht möglich ist (z.B. weil unsere Daten nicht weit genug in die Vergangenheit reichen um zu bestimmen was ein "normales" Aktivitätsniveau ist) werden absolute Werte angegeben.

        Im Folgenden kannst Du unseren Datensatz auf unterschiedliche Weise interaktiv erkunden:
        - <a href="#map">Aktuelle Deutschlandkarte</a>
        - <a href="#timeline">Zeitlicher Verlauf</a>
        - <a href="#histogram">Verteilung über alle Landkreise</a>
    ''',unsafe_allow_html=True)

    # MAP DESCRIPTION
    st_map_desc        = st.empty()
    
    # Selection box for the map
    df_scores, selected_score, selected_score_desc, selected_score_axis, use_states, use_states_select, countys, latest_date = detail_score_selector(df_scores_full, 
                                        scorenames_desc, 
                                        scorenames_axis, 
                                        allow_county_select=False,
                                        allow_detail_select=True,
                                        key='map',
                                        default_detail_index=0,
                                        default_score="gmap_score"
                                        )
    
    st_map_desc.markdown('''
        ---
        ## Aktuelle Karte vom {datum}<span id="map"></span>    
        In der Karte siehst Du wie sich die COVID-19-Maßnahmen auf die verschiedenen **{regionen}** in Deutschland auswirkt. Angezeigt werden Daten über **{datasource}**. Du kannst die Datenquelle über die Schaltflächen ändern.
    '''.format(regionen=use_states_select,
               datasource=selected_score_desc,
               datum=datetime.datetime.strptime(latest_date,"%Y-%m-%d").strftime("%d.%m.%Y")),
        unsafe_allow_html=True)
    
    # DRAW MAP
    map = get_map(df_scores, selected_score, selected_score_axis, selected_score_desc, use_states, latest_date)
    map2 = map.copy() # otherwise streamlit gives a Cached Object Mutated warning
    st.altair_chart(map2)
    
    # MAP LEGEND
    if selected_score=="airquality_score":
        st.image("images/legende_airquality.png")
    elif selected_score in ["webcam_score","tomtom_score"]:
        pass # no legend
    else:
        st.image("images/legende.png") 
    
    # TIMELINE DESCRIPTION    
    st_timeline_desc   = st.empty()
    
    # Selection box for the timeline
    df_scores2, selected_score2, selected_score_desc2, selected_score_axis2, use_states2, use_states_select2, countys2, latest_date2 = detail_score_selector(df_scores_full, 
                                        scorenames_desc, 
                                        scorenames_axis, 
                                        allow_county_select=True,
                                        allow_detail_select=True,
                                        key='timeline',
                                        default_detail_index=1,
                                        default_score="hystreet_score"
                                        )
    
    
    st_timeline_desc.markdown('''
        ---
        ## Zeitlicher Verlauf <span id="timeline"></span>   
        Hier kannst Du den zeitlichen Verlauf der gewählten Datenquelle für verschiedene **{regionen}** in Deutschland vergleichen. Angezeigt werden Daten über **{datasource}**. Du kannst die Datenquelle über die Schaltflächen ändern.
        
        **Sieh doch mal nach wie die Lage in Deiner Region ist!**
    '''.format(regionen=use_states_select2,
               datasource=selected_score_desc2),
        unsafe_allow_html=True
    )
        
    timeline = get_timeline_plots(df_scores2, selected_score2, selected_score_axis2, selected_score_desc2, use_states2, countys2)
    if timeline is not None:
        timeline2 = timeline.copy() # otherwise streamlit gives a Cached Object Mutated warning
        st.altair_chart(timeline2)


    # DRAW HISTOGRAMS
    # ===============
    st_histo_desc = st.empty()
    
    # Selection box for the timeline
    df_scores3, selected_score3, selected_score_desc3, selected_score_axis3, use_states3, use_states_select3, countys3, latest_date3 = detail_score_selector(df_scores_full, 
                                        scorenames_desc, 
                                        scorenames_axis, 
                                        allow_county_select=False,
                                        allow_detail_select=False,
                                        key='histo',
                                        default_score="hystreet_score"
                                        )
                                        
    st_histo_desc.markdown('''
        ---
        ## Verteilung über alle Landkreise <span id="histogram"></span>
        Hier kannst Du einen Überblick bekommen, wie die Verteilung der Daten über **{datasource}** für alle verfügbaren Landkreise ist. Du kannst die Datenauswahl weiter unten im Menü ändern. 
        
        Die pinke Linie ist der **Median**, das heißt jeweils die Hälfte aller Landkreise hat einen höheren beziehungswiese niedrigeren Score als dieser Wert. Im unteren Graph ist der zeitliche Verlauf des Medians dargestellt. **In diesem Graph kannst Du das Datum auswählen, für welches Dir die Verteilung über alle Landkreise angezeigt wird.**
        '''.format(datasource=selected_score_desc3), unsafe_allow_html=True
        )
    c=get_histograms(df_scores3, selected_score3, selected_score_desc3, selected_score_axis3)
    st.altair_chart(c)
    st.markdown('''
        Zur zeitlichen Einordung: Die [Vereinbarung zwischen der Bundesregierung und den Regierungschefinnen und Regierungschefs der Bundesländer angesichts der Corona-Epidemie in Deutschland](https://www.bundeskanzlerin.de/bkin-de/aktuelles/vereinbarung-zwischen-der-bundesregierung-und-den-regierungschefinnen-und-regierungschefs-der-bundeslaender-angesichts-der-corona-epidemie-in-deutschland-1730934) wurde am 16. März veröffentlicht.
    ''')
    

    
    
    # tracking javascript
    st.markdown("""   
    <!-- Matomo Image Tracker-->
    <img src="https://matomo.everyonecounts.de/matomo.php?idsite=1&amp;rec=1&amp;action_name=Dashboard" style="border:0" alt="" />
    <!-- End Matomo -->
    """, unsafe_allow_html=True)
