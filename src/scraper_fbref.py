from bs4 import BeautifulSoup
import  pandas as pd
import requests
import pathlib

df = pd.read_html("https://fbref.com/en/squads/206d90db/Barcelona-Stats")
print(df[0])
print(df[2])

