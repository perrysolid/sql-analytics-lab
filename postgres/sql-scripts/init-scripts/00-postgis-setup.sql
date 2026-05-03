-- Enable PostGIS extension for geospatial data
-- This must run before the taxi schema creation
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create spatial reference system if not exists (Web Mercator)
-- NYC taxi zones use State Plane New York Long Island NAD83 (EPSG:2263)
INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext)
SELECT 2263, 'EPSG', 2263,
'+proj=lcc +lat_1=41.03333333333333 +lat_2=40.66666666666666 +lat_0=40.16666666666666 +lon_0=-74 +x_0=300000.0000000001 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=ft +no_defs',
'PROJCS["NAD83 / New York Long Island",GEOGCS["NAD83",DATUM["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4269"]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["standard_parallel_1",41.03333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",40.16666666666666],PARAMETER["central_meridian",-74],PARAMETER["false_easting",300000.0000000001],PARAMETER["false_northing",0],UNIT["foot_US",0.3048006096012192,AUTHORITY["EPSG","9003"]],AUTHORITY["EPSG","2263"]]'
WHERE NOT EXISTS (SELECT 1 FROM spatial_ref_sys WHERE srid = 2263);