# ex-arukereso
Keboola connection extraktor from administration portal of Arukereso.hu

## Description
Extraktor provides daily statistics on individual product level available from http://www.arukereso.hu/admin/AkStatistics after the login. 
There are two way to input the period of interest 

a) number of past days starting from yesterday, 

b) close interval of date in format YYYY/MM/DD.

## Available Statistics
- *Date*, primary key
- *Product*, primary key -  name of the product
- *Category*, 
- *ClickThrough*, number of clicks 
- *TotalCost*, total cost of clicks
- *DefaultPrice*, cost per click
- *AVGPosition*, !!! empty for product granularity
- *OtherPrice*, !!! empty for product granularity
- *SelfProductView*, !!! empty for product granularity

## Usage
You could access the Arukereso extractor in Keboola project after login by adding to URL path 

*.../extractors/revolt-bi.ex-arukereso*


Prepared by  ![alt text](https://www.revolt.bi/wp-content/uploads/2018/08/mail-logo-zluta.png "revolt.bi")
