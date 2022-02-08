# Lab1

#Project 1

ENGO 551

In a terminal window, navigate into your project1 directory and type out the following commands:

      pip3 install -r requirements.txt 
      set FLASK_APP=application.py
      set FLASK_DEBUG=1
      set DATABASE_URL=postgresql://haoscanbcqzbxe:236e01a4503b880a49481f3cf0e3b9c24e7ab3d4f19a1d71bd5684e4ddf938f2@ec2-54-208-139-247.compute-1.amazonaws.com:5432/dfivjs7g5fjh53
      flask run

I have already used the import.py file (via command: python3 import.py) to import the excel sheet of books into my database.

Project description:

      "In this project, you’ll build a book review website. Users will be able to register for your 
      website and then log in using their username and password. Once they log in, they will be able
      to search for books, leave reviews for individual books, and see the reviews made by other people. 
      You’ll also use the a third-party API by Google Books, another book review website, to pull in ratings 
      from a broader audience. Finally, users will be able to query for book details and book reviews programmatically 
      via your website’s API."
      
 Files:
 
    requirements.txt : flask and python requirements that need to be installed
    application.py : contains all the flask routes and SQL code
    import.py : imports the excel file of all the books of the database
    books.csv : all the books of the database
    templates: 
     - books.html: contains information of a single book
     - index.html: login and sign up page
     - layout.html: styling and layout template
     - message.html: message template used for alerts and errors etc
     - results.html: displays results from a search
     - search.html: searches for books
 
 API: The user can also get JSON results from the Google book api by typing /api/<isbn> directly into the URL.
    
