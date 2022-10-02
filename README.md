# Nature Poster
# Created by: Logan Maupin

These scripts were created by Logan Maupin. I'm a student at the University of Arizona studying Applied Computing - Applied Artificial Intelligence. My goal is to one day create AI that can communicate & interface with humans and potentially detect threats or save humanity in some way.

This project has been a fun side hobby of mine after I made the Reddit Meme poster. I originally had the thought of, after I made the meme poster, what if we made a bot that instead of sharing memes it just shares absolutely beautiful landscapes / nature videos / art drawings that people made. My original idea was to make a sort of tattoo art page that shares beautiful tattoo pictures automatically, but the problem is that this is hard to moderate in FB because most tattoo pics are usually labeled as NSFW so I settled upon beautiful landscapes, nature, and scenary art.

-----------------------

How does it work? 

Basically it calls Pexels API and searches photos by key terms through a word list in the master spreadsheet. It will pick through those search results to make sure they are not NSFW or contain any badwords, and also ones that haven't been posted before. Once it finds a photo that meets that criteria, it will post it to FB. Once posted to FB, it will log the post to a google sheet so we can keep track of when & what was posted. This helps us keep down on duplicate posts. 

This script also uses OCR and Image Hashing as well. The OCR is used to detect bad words in photos. The hashing functions are used to make sure we don't post exact duplicates. Though in rare cases, some duplicates may still get through. I think Pexels also has a duplicate protection feature built in but this is more for our own redundancy more than anything else. 

Thanks for reading. If you have questions feel free to reach out to me and if you have any suggestions on how to improve the code, feel free to make those suggestions to me! 

You can visit my FB page for this project at https://www.facebook.com/AutomaticNaturePosts/
