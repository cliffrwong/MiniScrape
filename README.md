# MiniScrape

##Description

IMDB & Amazon ASIN mini-scraper

This python TkInter applicaton allows the user to search a movie title, select the correct movie from a list, and the application then extracts the IMDB ID, IMDB image URL, Amazon Standard Identification Numbers (ASINs), title, release year, etc. for the movie.

Type the movie name into the search box in the top, movie results will appear in the listbox below. The selected movie's poster will appear below that to help differentiate movie's with similar names. Hit enter or double click the selected movie name. The movie's information will be printed in stdout. 	

This version only prints out the movie's information into stdout. But you can modify insert2DB() in addmovie_util.py to direct the data where you please, such as saving in your DB. You can also modify the function alreadyExist() in addmovie_util.py to check if the movie is already in your DB.

### Screenshot
![alt tag](https://raw.githubusercontent.com/cliffrwong/MiniScrape/master/img/screenshot.png)

This mini-scraper can be extended in various ways:

1. extract multiple movies from IMDB's site. Instead of inputting a movie title in the searchbox, it can be changed to a URL that contain many movies.

2. add additional stages to extract information from other sites such as rottentomatoes.com or justwatch.com

3. when your scraping algorithm is uncertain about which choice to make, the UI allows the user to intervene and manually make a choice while having all the relevant information available. 


##How to Run
requires python 3. Tested on python 3.4+

Install tkinter (if not installed already)

http://www.tkdocs.com/tutorial/install.html 


git clone https://github.com/cliffrwong/MiniScrape.git

cd MiniScrape

pip install -r requirements.txt

python main.py
