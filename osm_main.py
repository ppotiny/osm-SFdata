
import sqlite3


def top_k(count=10):
    """By default, this prints the 10 most-used keys in node tags"""
    cur.execute("""SELECT k, COUNT(*) FROM nodes_tags
    GROUP BY k ORDER BY COUNT(*) DESC LIMIT """+str(count))
    print 'COUNT | KEY'
    for c in cur:
        print c[1], "|", c[0]


def top_v(k, count=10):
    """By default, this prints the 10 most-used values for a specific key in node tags"""
    cur.execute("""SELECT v, COUNT(*) FROM nodes_tags WHERE k='"""+k+"""'
    GROUP BY v ORDER BY COUNT(*) DESC LIMIT """+str(count))
    for c in cur:
        print c[1], "|", c[0]


def top_percent(k):
    """Returns the percentage of a value's count based on the entire count for that key"""

    # This gets the count for every node and way that contains the key.
    cur.execute("""
                SELECT COUNT(*) FROM
                (SELECT v from nodes_tags WHERE k='"""+k+"""'
                UNION ALL
                SELECT v from ways_tags WHERE k='"""+k+"""')
                                                            """)

    v_count = [c[0] for c in cur]


    # This gets the top ten values of the key for both nodes and ways and their count
    cur.execute("""
                SELECT v, COUNT(*) as count FROM
                (SELECT v from nodes_tags WHERE k='"""+k+"""'
                UNION ALL
                SELECT v from ways_tags WHERE k='"""+k+"""')
                GROUP BY v
                ORDER BY count DESC
                LIMIT 10
                                                            """)

    # Here, I get a percentage by dividing the value's count with v_count and multiplying by 100.
    # The result is formatted to 2 decimal places

    for c in cur:
            print "{0:.2f}".format((c[1]*100.0)/v_count[0])+'%', "|", c[0]



def overview_stats():
     # Overview Statistics
    print "The size of the file is: 400.722 MB",

    cur.execute("SELECT COUNT(*) FROM nodes")
    print "\nThere are ", [c[0] for c in cur][0], " unique users,"

    cur.execute("SELECT COUNT(*) FROM ways")
    print "nodes and ", [c[0] for c in cur][0], " ways in this file."

    print "\nHere are the top 10 keys for nodes:\n"
    top_k(10)

    print "\nHere are the top 10 keys for ways:\n"
    cur.execute("""SELECT k, COUNT(*) FROM ways_tags
    GROUP BY k ORDER BY COUNT(*) DESC LIMIT 10""")
    for c in cur:
        print c

    print "\nTop cities in this file\n"
    top_percent('addr:city')


if __name__ == '__main__':

    db = sqlite3.connect("SanFranciscoOSM.db")
    print "Connected to database"

    cur = db.cursor()
    print "Loading database into cursor \n"

    for c in cur: print c

    #overview_stats()

    print '\nSuccess!'