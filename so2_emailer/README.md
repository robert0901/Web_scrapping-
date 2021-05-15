# SO<sub>2</sub> Webscraper
## The Problem
My team at work needed to track 12 SO<sub>2</sub> monitors in different regions of Texas to make sure they were complying with the Data Requirements Rule (DRR) for the 2010, One-Hour SO<sub>2</sub> Primary NAAQS, 80 FR 5105
In the beginning, this task was done by hand by checking each monitor individualy each day. 

## The Solution
I created this emailer script that takes advantage of an already existing webscraper created by Fernando Mercado at the TCEQ. This emailer extension is on Linux Crontab schedular that is ran each day during the weekdays. There is another script that is ran Monday but considers if any events occur during the weekend.

The data for SO<sub>2</sub>, wind speed, and wind direction are downloaded then are SO<sub>2</sub> values are checked to see if they are over the NAAQS standard. If they are over the standard, a table is created and reported to team members. 

With this emailer, the team can save time in the morning by not checking monitors and only needing to write the report to upper mangement when an event does occur.

## Table Example: 
![alt text][logo]

[logo]: https://github.com/robert0901/Web_scrapping-/blob/main/so2_emailer/tableExample1.png "Table"
