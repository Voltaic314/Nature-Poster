# **Nature Poster**

### Developed by **Logan Maupin**

I'm a student at the University of Arizona studying Applied Computing with an emphasis in Applied Artificial Intelligence. I hope to one day create and work on AI for detecting threats and/or aiding human development. Nature Poster is an automatic Facebook posting bot I developed with Python as a side project.

🌱 🌲 🌿 🌳

---

## What is Nature Poster?

![Facebook page for Beautiful Worlds](/documentation-images/beautifulWorldsfb.png)

Nature Poster is an automatic bot scripted to periodically make nature-themed photography and video posts to the [Beautiful Worlds Facebook account](https://www.facebook.com/AutomaticNaturePosts/).

### Example posts:

- Photograph of a snowy tree branch
  ![Closeup photo of a tree branch with snow](/documentation-images/example-image-post.png)
- Video of a fish and a turtle near coral
  ![Fish and turtle under the sea](/documentation-images/example-video-post.png)

The posts include a short, simple description of the image or video and a url link to the original content source. All images and videos are sourced exclusively from Pexels, a copyright-free site for high resolution stock media.

## **How does it work?**

Nature Poster searches for and retrieves photos/videos via GET requests to the Pexels API. The API returns 15 photos/videos constituting a single page's worth of results, and the bot can access further pages if no result from the initial batch translates to a successful Facebook post.

The bot randomly selects a search term from a list of nature-related terms in a SQLite3 table named _Photo_Search_Terms_.

![SQLite3 table GUI first ten rows in Photo_Search_Terms](/documentation-images/photo_search_terms.png)

Basically it calls Pexels API and searches photos by key terms through a word list in the master spreadsheet. It will pick through those search results to make sure they are not NSFW or contain any badwords, and also ones that haven't been posted before. Once it finds a photo that meets that criteria, it will post it to FB. Once posted to FB, it will log the post to a google sheet so we can keep track of when & what was posted. This helps us keep down on duplicate posts.

This script also uses OCR and Image Hashing as well. The OCR is used to detect bad words in photos. The hashing functions are used to make sure we don't post exact duplicates. Though in rare cases, some duplicates may still get through. I think Pexels also has a duplicate protection feature built in but this is more for our own redundancy more than anything else.

Thanks for reading. If you have questions feel free to reach out to me and if you have any suggestions on how to improve the code, feel free to make those suggestions to me!

You can visit my FB page for this project at https://www.facebook.com/AutomaticNaturePosts/

---

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
