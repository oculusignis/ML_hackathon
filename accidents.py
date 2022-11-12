#!/usr/bin/env python
# coding: utf-8

# In[51]:


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np


# In[52]:


import pyproj
from shapely import geometry
from shapely.ops import transform
from functools import partial


# In[53]:


# Getting data

accidents = pd.read_csv("strassenverkehrsunfallorte.csv", sep=';')
accidents[["AccidentUID", "AccidentType", "Location"]]


# In[57]:


# Extracting Location into two separated columns
accidents[['lat','long']] = accidents['Location'].str.split(',',expand=True)
accidents


# In[58]:


# Understanding data and correct formatting

accidents.info()
accidents.lat = pd.to_numeric(accidents.lat)
accidents.long = pd.to_numeric(accidents.long)
accidents.info()


# In[59]:


# Creating points from coordinates

def create_geometry(row):
  row["geometry"] = Point(row["lat"],row["long"])
  return row

accidents = accidents.apply(create_geometry,axis=1)
accidents_gdf = gpd.GeoDataFrame(accidents,crs=4326)

accidents_gdf


# In[60]:


bus_stops = pd.read_csv("haltestelle-didok.csv", sep=';')
bus_stops


# In[61]:


# Extracting Location into two separated columns and creating two separated columns

bus_stops[['lat','long']] = bus_stops['Geoposition'].str.split(',',expand=True)
bus_stops


# In[62]:


bus_stops.lat = pd.to_numeric(bus_stops.lat)
bus_stops.long = pd.to_numeric(bus_stops.long)


# In[63]:


# Creating points from coordinates
bus_stops = bus_stops.apply(create_geometry,axis=1)
bus_stops_gdf = gpd.GeoDataFrame(bus_stops,crs=4326)

bus_stops_gdf


# In[64]:
lista = list()
raios = np.linspace(0, 10000, 100)

for raio in raios:
    def point2circle(row):
        radius = raio

        local_azimuthal_projection = "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(
            row.lat, row.long
        )
        wgs84_to_aeqd = partial(
            pyproj.transform,
            pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs"),
            pyproj.Proj(local_azimuthal_projection),
        )
        aeqd_to_wgs84 = partial(
            pyproj.transform,
            pyproj.Proj(local_azimuthal_projection),
            pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs"),
        )

        center = Point(float(row.lat), float(row.long))
        point_transformed = transform(wgs84_to_aeqd, center)
        buffer = point_transformed.buffer(radius)
        # Get the polygon with lat lon coordinates
        circle_poly = transform(aeqd_to_wgs84, buffer)
        row['Area_circle'] = circle_poly
        return row

    bus_stops_gdf = bus_stops_gdf.apply(point2circle,axis=1)


    # In[66]:


    bus_stops_gdf.head()



    # In[77]:


    accidents_gdf_geom = accidents_gdf["geometry"].reset_index().drop("index", axis=1)
    accidents_gdf_geom = gpd.GeoDataFrame(accidents_gdf_geom, crs="EPSG:4326", geometry='geometry')
    bus_stops_gdf_geom = bus_stops_gdf["Area_circle"].reset_index().drop("index", axis=1)
    bus_stops_gdf_geom = gpd.GeoDataFrame(bus_stops_gdf_geom, crs="EPSG:4326", geometry='Area_circle')


    # In[85]:


    accidents_gdf_geom


    # In[89]:


    join_inner_df = accidents_gdf_geom.sjoin(bus_stops_gdf_geom, how="inner")
    join_inner_df.index_right.unique()


    # In[94]:


    for row in accidents_gdf_geom.values:
        print(row)
        break


    # In[98]:


    bus_stops_gdf_geom


    # In[104]:


    accidents_count = 0
    for busstop in bus_stops_gdf_geom.values:
        for accident in accidents_gdf_geom.values:
            if busstop[0].contains(accident[0]):
                accidents_count += 1
                break
    final_number = accidents_count/len(accidents_gdf_geom)

    lista.append([raio, final_number])

