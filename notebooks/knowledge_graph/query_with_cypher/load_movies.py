#!/usr/bin/env python
"""
Load the standard Neo4j movies dataset into your AuraDB instance.

Usage:
    cd /path/to/your/agentic-ai-lab
    conda activate agentic-ai
    python notebooks/knowledge_graph/query_with_cypher/load_movies.py

Requires NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD in project-level .env.
Idempotent: uses MERGE so safe to run multiple times.
"""
import os
import sys
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    print("ERROR: NEO4J_URI / NEO4J_USERNAME / NEO4J_PASSWORD not set in .env")
    sys.exit(1)

from neo4j import GraphDatabase

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# ---------------------------------------------------------------------------
# Each statement is run separately so a single error doesn't abort the whole
# load. MERGE is used throughout so the script is safe to re-run.
# ---------------------------------------------------------------------------
STATEMENTS = [

    # ── Movies ──────────────────────────────────────────────────────────────
    "MERGE (:Movie {title:'The Matrix',                   released:1999, tagline:'Welcome to the Real World'})",
    "MERGE (:Movie {title:'The Matrix Reloaded',          released:2003, tagline:'Free your mind'})",
    "MERGE (:Movie {title:'The Matrix Revolutions',       released:2003, tagline:'Everything that has a beginning has an end'})",
    "MERGE (:Movie {title:\"The Devil's Advocate\",       released:1997, tagline:'Evil has its winning ways'})",
    "MERGE (:Movie {title:'A Few Good Men',               released:1992, tagline:\"In the heart of the nation's capital, in a courthouse of the U.S. government, one man will stop at nothing to keep his honor, and one will stop at nothing to find the truth.\"})",
    "MERGE (:Movie {title:'As Good as It Gets',           released:1997, tagline:'A comedy from the heart that goes for the throat.'})",
    "MERGE (:Movie {title:'What Dreams May Come',         released:1998, tagline:'After life there is more. The end is just the beginning.'})",
    "MERGE (:Movie {title:'Snow Falling on Cedars',       released:1999, tagline:'First loves last. Forever.'})",
    "MERGE (:Movie {title:\"You've Got Mail\",            released:1998, tagline:'At odds in life... in love on-line.'})",
    "MERGE (:Movie {title:'Sleepless in Seattle',         released:1993, tagline:'What if someone you never met, someone you never saw, someone you never knew was the only someone for you?'})",
    "MERGE (:Movie {title:'Joe Versus the Volcano',       released:1990, tagline:'A story of love, lava and burning desire.'})",
    "MERGE (:Movie {title:'When Harry Met Sally',         released:1989, tagline:'Can two friends sleep together and still love each other in the morning?'})",
    "MERGE (:Movie {title:'That Thing You Do',            released:1996, tagline:'In every life there comes a time when that thing you dream becomes that thing you do'})",
    "MERGE (:Movie {title:'The Replacements',             released:2000, tagline:'Pain heals, Chicks dig scars... Glory lasts forever'})",
    "MERGE (:Movie {title:'RescueDawn',                   released:2006, tagline:\"Based on the extraordinary true story of one man's fight for freedom\"})",
    "MERGE (:Movie {title:'The Birdcage',                 released:1996, tagline:'Come as you are'})",
    "MERGE (:Movie {title:'Unforgiven',                   released:1992, tagline:\"It's a hell of a thing, killing a man\"})",
    "MERGE (:Movie {title:'Johnny Mnemonic',              released:1995, tagline:'The hottest data on earth. In the coolest head in town.'})",
    "MERGE (:Movie {title:'Cloud Atlas',                  released:2012, tagline:'Everything is connected'})",
    "MERGE (:Movie {title:'The Da Vinci Code',            released:2006, tagline:'Break The Codes'})",
    "MERGE (:Movie {title:'V for Vendetta',               released:2005, tagline:'Freedom! Forever!'})",
    "MERGE (:Movie {title:'Speed Racer',                  released:2008, tagline:'Speed has no limits'})",
    "MERGE (:Movie {title:'Ninja Assassin',               released:2009, tagline:'Prepare to enter a secret world of assassins'})",
    "MERGE (:Movie {title:'The Green Mile',               released:1999, tagline:\"Walk a mile you'll never forget.\"})",
    "MERGE (:Movie {title:'Frost/Nixon',                  released:2008, tagline:'400 million people were waiting for the truth.'})",
    "MERGE (:Movie {title:'Hoffa',                        released:1992, tagline:\"He didn't want law. He wanted justice.\"})",
    "MERGE (:Movie {title:'Apollo 13',                    released:1995, tagline:'Houston, we have a problem.'})",
    "MERGE (:Movie {title:'Twister',                      released:1996, tagline:\"Don't Breathe. Don't Look Back.\"})",
    "MERGE (:Movie {title:'Cast Away',                    released:2000, tagline:'At the edge of the world, his journey begins.'})",
    "MERGE (:Movie {title:\"One Flew Over the Cuckoo's Nest\", released:1975, tagline:\"If he's crazy, what does that make you?\"})",
    "MERGE (:Movie {title:\"Something's Gotta Give\",     released:2003})",
    "MERGE (:Movie {title:'Bicentennial Man',             released:1999, tagline:\"One robot's 200 year journey to become an ordinary man.\"})",
    "MERGE (:Movie {title:\"Charlie Wilson's War\",       released:2007, tagline:\"A stiff drink. A little mascara. A lot of nerve. Who said they couldn't bring down the Soviet empire.\"})",
    "MERGE (:Movie {title:'The Polar Express',            released:2004, tagline:'This Holiday Season... Believe'})",
    "MERGE (:Movie {title:'A League of Their Own',        released:1992, tagline:'Once in a lifetime you get a chance to do something different.'})",

    # ── People ──────────────────────────────────────────────────────────────
    "MERGE (:Person {name:'Tom Hanks',           born:1956})",
    "MERGE (:Person {name:'Tom Tykwer',          born:1965})",
    "MERGE (:Person {name:'Emil Eifrem',         born:1978})",
    "MERGE (:Person {name:'Charlize Theron',     born:1975})",
    "MERGE (:Person {name:'Al Pacino',           born:1940})",
    "MERGE (:Person {name:'Taylor Hackford',     born:1944})",
    "MERGE (:Person {name:'Tom Cruise',          born:1962})",
    "MERGE (:Person {name:'Jack Nicholson',      born:1937})",
    "MERGE (:Person {name:'Demi Moore',          born:1962})",
    "MERGE (:Person {name:'Kevin Bacon',         born:1958})",
    "MERGE (:Person {name:'Kiefer Sutherland',   born:1966})",
    "MERGE (:Person {name:'Nicolas Cage',        born:1964})",
    "MERGE (:Person {name:'Kevin Pollak',        born:1957})",
    "MERGE (:Person {name:'J.T. Walsh',          born:1943})",
    "MERGE (:Person {name:'James Marshall',      born:1967})",
    "MERGE (:Person {name:'Christopher Guest',   born:1948})",
    "MERGE (:Person {name:'Rob Reiner',          born:1947})",
    "MERGE (:Person {name:'Aaron Sorkin',        born:1961})",
    "MERGE (:Person {name:'Helen Hunt',          born:1963})",
    "MERGE (:Person {name:'Greg Kinnear',        born:1963})",
    "MERGE (:Person {name:'James L. Brooks',     born:1940})",
    "MERGE (:Person {name:'Cuba Gooding Jr.',    born:1968})",
    "MERGE (:Person {name:'Renee Zellweger',     born:1969})",
    "MERGE (:Person {name:'Bonnie Hunt',         born:1961})",
    "MERGE (:Person {name:'Rob Cohen',           born:1949})",
    "MERGE (:Person {name:'Robin Williams',      born:1951})",
    "MERGE (:Person {name:'Vincent Ward',        born:1956})",
    "MERGE (:Person {name:'Ethan Hawke',         born:1970})",
    "MERGE (:Person {name:'Rick Yune',           born:1971})",
    "MERGE (:Person {name:'James Cromwell',      born:1940})",
    "MERGE (:Person {name:'Scott Hicks',         born:1953})",
    "MERGE (:Person {name:'Annabella Sciorra',   born:1960})",
    "MERGE (:Person {name:'Keanu Reeves',        born:1964})",
    "MERGE (:Person {name:'Carrie-Anne Moss',    born:1967})",
    "MERGE (:Person {name:'Laurence Fishburne',  born:1961})",
    "MERGE (:Person {name:'Hugo Weaving',        born:1960})",
    "MERGE (:Person {name:'Lilly Wachowski',     born:1967})",
    "MERGE (:Person {name:'Lana Wachowski',      born:1965})",
    "MERGE (:Person {name:'Joel Silver',         born:1952})",
    "MERGE (:Person {name:'Ian McKellen',        born:1939})",
    "MERGE (:Person {name:'Audrey Tautou',       born:1976})",
    "MERGE (:Person {name:'Paul Bettany',        born:1971})",
    "MERGE (:Person {name:'Ron Howard',          born:1954})",
    "MERGE (:Person {name:'Nathan Lane',         born:1956})",
    "MERGE (:Person {name:'Mike Nichols',        born:1931})",
    "MERGE (:Person {name:\"Rosie O'Donnell\",   born:1962})",
    "MERGE (:Person {name:'Rita Wilson',         born:1956})",
    "MERGE (:Person {name:'Bill Pullman',        born:1953})",
    "MERGE (:Person {name:'Meg Ryan',            born:1961})",
    "MERGE (:Person {name:'Nora Ephron',         born:1941})",
    "MERGE (:Person {name:'Victor Garber',       born:1949})",
    "MERGE (:Person {name:'Clint Eastwood',      born:1930})",
    "MERGE (:Person {name:'Richard Harris',      born:1930})",
    "MERGE (:Person {name:'Michael Sheen',       born:1969})",
    "MERGE (:Person {name:'Oliver Platt',        born:1960})",
    "MERGE (:Person {name:'Danny DeVito',        born:1944})",
    "MERGE (:Person {name:'John C. Reilly',      born:1965})",
    "MERGE (:Person {name:'Ed Harris',           born:1950})",
    "MERGE (:Person {name:'Bill Paxton',         born:1955})",
    "MERGE (:Person {name:'Philip Seymour Hoffman', born:1967})",
    "MERGE (:Person {name:'Diane Keaton',        born:1946})",
    "MERGE (:Person {name:'Halle Berry',         born:1966})",
    "MERGE (:Person {name:'Jim Broadbent',       born:1949})",
    "MERGE (:Person {name:'Stefan Arndt',        born:1961})",
    "MERGE (:Person {name:'Natalie Portman',     born:1981})",
    "MERGE (:Person {name:'Stephen Rea',         born:1946})",
    "MERGE (:Person {name:'John Hurt',           born:1940})",
    "MERGE (:Person {name:'James McTeigue',      born:1967})",
    "MERGE (:Person {name:'Emile Hirsch',        born:1985})",
    "MERGE (:Person {name:'John Goodman',        born:1960})",
    "MERGE (:Person {name:'Susan Sarandon',      born:1946})",
    "MERGE (:Person {name:'Matthew Fox',         born:1966})",
    "MERGE (:Person {name:'Christina Ricci',     born:1980})",
    "MERGE (:Person {name:'Rain',                born:1982})",
    "MERGE (:Person {name:'Naomie Harris',       born:1976})",
    "MERGE (:Person {name:'Michael Clarke Duncan', born:1957})",
    "MERGE (:Person {name:'David Morse',         born:1953})",
    "MERGE (:Person {name:'Sam Rockwell',        born:1968})",
    "MERGE (:Person {name:'Gary Sinise',         born:1955})",
    "MERGE (:Person {name:'Patricia Clarkson',   born:1959})",
    "MERGE (:Person {name:'Frank Darabont',      born:1959})",
    "MERGE (:Person {name:'Frank Langella',      born:1938})",
    "MERGE (:Person {name:'Gene Hackman',        born:1930})",
    "MERGE (:Person {name:'Howard Deutch',       born:1950})",
    "MERGE (:Person {name:'Christian Bale',      born:1974})",
    "MERGE (:Person {name:'Werner Herzog',       born:1942})",
    "MERGE (:Person {name:'Billy Crystal',       born:1948})",
    "MERGE (:Person {name:'Carrie Fisher',       born:1956})",
    "MERGE (:Person {name:'Bruno Kirby',         born:1949})",
    "MERGE (:Person {name:'Parker Posey',        born:1968})",
    "MERGE (:Person {name:'Dave Chappelle',      born:1973})",
    "MERGE (:Person {name:'Sam Neill',           born:1947})",
    "MERGE (:Person {name:'Julia Roberts',       born:1967})",
    "MERGE (:Person {name:'Robert Zemeckis',     born:1951})",
    "MERGE (:Person {name:'Geena Davis',         born:1956})",
    "MERGE (:Person {name:'Lori Petty',          born:1963})",
    "MERGE (:Person {name:'Penny Marshall',      born:1943})",
    "MERGE (:Person {name:'Ben Miles',           born:1966})",

    # ── Relationships ───────────────────────────────────────────────────────
    # Each MATCH+MERGE finds existing nodes by title/name and links them.

    # The Matrix trilogy
    """MATCH (p:Person {name:'Keanu Reeves'}),(m:Movie {title:'The Matrix'})
       MERGE (p)-[:ACTED_IN {roles:['Neo']}]->(m)""",
    """MATCH (p:Person {name:'Carrie-Anne Moss'}),(m:Movie {title:'The Matrix'})
       MERGE (p)-[:ACTED_IN {roles:['Trinity']}]->(m)""",
    """MATCH (p:Person {name:'Laurence Fishburne'}),(m:Movie {title:'The Matrix'})
       MERGE (p)-[:ACTED_IN {roles:['Morpheus']}]->(m)""",
    """MATCH (p:Person {name:'Hugo Weaving'}),(m:Movie {title:'The Matrix'})
       MERGE (p)-[:ACTED_IN {roles:['Agent Smith']}]->(m)""",
    """MATCH (p:Person {name:'Emil Eifrem'}),(m:Movie {title:'The Matrix'})
       MERGE (p)-[:ACTED_IN {roles:['Emil']}]->(m)""",
    """MATCH (p:Person {name:'Lilly Wachowski'}),(m:Movie {title:'The Matrix'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Lana Wachowski'}),(m:Movie {title:'The Matrix'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Joel Silver'}),(m:Movie {title:'The Matrix'}) MERGE (p)-[:PRODUCED]->(m)""",

    """MATCH (p:Person {name:'Keanu Reeves'}),(m:Movie {title:'The Matrix Reloaded'})
       MERGE (p)-[:ACTED_IN {roles:['Neo']}]->(m)""",
    """MATCH (p:Person {name:'Carrie-Anne Moss'}),(m:Movie {title:'The Matrix Reloaded'})
       MERGE (p)-[:ACTED_IN {roles:['Trinity']}]->(m)""",
    """MATCH (p:Person {name:'Laurence Fishburne'}),(m:Movie {title:'The Matrix Reloaded'})
       MERGE (p)-[:ACTED_IN {roles:['Morpheus']}]->(m)""",
    """MATCH (p:Person {name:'Hugo Weaving'}),(m:Movie {title:'The Matrix Reloaded'})
       MERGE (p)-[:ACTED_IN {roles:['Agent Smith']}]->(m)""",
    """MATCH (p:Person {name:'Lilly Wachowski'}),(m:Movie {title:'The Matrix Reloaded'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Lana Wachowski'}),(m:Movie {title:'The Matrix Reloaded'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Joel Silver'}),(m:Movie {title:'The Matrix Reloaded'}) MERGE (p)-[:PRODUCED]->(m)""",

    """MATCH (p:Person {name:'Keanu Reeves'}),(m:Movie {title:'The Matrix Revolutions'})
       MERGE (p)-[:ACTED_IN {roles:['Neo']}]->(m)""",
    """MATCH (p:Person {name:'Carrie-Anne Moss'}),(m:Movie {title:'The Matrix Revolutions'})
       MERGE (p)-[:ACTED_IN {roles:['Trinity']}]->(m)""",
    """MATCH (p:Person {name:'Laurence Fishburne'}),(m:Movie {title:'The Matrix Revolutions'})
       MERGE (p)-[:ACTED_IN {roles:['Morpheus']}]->(m)""",
    """MATCH (p:Person {name:'Hugo Weaving'}),(m:Movie {title:'The Matrix Revolutions'})
       MERGE (p)-[:ACTED_IN {roles:['Agent Smith']}]->(m)""",
    """MATCH (p:Person {name:'Lilly Wachowski'}),(m:Movie {title:'The Matrix Revolutions'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Lana Wachowski'}),(m:Movie {title:'The Matrix Revolutions'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Joel Silver'}),(m:Movie {title:'The Matrix Revolutions'}) MERGE (p)-[:PRODUCED]->(m)""",

    # The Devil's Advocate
    """MATCH (p:Person {name:'Keanu Reeves'}),(m:Movie {title:"The Devil's Advocate"})
       MERGE (p)-[:ACTED_IN {roles:['Kevin Lomax']}]->(m)""",
    """MATCH (p:Person {name:'Al Pacino'}),(m:Movie {title:"The Devil's Advocate"})
       MERGE (p)-[:ACTED_IN {roles:['John Milton']}]->(m)""",
    """MATCH (p:Person {name:'Charlize Theron'}),(m:Movie {title:"The Devil's Advocate"})
       MERGE (p)-[:ACTED_IN {roles:['Mary Ann Lomax']}]->(m)""",
    """MATCH (p:Person {name:'Taylor Hackford'}),(m:Movie {title:"The Devil's Advocate"}) MERGE (p)-[:DIRECTED]->(m)""",

    # A Few Good Men
    """MATCH (p:Person {name:'Tom Cruise'}),(m:Movie {title:'A Few Good Men'})
       MERGE (p)-[:ACTED_IN {roles:['Lt. Daniel Kaffee']}]->(m)""",
    """MATCH (p:Person {name:'Jack Nicholson'}),(m:Movie {title:'A Few Good Men'})
       MERGE (p)-[:ACTED_IN {roles:['Col. Nathan R. Jessup']}]->(m)""",
    """MATCH (p:Person {name:'Demi Moore'}),(m:Movie {title:'A Few Good Men'})
       MERGE (p)-[:ACTED_IN {roles:['Lt. Cdr. JoAnne Galloway']}]->(m)""",
    """MATCH (p:Person {name:'Kevin Bacon'}),(m:Movie {title:'A Few Good Men'})
       MERGE (p)-[:ACTED_IN {roles:['Capt. Jack Ross']}]->(m)""",
    """MATCH (p:Person {name:'Kiefer Sutherland'}),(m:Movie {title:'A Few Good Men'})
       MERGE (p)-[:ACTED_IN {roles:['Lt. Jonathan Kendrick']}]->(m)""",
    """MATCH (p:Person {name:'Nicolas Cage'}),(m:Movie {title:'A Few Good Men'})
       MERGE (p)-[:ACTED_IN {roles:['Cpl. Jeffrey Barnes']}]->(m)""",
    """MATCH (p:Person {name:'Kevin Pollak'}),(m:Movie {title:'A Few Good Men'})
       MERGE (p)-[:ACTED_IN {roles:['Lt. Sam Weinberg']}]->(m)""",
    """MATCH (p:Person {name:'J.T. Walsh'}),(m:Movie {title:'A Few Good Men'})
       MERGE (p)-[:ACTED_IN {roles:['Lt. Col. Matthew Andrew Markinson']}]->(m)""",
    """MATCH (p:Person {name:'James Marshall'}),(m:Movie {title:'A Few Good Men'})
       MERGE (p)-[:ACTED_IN {roles:['Pfc. Louden Downey']}]->(m)""",
    """MATCH (p:Person {name:'Christopher Guest'}),(m:Movie {title:'A Few Good Men'})
       MERGE (p)-[:ACTED_IN {roles:['Dr. Stone']}]->(m)""",
    """MATCH (p:Person {name:'Aaron Sorkin'}),(m:Movie {title:'A Few Good Men'}) MERGE (p)-[:WROTE]->(m)""",
    """MATCH (p:Person {name:'Rob Reiner'}),(m:Movie {title:'A Few Good Men'}) MERGE (p)-[:DIRECTED]->(m)""",

    # As Good as It Gets
    """MATCH (p:Person {name:'Helen Hunt'}),(m:Movie {title:'As Good as It Gets'})
       MERGE (p)-[:ACTED_IN {roles:['Carol Connelly']}]->(m)""",
    """MATCH (p:Person {name:'Jack Nicholson'}),(m:Movie {title:'As Good as It Gets'})
       MERGE (p)-[:ACTED_IN {roles:['Melvin Udall']}]->(m)""",
    """MATCH (p:Person {name:'Greg Kinnear'}),(m:Movie {title:'As Good as It Gets'})
       MERGE (p)-[:ACTED_IN {roles:['Simon Bishop']}]->(m)""",
    """MATCH (p:Person {name:'Cuba Gooding Jr.'}),(m:Movie {title:'As Good as It Gets'})
       MERGE (p)-[:ACTED_IN {roles:['Frank Sachs']}]->(m)""",
    """MATCH (p:Person {name:'James L. Brooks'}),(m:Movie {title:'As Good as It Gets'}) MERGE (p)-[:DIRECTED]->(m)""",

    # What Dreams May Come
    """MATCH (p:Person {name:'Robin Williams'}),(m:Movie {title:'What Dreams May Come'})
       MERGE (p)-[:ACTED_IN {roles:['Chris Nielsen']}]->(m)""",
    """MATCH (p:Person {name:'Cuba Gooding Jr.'}),(m:Movie {title:'What Dreams May Come'})
       MERGE (p)-[:ACTED_IN {roles:['Albert Lewis']}]->(m)""",
    """MATCH (p:Person {name:'Annabella Sciorra'}),(m:Movie {title:'What Dreams May Come'})
       MERGE (p)-[:ACTED_IN {roles:['Annie Collins-Nielsen']}]->(m)""",
    """MATCH (p:Person {name:'Vincent Ward'}),(m:Movie {title:'What Dreams May Come'}) MERGE (p)-[:DIRECTED]->(m)""",

    # Snow Falling on Cedars
    """MATCH (p:Person {name:'Ethan Hawke'}),(m:Movie {title:'Snow Falling on Cedars'})
       MERGE (p)-[:ACTED_IN {roles:['Ishmael Chambers']}]->(m)""",
    """MATCH (p:Person {name:'Rick Yune'}),(m:Movie {title:'Snow Falling on Cedars'})
       MERGE (p)-[:ACTED_IN {roles:['Kazuo Miyamoto']}]->(m)""",
    """MATCH (p:Person {name:'James Cromwell'}),(m:Movie {title:'Snow Falling on Cedars'})
       MERGE (p)-[:ACTED_IN {roles:['Nels Gudmundsson']}]->(m)""",
    """MATCH (p:Person {name:'Scott Hicks'}),(m:Movie {title:'Snow Falling on Cedars'}) MERGE (p)-[:DIRECTED]->(m)""",

    # You've Got Mail
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:"You've Got Mail"})
       MERGE (p)-[:ACTED_IN {roles:['Joe Fox']}]->(m)""",
    """MATCH (p:Person {name:'Meg Ryan'}),(m:Movie {title:"You've Got Mail"})
       MERGE (p)-[:ACTED_IN {roles:['Kathleen Kelly']}]->(m)""",
    """MATCH (p:Person {name:'Greg Kinnear'}),(m:Movie {title:"You've Got Mail"})
       MERGE (p)-[:ACTED_IN {roles:['Frank Navasky']}]->(m)""",
    """MATCH (p:Person {name:'Parker Posey'}),(m:Movie {title:"You've Got Mail"})
       MERGE (p)-[:ACTED_IN {roles:['Patricia Eden']}]->(m)""",
    """MATCH (p:Person {name:'Dave Chappelle'}),(m:Movie {title:"You've Got Mail"})
       MERGE (p)-[:ACTED_IN {roles:['Kevin Jackson']}]->(m)""",
    """MATCH (p:Person {name:'Nora Ephron'}),(m:Movie {title:"You've Got Mail"}) MERGE (p)-[:DIRECTED]->(m)""",

    # Sleepless in Seattle
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'Sleepless in Seattle'})
       MERGE (p)-[:ACTED_IN {roles:['Sam Baldwin']}]->(m)""",
    """MATCH (p:Person {name:'Meg Ryan'}),(m:Movie {title:'Sleepless in Seattle'})
       MERGE (p)-[:ACTED_IN {roles:['Annie Reed']}]->(m)""",
    """MATCH (p:Person {name:'Rita Wilson'}),(m:Movie {title:'Sleepless in Seattle'})
       MERGE (p)-[:ACTED_IN {roles:['Suzy']}]->(m)""",
    """MATCH (p:Person {name:'Bill Pullman'}),(m:Movie {title:'Sleepless in Seattle'})
       MERGE (p)-[:ACTED_IN {roles:['Walter']}]->(m)""",
    """MATCH (p:Person {name:'Victor Garber'}),(m:Movie {title:'Sleepless in Seattle'})
       MERGE (p)-[:ACTED_IN {roles:['Greg']}]->(m)""",
    """MATCH (p:Person {name:'Nora Ephron'}),(m:Movie {title:'Sleepless in Seattle'}) MERGE (p)-[:DIRECTED]->(m)""",

    # Joe Versus the Volcano
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'Joe Versus the Volcano'})
       MERGE (p)-[:ACTED_IN {roles:['Joe Banks']}]->(m)""",
    """MATCH (p:Person {name:'Meg Ryan'}),(m:Movie {title:'Joe Versus the Volcano'})
       MERGE (p)-[:ACTED_IN {roles:['DeDe', 'Angelica Graynamore', 'Patricia Graynamore']}]->(m)""",
    """MATCH (p:Person {name:'Nathan Lane'}),(m:Movie {title:'Joe Versus the Volcano'})
       MERGE (p)-[:ACTED_IN {roles:['Baw']}]->(m)""",

    # When Harry Met Sally
    """MATCH (p:Person {name:'Billy Crystal'}),(m:Movie {title:'When Harry Met Sally'})
       MERGE (p)-[:ACTED_IN {roles:['Harry Burns']}]->(m)""",
    """MATCH (p:Person {name:'Meg Ryan'}),(m:Movie {title:'When Harry Met Sally'})
       MERGE (p)-[:ACTED_IN {roles:['Sally Albright']}]->(m)""",
    """MATCH (p:Person {name:'Carrie Fisher'}),(m:Movie {title:'When Harry Met Sally'})
       MERGE (p)-[:ACTED_IN {roles:['Marie']}]->(m)""",
    """MATCH (p:Person {name:'Bruno Kirby'}),(m:Movie {title:'When Harry Met Sally'})
       MERGE (p)-[:ACTED_IN {roles:['Jess']}]->(m)""",
    """MATCH (p:Person {name:'Rob Reiner'}),(m:Movie {title:'When Harry Met Sally'}) MERGE (p)-[:DIRECTED]->(m)""",

    # That Thing You Do
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'That Thing You Do'})
       MERGE (p)-[:ACTED_IN {roles:['Mr. White']}]->(m)""",
    """MATCH (p:Person {name:'Liv Tyler'}),(m:Movie {title:'That Thing You Do'})
       MERGE (p)-[:ACTED_IN {roles:['Faye Dolan']}]->(m)""",
    """MERGE (:Person {name:'Liv Tyler', born:1977})""",
    """MATCH (p:Person {name:'Charlize Theron'}),(m:Movie {title:'That Thing You Do'})
       MERGE (p)-[:ACTED_IN {roles:['Tina']}]->(m)""",
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'That Thing You Do'}) MERGE (p)-[:DIRECTED]->(m)""",

    # The Replacements
    """MATCH (p:Person {name:'Keanu Reeves'}),(m:Movie {title:'The Replacements'})
       MERGE (p)-[:ACTED_IN {roles:['Shane Falco']}]->(m)""",
    """MATCH (p:Person {name:'Gene Hackman'}),(m:Movie {title:'The Replacements'})
       MERGE (p)-[:ACTED_IN {roles:['Bill Parcells']}]->(m)""",
    """MATCH (p:Person {name:'Howard Deutch'}),(m:Movie {title:'The Replacements'}) MERGE (p)-[:DIRECTED]->(m)""",

    # RescueDawn
    """MATCH (p:Person {name:'Christian Bale'}),(m:Movie {title:'RescueDawn'})
       MERGE (p)-[:ACTED_IN {roles:['Dieter Dengler']}]->(m)""",
    """MATCH (p:Person {name:'Werner Herzog'}),(m:Movie {title:'RescueDawn'}) MERGE (p)-[:DIRECTED]->(m)""",

    # The Birdcage
    """MATCH (p:Person {name:'Robin Williams'}),(m:Movie {title:'The Birdcage'})
       MERGE (p)-[:ACTED_IN {roles:['Armand Goldman']}]->(m)""",
    """MATCH (p:Person {name:'Nathan Lane'}),(m:Movie {title:'The Birdcage'})
       MERGE (p)-[:ACTED_IN {roles:['Albert Goldman']}]->(m)""",
    """MATCH (p:Person {name:'Gene Hackman'}),(m:Movie {title:'The Birdcage'})
       MERGE (p)-[:ACTED_IN {roles:['Senator Kevin Keeley']}]->(m)""",
    """MATCH (p:Person {name:'Mike Nichols'}),(m:Movie {title:'The Birdcage'}) MERGE (p)-[:DIRECTED]->(m)""",

    # Unforgiven
    """MATCH (p:Person {name:'Clint Eastwood'}),(m:Movie {title:'Unforgiven'})
       MERGE (p)-[:ACTED_IN {roles:['Bill Munny']}]->(m)""",
    """MATCH (p:Person {name:'Richard Harris'}),(m:Movie {title:'Unforgiven'})
       MERGE (p)-[:ACTED_IN {roles:['English Bob']}]->(m)""",
    """MATCH (p:Person {name:'Clint Eastwood'}),(m:Movie {title:'Unforgiven'}) MERGE (p)-[:DIRECTED]->(m)""",

    # Johnny Mnemonic
    """MATCH (p:Person {name:'Keanu Reeves'}),(m:Movie {title:'Johnny Mnemonic'})
       MERGE (p)-[:ACTED_IN {roles:['Johnny Mnemonic']}]->(m)""",

    # Cloud Atlas
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'Cloud Atlas'})
       MERGE (p)-[:ACTED_IN {roles:['Zachry', 'Dr. Henry Goose', 'Isaac Sachs', 'Dermot Hoggins']}]->(m)""",
    """MATCH (p:Person {name:'Hugo Weaving'}),(m:Movie {title:'Cloud Atlas'})
       MERGE (p)-[:ACTED_IN {roles:['Bill Smoke', 'Haskell Moore', 'Tadeusz Kesselring', 'Nurse Noakes', 'Boardman Mephi', 'Old Georgie']}]->(m)""",
    """MATCH (p:Person {name:'Halle Berry'}),(m:Movie {title:'Cloud Atlas'})
       MERGE (p)-[:ACTED_IN {roles:['Luisa Rey', 'Jocasta Ayrs', 'Ovid', 'Meronym']}]->(m)""",
    """MATCH (p:Person {name:'Jim Broadbent'}),(m:Movie {title:'Cloud Atlas'})
       MERGE (p)-[:ACTED_IN {roles:['Vyvyan Ayrs', 'Captain Molyneux', 'Timothy Cavendish']}]->(m)""",
    """MATCH (p:Person {name:'Tom Tykwer'}),(m:Movie {title:'Cloud Atlas'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Lilly Wachowski'}),(m:Movie {title:'Cloud Atlas'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Lana Wachowski'}),(m:Movie {title:'Cloud Atlas'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Stefan Arndt'}),(m:Movie {title:'Cloud Atlas'}) MERGE (p)-[:PRODUCED]->(m)""",

    # The Da Vinci Code
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'The Da Vinci Code'})
       MERGE (p)-[:ACTED_IN {roles:['Dr. Robert Langdon']}]->(m)""",
    """MATCH (p:Person {name:'Ian McKellen'}),(m:Movie {title:'The Da Vinci Code'})
       MERGE (p)-[:ACTED_IN {roles:['Sir Leigh Teabing']}]->(m)""",
    """MATCH (p:Person {name:'Audrey Tautou'}),(m:Movie {title:'The Da Vinci Code'})
       MERGE (p)-[:ACTED_IN {roles:['Sophie Neveu']}]->(m)""",
    """MATCH (p:Person {name:'Paul Bettany'}),(m:Movie {title:'The Da Vinci Code'})
       MERGE (p)-[:ACTED_IN {roles:['Silas']}]->(m)""",
    """MATCH (p:Person {name:'Ron Howard'}),(m:Movie {title:'The Da Vinci Code'}) MERGE (p)-[:DIRECTED]->(m)""",

    # V for Vendetta
    """MATCH (p:Person {name:'Hugo Weaving'}),(m:Movie {title:'V for Vendetta'})
       MERGE (p)-[:ACTED_IN {roles:['V']}]->(m)""",
    """MATCH (p:Person {name:'Natalie Portman'}),(m:Movie {title:'V for Vendetta'})
       MERGE (p)-[:ACTED_IN {roles:['Evey Hammond']}]->(m)""",
    """MATCH (p:Person {name:'Stephen Rea'}),(m:Movie {title:'V for Vendetta'})
       MERGE (p)-[:ACTED_IN {roles:['Inspector Eric Finch']}]->(m)""",
    """MATCH (p:Person {name:'John Hurt'}),(m:Movie {title:'V for Vendetta'})
       MERGE (p)-[:ACTED_IN {roles:['High Chancellor Adam Sutler']}]->(m)""",
    """MATCH (p:Person {name:'James McTeigue'}),(m:Movie {title:'V for Vendetta'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Joel Silver'}),(m:Movie {title:'V for Vendetta'}) MERGE (p)-[:PRODUCED]->(m)""",

    # Speed Racer
    """MATCH (p:Person {name:'Emile Hirsch'}),(m:Movie {title:'Speed Racer'})
       MERGE (p)-[:ACTED_IN {roles:['Speed Racer']}]->(m)""",
    """MATCH (p:Person {name:'John Goodman'}),(m:Movie {title:'Speed Racer'})
       MERGE (p)-[:ACTED_IN {roles:['Pops']}]->(m)""",
    """MATCH (p:Person {name:'Susan Sarandon'}),(m:Movie {title:'Speed Racer'})
       MERGE (p)-[:ACTED_IN {roles:['Mom']}]->(m)""",
    """MATCH (p:Person {name:'Matthew Fox'}),(m:Movie {title:'Speed Racer'})
       MERGE (p)-[:ACTED_IN {roles:['Racer X']}]->(m)""",
    """MATCH (p:Person {name:'Christina Ricci'}),(m:Movie {title:'Speed Racer'})
       MERGE (p)-[:ACTED_IN {roles:['Trixie']}]->(m)""",
    """MATCH (p:Person {name:'Rain'}),(m:Movie {title:'Speed Racer'})
       MERGE (p)-[:ACTED_IN {roles:['Taejo Togokahn']}]->(m)""",
    """MATCH (p:Person {name:'Lilly Wachowski'}),(m:Movie {title:'Speed Racer'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Lana Wachowski'}),(m:Movie {title:'Speed Racer'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Joel Silver'}),(m:Movie {title:'Speed Racer'}) MERGE (p)-[:PRODUCED]->(m)""",

    # Ninja Assassin
    """MATCH (p:Person {name:'Rain'}),(m:Movie {title:'Ninja Assassin'})
       MERGE (p)-[:ACTED_IN {roles:['Raizo']}]->(m)""",
    """MATCH (p:Person {name:'Naomie Harris'}),(m:Movie {title:'Ninja Assassin'})
       MERGE (p)-[:ACTED_IN {roles:['Mika Coretti']}]->(m)""",
    """MATCH (p:Person {name:'Ben Miles'}),(m:Movie {title:'Ninja Assassin'})
       MERGE (p)-[:ACTED_IN {roles:['Ryan Maslow']}]->(m)""",
    """MATCH (p:Person {name:'James McTeigue'}),(m:Movie {title:'Ninja Assassin'}) MERGE (p)-[:DIRECTED]->(m)""",
    """MATCH (p:Person {name:'Joel Silver'}),(m:Movie {title:'Ninja Assassin'}) MERGE (p)-[:PRODUCED]->(m)""",

    # The Green Mile
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'The Green Mile'})
       MERGE (p)-[:ACTED_IN {roles:['Paul Edgecomb']}]->(m)""",
    """MATCH (p:Person {name:'Michael Clarke Duncan'}),(m:Movie {title:'The Green Mile'})
       MERGE (p)-[:ACTED_IN {roles:['John Coffey']}]->(m)""",
    """MATCH (p:Person {name:'David Morse'}),(m:Movie {title:'The Green Mile'})
       MERGE (p)-[:ACTED_IN {roles:['Brutal Howell']}]->(m)""",
    """MATCH (p:Person {name:'Bonnie Hunt'}),(m:Movie {title:'The Green Mile'})
       MERGE (p)-[:ACTED_IN {roles:['Jan Edgecomb']}]->(m)""",
    """MATCH (p:Person {name:'James Cromwell'}),(m:Movie {title:'The Green Mile'})
       MERGE (p)-[:ACTED_IN {roles:['Warden Hal Moores']}]->(m)""",
    """MATCH (p:Person {name:'Sam Rockwell'}),(m:Movie {title:'The Green Mile'})
       MERGE (p)-[:ACTED_IN {roles:["'Wild Bill' Wharton"]}]->(m)""",
    """MATCH (p:Person {name:'Gary Sinise'}),(m:Movie {title:'The Green Mile'})
       MERGE (p)-[:ACTED_IN {roles:['Burt Hammersmith']}]->(m)""",
    """MATCH (p:Person {name:'Patricia Clarkson'}),(m:Movie {title:'The Green Mile'})
       MERGE (p)-[:ACTED_IN {roles:['Melinda Moores']}]->(m)""",
    """MATCH (p:Person {name:'Frank Darabont'}),(m:Movie {title:'The Green Mile'}) MERGE (p)-[:DIRECTED]->(m)""",

    # Frost/Nixon
    """MATCH (p:Person {name:'Frank Langella'}),(m:Movie {title:'Frost/Nixon'})
       MERGE (p)-[:ACTED_IN {roles:['Richard Nixon']}]->(m)""",
    """MATCH (p:Person {name:'Michael Sheen'}),(m:Movie {title:'Frost/Nixon'})
       MERGE (p)-[:ACTED_IN {roles:['David Frost']}]->(m)""",
    """MATCH (p:Person {name:'Kevin Bacon'}),(m:Movie {title:'Frost/Nixon'})
       MERGE (p)-[:ACTED_IN {roles:['Jack Brennan']}]->(m)""",
    """MATCH (p:Person {name:'Oliver Platt'}),(m:Movie {title:'Frost/Nixon'})
       MERGE (p)-[:ACTED_IN {roles:['Bob Zelnick']}]->(m)""",
    """MATCH (p:Person {name:'Sam Rockwell'}),(m:Movie {title:'Frost/Nixon'})
       MERGE (p)-[:ACTED_IN {roles:['James Reston, Jr.']}]->(m)""",
    """MATCH (p:Person {name:'Ron Howard'}),(m:Movie {title:'Frost/Nixon'}) MERGE (p)-[:DIRECTED]->(m)""",

    # Hoffa
    """MATCH (p:Person {name:'Jack Nicholson'}),(m:Movie {title:'Hoffa'})
       MERGE (p)-[:ACTED_IN {roles:['Hoffa']}]->(m)""",
    """MATCH (p:Person {name:'Danny DeVito'}),(m:Movie {title:'Hoffa'})
       MERGE (p)-[:ACTED_IN {roles:['Robert Ciaro']}]->(m)""",
    """MATCH (p:Person {name:'John C. Reilly'}),(m:Movie {title:'Hoffa'})
       MERGE (p)-[:ACTED_IN {roles:['Frank Fitzsimmons']}]->(m)""",
    """MATCH (p:Person {name:'Danny DeVito'}),(m:Movie {title:'Hoffa'}) MERGE (p)-[:DIRECTED]->(m)""",

    # Apollo 13
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'Apollo 13'})
       MERGE (p)-[:ACTED_IN {roles:['Jim Lovell']}]->(m)""",
    """MATCH (p:Person {name:'Gary Sinise'}),(m:Movie {title:'Apollo 13'})
       MERGE (p)-[:ACTED_IN {roles:['Ken Mattingly']}]->(m)""",
    """MATCH (p:Person {name:'Ed Harris'}),(m:Movie {title:'Apollo 13'})
       MERGE (p)-[:ACTED_IN {roles:['Gene Kranz']}]->(m)""",
    """MATCH (p:Person {name:'Bill Paxton'}),(m:Movie {title:'Apollo 13'})
       MERGE (p)-[:ACTED_IN {roles:['Fred Haise']}]->(m)""",
    """MATCH (p:Person {name:'Kevin Bacon'}),(m:Movie {title:'Apollo 13'})
       MERGE (p)-[:ACTED_IN {roles:['Jack Swigert']}]->(m)""",
    """MATCH (p:Person {name:'Ron Howard'}),(m:Movie {title:'Apollo 13'}) MERGE (p)-[:DIRECTED]->(m)""",

    # Twister
    """MATCH (p:Person {name:'Bill Paxton'}),(m:Movie {title:'Twister'})
       MERGE (p)-[:ACTED_IN {roles:['Bill Harding']}]->(m)""",
    """MATCH (p:Person {name:'Helen Hunt'}),(m:Movie {title:'Twister'})
       MERGE (p)-[:ACTED_IN {roles:['Dr. Jo Harding']}]->(m)""",

    # Cast Away
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'Cast Away'})
       MERGE (p)-[:ACTED_IN {roles:['Chuck Noland']}]->(m)""",
    """MATCH (p:Person {name:'Robert Zemeckis'}),(m:Movie {title:'Cast Away'}) MERGE (p)-[:DIRECTED]->(m)""",

    # One Flew Over the Cuckoo's Nest
    """MATCH (p:Person {name:'Jack Nicholson'}),(m:Movie {title:"One Flew Over the Cuckoo's Nest"})
       MERGE (p)-[:ACTED_IN {roles:['Randle McMurphy']}]->(m)""",

    # Something's Gotta Give
    """MATCH (p:Person {name:'Jack Nicholson'}),(m:Movie {title:"Something's Gotta Give"})
       MERGE (p)-[:ACTED_IN {roles:['Harry Sanborn']}]->(m)""",
    """MATCH (p:Person {name:'Diane Keaton'}),(m:Movie {title:"Something's Gotta Give"})
       MERGE (p)-[:ACTED_IN {roles:['Erica Barry']}]->(m)""",
    """MATCH (p:Person {name:'Keanu Reeves'}),(m:Movie {title:"Something's Gotta Give"})
       MERGE (p)-[:ACTED_IN {roles:['Julian Mercer']}]->(m)""",

    # Bicentennial Man
    """MATCH (p:Person {name:'Robin Williams'}),(m:Movie {title:'Bicentennial Man'})
       MERGE (p)-[:ACTED_IN {roles:['Andrew Marin']}]->(m)""",
    """MATCH (p:Person {name:'Sam Neill'}),(m:Movie {title:'Bicentennial Man'})
       MERGE (p)-[:ACTED_IN {roles:['Richard Martin']}]->(m)""",

    # Charlie Wilson's War
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:"Charlie Wilson's War"})
       MERGE (p)-[:ACTED_IN {roles:["Rep. Charlie Wilson"]}]->(m)""",
    """MATCH (p:Person {name:'Julia Roberts'}),(m:Movie {title:"Charlie Wilson's War"})
       MERGE (p)-[:ACTED_IN {roles:['Joanne Herring']}]->(m)""",
    """MATCH (p:Person {name:'Philip Seymour Hoffman'}),(m:Movie {title:"Charlie Wilson's War"})
       MERGE (p)-[:ACTED_IN {roles:['Gust Avrakotos']}]->(m)""",
    """MATCH (p:Person {name:'Mike Nichols'}),(m:Movie {title:"Charlie Wilson's War"}) MERGE (p)-[:DIRECTED]->(m)""",

    # The Polar Express
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'The Polar Express'})
       MERGE (p)-[:ACTED_IN {roles:['Hero Boy', 'Father', 'Conductor', 'Hobo', 'Scrooge', 'Santa Claus']}]->(m)""",
    """MATCH (p:Person {name:'Robert Zemeckis'}),(m:Movie {title:'The Polar Express'}) MERGE (p)-[:DIRECTED]->(m)""",

    # A League of Their Own
    """MATCH (p:Person {name:'Tom Hanks'}),(m:Movie {title:'A League of Their Own'})
       MERGE (p)-[:ACTED_IN {roles:['Jimmy Dugan']}]->(m)""",
    """MATCH (p:Person {name:'Geena Davis'}),(m:Movie {title:'A League of Their Own'})
       MERGE (p)-[:ACTED_IN {roles:['Dottie Hinson']}]->(m)""",
    """MATCH (p:Person {name:'Lori Petty'}),(m:Movie {title:'A League of Their Own'})
       MERGE (p)-[:ACTED_IN {roles:['Kit Keller']}]->(m)""",
    """MATCH (p:Person {name:"Rosie O'Donnell"}),(m:Movie {title:'A League of Their Own'})
       MERGE (p)-[:ACTED_IN {roles:['Doris Murphy']}]->(m)""",
    """MATCH (p:Person {name:'Penny Marshall'}),(m:Movie {title:'A League of Their Own'}) MERGE (p)-[:DIRECTED]->(m)""",
]


def run_load():
    errors = []
    with driver.session(database=NEO4J_DATABASE) as session:
        for i, stmt in enumerate(STATEMENTS, 1):
            try:
                session.run(stmt)
            except Exception as e:
                errors.append((i, str(e)[:120]))
                print(f"  ✗ Statement {i}: {str(e)[:80]}")

    print(f"\n  Ran {len(STATEMENTS)} statements.")
    if errors:
        print(f"  {len(errors)} error(s):")
        for idx, msg in errors:
            print(f"    [{idx}] {msg}")
    else:
        print("  All statements succeeded.")


def verify():
    with driver.session(database=NEO4J_DATABASE) as session:
        counts = session.run(
            "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC"
        ).data()
        rels = session.run("MATCH ()-[r]->() RETURN count(r) AS total").single()["total"]
    print("\n  Node counts:")
    for row in counts:
        print(f"    {row['label']:20s} {row['count']}")
    print(f"  Relationships: {rels}")


if __name__ == "__main__":
    print("Loading Neo4j movie dataset...")
    run_load()
    print("\nVerifying...")
    verify()
    driver.close()
    print("\nDone.")
