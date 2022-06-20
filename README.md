# Art / Photo Poster

These scripts were created by Logan Maupin. I'm a student at the University of Arizona (Online) studying Applied Computing - Applied Artificial Intelligence. My goal is to one day create AI that can communicate & interface with humans and potentially detect threats or save humanity in some way. Specifically my field of choice is Natural Language Processing. If you don't know what I mean, check out GPT-3, IBM's Watson, or Gopher, as examples of what I am referring to. 

This project has been a fun side hobby of mine after I made the Reddit Meme poster. I originally had the thought of, after I made the meme poster, what if we made a bot that instead of sharing memes it just shares absolutely beautiful landscapes / nature photos / art drawings that people made. My original idea was to make a sort of tattoo art page that shares beautiful tattoo pictures automatically, but the problem is that this is hard to moderate in FB because most tattoo pics are usually labeled as NSFW so I settled upon beautiful landscapes, nature, and scenary art.

The way this bot works (now) is by grabbing photos from Pexels API given a list of possible source search queries to use. Primarily nature & landscape related photos. Once it grabs a photo it logs it to a spreadsheet where the FB Poster script will then grab from that spreadsheet and post one and remove the entry from the original log file. Once FB Poster posts, edits in its caption, then removes it from the spreadsheet, it logs that info to the FB Poster log sheet. :) 

Thanks for reading. If you have questions feel free to reach out to me and if you have any suggestions on how to improve the code, feel free to make those suggestions to me! 

You can visit my FB page for this project at https://www.facebook.com/AutomaticNaturePosts/
