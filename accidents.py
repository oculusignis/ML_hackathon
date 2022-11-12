#!/usr/bin/env python
# coding: utf-8

# In[218]:


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


# In[219]:


import pyproj
from shapely import geometry
from shapely.ops import transform
from functools import partial


# In[220]:


# Getting data

accidents = pd.read_csv("strassenverkehrsunfallorte.csv", sep=';')
accidents[["AccidentUID", "AccidentType", "Location"]]


# In[221]:


# Extracting Location into two separated columns
accidents[['lat','long']] = accidents['Location'].str.split(',',expand=True)
accidents


# In[222]:


# Understanding data and correct formatting

accidents.info()
accidents.lat = pd.to_numeric(accidents.lat)
accidents.long = pd.to_numeric(accidents.long)
accidents.info()


# In[223]:


# Creating points from coordinates

def create_geometry(row):
  row["geometry"] = Point(row["lat"],row["long"])
  return row

accidents = accidents.apply(create_geometry,axis=1)
accidents_gdf = gpd.GeoDataFrame(accidents,crs=4326)

accidents_gdf


# In[224]:


bus_stops = pd.read_csv("haltestelle-didok.csv", sep=';')
bus_stops


# In[225]:


bus_stops = bus_stops[bus_stops['Verkehrsmitteltext'] == 'Bus']


# In[226]:


# Extracting Location into two separated columns and creating two separated columns

bus_stops[['lat','long']] = bus_stops['Geoposition'].str.split(',',expand=True)
bus_stops


# In[227]:


bus_stops.info()

bus_stops.lat = pd.to_numeric(bus_stops.lat)
bus_stops.long = pd.to_numeric(bus_stops.long)

bus_stops.info()


# In[228]:


# Creating points from coordinates
bus_stops = bus_stops.apply(create_geometry,axis=1)
bus_stops_gdf = gpd.GeoDataFrame(bus_stops,crs=4326)

bus_stops_gdf


# In[229]:


def point2circle(row):
    radius = 20
    
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


# In[230]:


bus_stops_gdf.head()


# In[231]:


bus_stops_gdf_geom.columns


# In[232]:


len(accidents_gdf_geom.geometry.unique()) / len(accidents_gdf_geom)


# In[233]:


accidents_gdf_geom = accidents_gdf["geometry"].reset_index().drop("index", axis=1)
accidents_gdf_geom = gpd.GeoDataFrame(accidents_gdf_geom, crs="EPSG:4326", geometry='geometry')
bus_stops_gdf_geom = bus_stops_gdf["Area_circle"].reset_index().drop("index", axis=1)
bus_stops_gdf_geom = gpd.GeoDataFrame(bus_stops_gdf_geom, crs="EPSG:4326", geometry='Area_circle')


# In[234]:


accidents_gdf_geom


# In[235]:


join_inner_df = accidents_gdf_geom.sjoin(bus_stops_gdf_geom, how="inner")
join_inner_df.index_right.unique()


# In[236]:


for row in accidents_gdf_geom.values:
    print(row)
    break


# In[237]:


bus_stops_gdf_geom


# In[238]:


accidents_gdf_geom


# In[239]:


# accidents_count = 0
# for busstop in bus_stops_gdf_geom.values:
#     for accident in accidents_gdf_geom.values:
#         if busstop[0].contains(accident[0]):
#             accidents_count += 1
#             break
# accidents_count/len(accidents_gdf_geom)


# In[240]:


accidents_count = 0
for accident in accidents_gdf_geom.values:
    for busstop in bus_stops_gdf_geom.values:
        if busstop[0].contains(accident[0]):
            accidents_count += 1
            break
accidents_count/len(accidents_gdf_geom)

