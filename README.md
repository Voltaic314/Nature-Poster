# Art / Photo Poster

These scripts were created by Logan Maupin. I'm a student at the University of Arizona (Online) studying Applied Computing - Applied Artificial Intelligence. My goal is to one day create AI that can communicate & interface with humans and potentially detect threats or save humanity in some way. Specifically my field of choice is Natural Language Processing. If you don't know what I mean, check out GPT-3 or Gopher as examples of what I am referring to in a way. 

This project has been a fun side hobby of mine after I made the Reddit Meme poster. I originally had the thought of, after I made the meme poster, what if we made a bot that instead of sharing memes it just shares absolutely beautiful landscapes / nature photos / art drawings that people made. My original idea was to make a sort of tattoo art page that shares beautiful tattoo pictures automatically, but the problem is that this is hard to moderate in FB because most tattoo pics are usually labeled as NSFW so I settled upon beautiful landscapes, nature, and scenary art.

The way this script works is by making HTTP requests to DeviantArt, loading the HTML data in memory, looking for specific HTML tags that specify images on the page and things like the title and the user that posted it. We then grab that info and post it to a spreadsheet. Before it grabs that data though it checks to make sure that it hasn't ever grabbed that before. Unfortunately because it's web scraping, the only way to check this is by comparing the links, which doesn't help much. Luckily I put in image hashing in the script so we can check for duplicate images that way. 

Anyways, once it grabs the data of the post we want, it logs it to the deviant art log spreadsheet on google sheets. 

Then when the FB Poster script runs, it picks a random one from the DA spreadsheet, checks to make sure that image hash is not already in the list of already posted FB post logs on the FB Poster spreadsheet, then once it knows it hasn't posted that before, it will make a FB post with the image link in question, then once the post is made it will very quickly edit the post to add in the caption that we want. You can see this near the end of the FB Poster script. 

In the future I would love to use Deviant Art's actual API but there was not a python wrapper made that has what I need, so I'll need to get better at programming to figure out what to do with it. But we'll get there eventually as we get better. For now this will work. :) 

Thanks for reading. If you have questions feel free to reach out to me and if you have any suggestions on how to improve the code, feel free to make those suggestions to me! 

You can visit my FB page for this project at https://www.facebook.com/AutomaticNaturePosts/
