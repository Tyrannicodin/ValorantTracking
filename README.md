# ValorantTracking
An open source tracking program for collecting VALORANT data. It has options to share with my server to see data on VALORANT players and make some nice graphs which you will be able to view below when they are ready.

## Collecting data
To collect your data, simply play a game whilst the program is running and the track checkbox is ticked. The tracker will automatically wait for a new game and record it. If you weren't running the program whilst playing the game you cn click view history and select a game to add to the tracking data.

## Viewing data
To view your data, click view data, then select the format and time range. The requested data can then be viewed and saved as png format. Optionally select dump info to get a json file with all recorded games.

## Submitting data
To submit data, simply click submit data. If the server is currently accepting data the button will go green, then go back to gray once submitted. You can see the results of the file upload in logs\\upload.json. If it fails it will go red, this could be due to an error in uploading or that the server is not up.