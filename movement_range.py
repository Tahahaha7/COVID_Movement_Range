import numpy as np
import pandas as pd
from ipywidgets import interact, Dropdown
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.offline as py
import plotly.graph_objs as go
import mplleaflet, warnings
import datetime

warnings.simplefilter(action='ignore', category=UserWarning)

'''
Goal:
have every single major city represented with a time slider that shows
the change in relative mobility for the month of March, April, May, June, and July

Further offers to use this dataset against the COVID-19 records and the policies implimented.
Work can be carried away with other people that have already invested into COVID related topics in Algeria.

Source: https://dataforgood.fb.com/tools/movement-range-maps/
'''

np.unique(data.country)
link = 'C:/Users/Taha/Desktop/Facebook Algeria/Movement Range Maps/movement-range-2020-07-29.txt'
data = pd.read_csv(link, delimiter="\t", low_memory=False)

algeria = data[data.country=='DZA']
algeria = algeria.reset_index(drop=True)
algeria['ds'] = pd.to_datetime(algeria['ds'])

name = Dropdown(options = np.unique(algeria['polygon_name']))
@interact(Region = name)
def plot_movement(Region):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=algeria[algeria.polygon_name==Region].ds,
                             y=algeria[algeria.polygon_name==Region]\
                             .all_day_bing_tiles_visited_relative_change, 
                             mode='lines+markers', name='Relative Change'))
    
    fig.add_trace(go.Scatter(x=algeria[algeria.polygon_name==Region].ds,
                             y=algeria[algeria.polygon_name==Region]\
                             .all_day_ratio_single_tile_users, 
                             mode='lines+markers', name='Stay Put Ratio'))
    fig.show()


len(np.unique(algeria.polygon_id))

'''
https://gadm.org/download_country_v3.html
'''
polygons = gpd.read_file('C:/Users/Taha/Desktop/Facebook Algeria/GADM v3.6/gadm36_DZA_2.shp')
borders = gpd.read_file('C:/Users/Taha/Desktop/Facebook Algeria/GADM v3.6/gadm36_DZA_0.shp')

polygons = polygons[polygons['GID_2'].isin(np.unique(algeria.polygon_id))]

fig, ax = plt.subplots(figsize=(15, 10))
ax.set_aspect('equal')
borders.plot(ax=ax, color='white', edgecolor='black')
polygons.plot(ax=ax, cmap='plasma', column='GID_2')
plt.show()

np.unique(polygons.NAME_1)

# ALGIERS

mydict = dict(zip(polygons.GID_2, polygons.geometry))
states = dict(zip(polygons.GID_2, polygons.NAME_1))
algeria['geometry'] = [mydict.get(i) for i in algeria.polygon_id]
algeria['state'] = [states.get(i) for i in algeria.polygon_id]

algiers = algeria[algeria.state == 'Alger']

sort_algiers = algiers.sort_values(by='ds')
sort_algiers = gpd.GeoDataFrame(sort_algiers)

sort_algiers[:26].plot(cmap='hot', figsize=(15, 7), edgecolor='black',
                       column='all_day_bing_tiles_visited_relative_change')
mplleaflet.display()

# Movement Plots Algeria

import chart_studio
username = 'ta.hahaha7'
api_key = '2wgpWm1V2higObS7SKtE'
chart_studio.tools.set_credentials_file(username=username, api_key=api_key)
import chart_studio.plotly as pycs

np.unique(algeria[algeria.state=='Alger']['polygon_name'])

to_show = ['Kouba', 'Tessala-El-Merdja', 'Dar El Beida']
import plotly.graph_objects as go
fig = go.Figure()
for Region in np.unique(algeria[algeria.state=='Alger']['polygon_name']):
    if Region in to_show:
        fig.add_trace(go.Scatter(
            x=algeria[algeria.state=='Alger'][algeria[algeria.state=='Alger'].polygon_name==Region].ds,
            y=algeria[algeria.state=='Alger'][algeria[algeria.state=='Alger'].polygon_name==Region]\
            .all_day_bing_tiles_visited_relative_change, mode='lines+markers', name=str(Region)))
    else:             
        fig.add_trace(go.Scatter(
            x=algeria[algeria.state=='Alger'][algeria[algeria.state=='Alger'].polygon_name==Region].ds,
            y=algeria[algeria.state=='Alger'][algeria[algeria.state=='Alger'].polygon_name==Region]\
            .all_day_bing_tiles_visited_relative_change, 
            mode='lines+markers', name=str(Region), visible='legendonly'))

fig.update_layout(title='Movement Range during COVID outbreak<br>City of Algiers', xaxis_title='Time', 
                   yaxis_title='Percentage Change', legend_title="<b>Municipalities</b>",)
pycs.plot(fig, auto_open=False)

# Movement Map Algeria

import branca.colormap as cm
sort_algeria = algeria.sort_values(by='ds')
sort_algeria = gpd.GeoDataFrame(sort_algeria)

cleaned_sort_algeria = sort_algeria[['ds', 'polygon_name', 'geometry',
                                     'all_day_bing_tiles_visited_relative_change']]
