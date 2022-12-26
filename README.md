# Nature Poster
# Created by: Logan Maupin

These scripts were created by Logan Maupin. I'm a student at the University of Arizona studying Applied Computing - Applied Artificial Intelligence. My goal is to one day create AI that can communicate & interface with humans and potentially detect threats or save humanity in some way.

This project has been a fun side hobby of mine after I made the Reddit Meme poster. I originally had the thought of, after I made the meme poster, what if we made a bot that instead of sharing memes it just shares absolutely beautiful landscapes / nature videos / art drawings that people made. My original idea was to make a sort of tattoo art page that shares beautiful tattoo pictures automatically, but the problem is that this is hard to moderate in FB because most tattoo pics are usually labeled as NSFW so I settled upon beautiful landscapes, nature, and scenary art.

------------------------

How does it work? 

Basically it calls Pexels API and searches photos by key terms through a word list in the master spreadsheet. It will pick through those search results to make sure they are not NSFW or contain any badwords, and also ones that haven't been posted before. Once it finds a photo that meets that criteria, it will post it to FB. Once posted to FB, it will log the post to a google sheet so we can keep track of when & what was posted. This helps us keep down on duplicate posts. 

This script also uses OCR and Image Hashing as well. The OCR is used to detect bad words in photos. The hashing functions are used to make sure we don't post exact duplicates. Though in rare cases, some duplicates may still get through. I think Pexels also has a duplicate protection feature built in but this is more for our own redundancy more than anything else. 

Thanks for reading. If you have questions feel free to reach out to me and if you have any suggestions on how to improve the code, feel free to make those suggestions to me! 

You can visit my FB page for this project at https://www.facebook.com/AutomaticNaturePosts/


------------------------
1 big issue with this code and 2 minor things:

TODO: (see below issues)

1. it will always look through the same photos and check them over and over until new photos are uploaded
to replace the old ones, so this code may not be the most efficient. i.e. if there is a list of 5 photos,
and the first 4 don't meet the criteria, then it posts the last one... then another photo is uploaded to that list
on pexels, then now it will check the first 4 photos (again), skip the fifth one it posted before, and
now the new one and maybe post it. I could solve this problem by keeping a DB of checked post ID's, but
seems too storage intensive, might save a lot of resources elsewhere though.

2. The other thing is that if it has a good photo and tries to post it but FB is down, it will just discard that
photo altogether instead of trying to save it for a rainy day. There is a way to fix this but eh. I want it
to be completely automated so I'm not gonna bother.

3. We don't have a way to check if the photo was deleted or not after it was posted. This is important to know
if you're going to train a ML model on these photos. As ones that were deleted obviously didn't fit the
nature photo theme. Which could throw off your data. I can add a column for that in the DB tables, but,
I'm not sure how I would check each post to see if it got deleted or not. Not without pinging FB API like
10,000 times a day. Maybe if any of you have a better solution, let me know.
