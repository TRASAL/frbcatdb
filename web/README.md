# FRBCat DB web

This is a flask-based web for browsing the FRBCat

It wants to replace the PHP-based version on https://github.com/AA-ALERT/frbcatweb

Execution:

Just run:

 `python app.py`

Current functionality:
 - The main page shows all the FRBs measurements (it is a join of the 4 main tables: frbs,obs,rops and rmps)
   It only shows the not-null columns in these tables
 - If one clicks in any row a new page is loaded with extended info about the Event
   The exception is if one clicks on the VOEvent column, in which case the XML of the VOEvent is shown
 - The page with extended info for an event contains 3 tables, once with the observations of the event, another one
   with the rops of the event and the final one with the rmps of the event. Similar to the main page, if one clicks
  on the VOEvent colum in the rmps table, the XML is shown