cleaned_sort_algeria = cleaned_sort_algeria.reset_index(drop=True)
cleaned_sort_algeria['ds'] = pd.to_datetime(cleaned_sort_algeria['ds'].values).astype(int) / 10**9
cleaned_sort_algeria['ds'] = cleaned_sort_algeria['ds'].astype(int).astype(str)

max_colour = max(cleaned_sort_algeria['all_day_bing_tiles_visited_relative_change'])
min_colour = min(cleaned_sort_algeria['all_day_bing_tiles_visited_relative_change'])
cmap = cm.linear.YlOrRd_09.scale(min_colour, max_colour)
cleaned_sort_algeria['colour'] = cleaned_sort_algeria['all_day_bing_tiles_visited_relative_change'].map(cmap)

county_list = cleaned_sort_algeria['polygon_name'].unique().tolist()
county_idx = range(len(county_list))

style_dict = {}
for i in county_idx:
    county = county_list[i]
    result = cleaned_sort_algeria[cleaned_sort_algeria['polygon_name'] == county]
    inner_dict = {}
    for _, r in result.iterrows():
        inner_dict[r['ds']] = {'color': r['colour'], 'opacity': 0.7}
    style_dict[str(i)] = inner_dict

counties_df = cleaned_sort_algeria[['geometry']]
counties_gdf = gpd.GeoDataFrame(counties_df)
counties_gdf = counties_gdf.drop_duplicates().reset_index()


slider_map = folium.Map(max_bounds=True, tiles='cartodbpositron', height=500,
                        control_scale=True, location=[36.710139, 3.109861], zoom_start=7)

_ = TimeSliderChoropleth(
    data = counties_gdf.to_json(),
    styledict = style_dict,
).add_to(slider_map)

_ = cmap.add_to(slider_map)
cmap.caption = "Percentage Change in Movement"

slider_map

# SOUTH AFRICA

sa = data[data.country=='ZAF']
sa = sa.reset_index(drop=True)
sa['ds'] = pd.to_datetime(sa['ds'])

sa_polygons = gpd.read_file('C:/Users/Taha/Desktop/Facebook Algeria/GADM v3.6/gadm36_ZAF_2.shp')
sa_polygons = sa_polygons[sa_polygons['GID_2'].isin(np.unique(sa.polygon_id))]

mydict = dict(zip(sa_polygons.GID_2, sa_polygons.geometry))
states = dict(zip(sa_polygons.GID_2, sa_polygons.NAME_1))
sa['geometry'] = [mydict.get(i) for i in sa.polygon_id]
sa['state'] = [states.get(i) for i in sa.polygon_id]

sort_sa = sa.sort_values(by='ds')
sort_sa = gpd.GeoDataFrame(sort_sa)


cleaned_sort_sa = sort_sa[['ds', 'polygon_name', 'geometry',
                           'all_day_bing_tiles_visited_relative_change']]
cleaned_sort_sa = cleaned_sort_sa.reset_index(drop=True)
cleaned_sort_sa['ds'] = pd.to_datetime(cleaned_sort_sa['ds'].values).astype(int) / 10**9
cleaned_sort_sa['ds'] = cleaned_sort_sa['ds'].astype(int).astype(str)

max_colour = max(cleaned_sort_sa['all_day_bing_tiles_visited_relative_change'])
min_colour = min(cleaned_sort_sa['all_day_bing_tiles_visited_relative_change'])
cmap = cm.linear.YlOrRd_09.scale(min_colour, max_colour)
cleaned_sort_sa['colour'] = cleaned_sort_sa['all_day_bing_tiles_visited_relative_change'].map(cmap)

county_list = cleaned_sort_sa['polygon_name'].unique().tolist()
county_idx = range(len(county_list))

style_dict = {}
for i in county_idx:
    county = county_list[i]
    result = cleaned_sort_sa[cleaned_sort_sa['polygon_name'] == county]
    inner_dict = {}
    for _, r in result.iterrows():
        inner_dict[r['ds']] = {'color': r['colour'], 'opacity': 0.7}
    style_dict[str(i)] = inner_dict

counties_df = cleaned_sort_sa[['geometry']]
counties_gdf = gpd.GeoDataFrame(counties_df)
counties_gdf = counties_gdf.drop_duplicates().reset_index()

slider_map = folium.Map(max_bounds=True, tiles='cartodbpositron', height=500,
                        control_scale=True, location=[-26.270760, 28.112268], zoom_start=7)

_ = TimeSliderChoropleth(
    data = counties_gdf.to_json(),
    styledict = style_dict,
).add_to(slider_map)

_ = cmap.add_to(slider_map)
cmap.caption = "Percentage Change in Movement"

slider_map

fig = go.Figure()
for Region in np.unique(sa['polygon_name']):
    #if Region in to_show:
    fig.add_trace(go.Scatter(
        x=sa[sa.polygon_name==Region].ds,
        y=sa[sa.polygon_name==Region].all_day_bing_tiles_visited_relative_change, 
        mode='lines+markers', name=str(Region)))

fig.update_layout(title='Movement Range during COVID outbreak<br>South Africa', xaxis_title='Time', 
                   yaxis_title='Percentage Change', legend_title="<b>Municipalities</b>",)
pycs.plot(fig, auto_open=False)