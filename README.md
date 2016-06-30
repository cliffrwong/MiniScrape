IMDB & Amazon ASIN mini-scraper

This python desktop applicaton allows you to query a movie title, select the desired movie from a list, and it then extract the IMDB ID, IMDB image URL, Amazon Standard Identification Numbers (ASINs), title, release year, etc. for the movie. It is a stripped down version of a tool that I find very useful. 

Type the movie name into the search box in the top, movie results will appear in the listbox below. The selected movie's poster will appear below that to help differentiate movie's with similar names. 

This mini-scraper can be extended in various ways:
1. extract multiple movies from IMDB's site. Instead of inputting a movie title in the searchbox, it can be changed to a URL that can contain many movies.
2. add additional stages to extract information from other sites such as rottentomatoes.com or justwatch.com
3. when your scraping algorithm is uncertain which choice to make, the benefit of the UI allows the user to intervene and manually make a decision while have all the relevant information available. 

This version only prints out the movie's information into stdout. But you can modify insert2DB() in addmovie_util.py to save the information where you please such as your DB. You can also modify the function alreadyExist() in addmovie_util.py to check if the movie is already in your DB.

Requirements:
python 3

Install tkinter 

Mac: https://www.lynda.com/Tkinter-tutorials/
Installing-Python-3-TclTk-Mac/163607/184090-4.html
Linux: http://tkinter.unpythonic.net/wiki/How_to_install_Tkinter

Note: I had issues when following install direction for python2

pip install Pillow

Note: install tcl/tk before installing Pillow

pip install beautifulsoup4

git clone https://github.com/cliffrwong/MiniScrape.git
cd MiniScrape
python3 main.py

# MiniScrape
