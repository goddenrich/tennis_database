README.txt
Killian Rutherford (krr2125)
Richard Godden (rg3047)

1. The database is found under the account rg3047

2. The url of the web application is: 104.155.226.83 port 8111 ie. insert 104.155.226.83:8111 to your browser

3. The application interacts in some way or another with all the entities and 
relationships in our final E/R diagram. According to the comments which were given by
our Project Mentor in part 1.2, we edited our timestamp values to include time zones.
According to what we described in part 1, "Users will be able to query this database
to discover player stats and match outcomes". This has been done in the player page.
"Logistics, enquiries about where the matches are taking place" are done in the
schedule page. "Ticket and spectator statistics" are located in the tournament page, including charts and figures.
On top of all our proposed applications, we have enabled the user to add in data into the database, specifically the Complex table, as we would not want the user to have to enter more complicated data and have to deal with satisfying all of the requirements, potentially rendering the database faulty.


4. The two web pages that require the most interesting database operations are:
        
     a. 104.155.226.83:8111/tournaments.html
        This page reports statistics of a user inputed tennis tournament. The user can enter the name of the tournament they wish to see. The page then displays a bargraph of the tickets numbers for each match that was or is sheduled to be played in that tournament as well as a pie chart of the split of the gender of the audience. The query for the ticket sales bar graph is particularly interesting because it links most tables in the database to find out the names of the two players in the match to give a more informative match name than the match id.

     b. 104.155.226.83:8111/players.html
        This page reports statistics on a certain player. The user inputs the player name for which they would like to know information about. 
If this name is not found, an error page is shown and the user is prompted to go back and input valid information. The player details page is interesting as it combines information from almost all tables, through use of complicated nested queries and joins to show the information. Although the information is simply displayed, a lot of sql queries are sitting on the backend.
Furthermore, from a web user interface, javascript functions were utilised to show the data on the click of reveal buttons.


Some HTML/javascript snippets of code may have directly been taken from "https://www.w3schools.com/" HTML tutorials 
