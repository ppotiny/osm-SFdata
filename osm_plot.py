__author__ = 'Praneetha'

import sqlite3
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

DATABASE = sqlite3.connect("SanFranciscoOSM.db")
MAP_IMG = 'sfmap.png'


def scatter_map(db, map_img, title):
    # Average longitude and latitude for each city
    lonlat_df = pd.read_sql("""SELECT AVG(lon) as lon, AVG(lat) as lat, v as city FROM
                (SELECT lon, lat, k, v FROM nodes_tags
                INNER JOIN nodes
                ON nodes.id = nodes_tags.id)
                WHERE k='addr:city'
                GROUP BY v""", db)

    # Count for each city
    city_count = pd.read_sql("""SELECT COUNT(*) as count, v as city FROM
                                (SELECT v FROM nodes_tags WHERE k='addr:city'
                                UNION ALL
                                SELECT v FROM ways_tags WHERE k='addr:city')
                                GROUP BY city""", db)

    # Merge the datasets above by city
    city_count = city_count.merge(lonlat_df, how='inner', on='city')

    f = plt.figure(figsize=(10,10))
    osm_img = mpimg.imread(map_img)  # Load the map image

    # Create a scatterplot where circle size reflects the number of records per city
    ax2 = f.add_subplot(111)
    ax2.scatter(city_count['lon'], city_count['lat'], city_count['count'], color='m', alpha=0.3)
    ax2.set_title(title, fontsize=16)

    # Load the map with the longitude and latitude as the x and y axes respectively
    ax = f.add_subplot(111)
    ax.imshow(osm_img, interpolation='none', aspect='auto', extent=[-122.7369, -121.9920, 37.4420, 37.9600])
    ax.grid(False)

    plt.show()


def value_pies(values, labels, title):
    """Creates pie chart based on values"""
    if len(values) != len(labels):
        print 'ERROR: Lengths do not match'
    else:
        plt.figure(figsize=(7, 7))

        # Creates the pie chart with a shadow and a percentage at the wedges
        x, plabels, autotexts = plt.pie(x=values, labels=labels, autopct='%1.1f%%',shadow=True)

        #  Each label has a font size of 14
        for label in plabels:
            label.set_fontsize(14)

        # Each percentage has a font size of 14 and is colored white
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)

        plt.title(title, fontsize=20)

        plt.show()