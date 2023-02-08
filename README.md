# **Nature Poster**

### Developed by **Logan Maupin**

I'm a student at the University of Arizona studying Applied Computing with an emphasis in Applied Artificial Intelligence. I hope to one day create and work on AI for detecting threats and/or aiding human development. Nature Poster is an automatic Facebook posting bot I developed with Python as a side project.

If you have any questions or suggestions on how to improve the code, feel free to reach out to me!

[Link to Facebook page Nature Poster makes posts to](https://www.facebook.com/AutomaticNaturePosts/)

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

The posts include a short, simple description of the image or video and a URL link to the original content source. All images and videos are sourced exclusively from Pexels, a royalty free site for high resolution stock media.

## **How does it work?**

### **Pexels API GET Request**

Nature Poster searches for and retrieves photos/videos via GET requests to the Pexels API.

- Example endpoint with arbitrarily selected query:

```
GET https://api.pexels.com/v1/search?query=sunset&per_page=15
```

The script uses the pexels_api Python client library to make requests.

Request parameters have been configured so that the API response always returns 15 photos or videos as a single page's worth of results. The script has access to further pages if no result from the initial batch converts to a successful Facebook post.

- Example response for single photo:

```json
{
  "id": 2014422,
  "width": 3024,
  "height": 3024,
  "url": "https://www.pexels.com/photo/brown-rocks-during-golden-hour-2014422/",
  "photographer": "Joey Farina",
  "photographer_url": "https://www.pexels.com/@joey",
  "photographer_id": 680589,
  "avg_color": "#978E82",
  "src": {
    "original": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg",
    "large2x": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "large": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "medium": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&h=350",
    "small": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&h=130",
    "portrait": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=800",
    "landscape": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
    "tiny": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=200&w=280"
  },
  "liked": false,
  "alt": "Brown Rocks During Golden Hour"
}
```

A query to the search endpoint returns as data an object with a list of 15 photo objects like the one above.

### **Selecting a search term**

The bot randomly selects a search term from a list of nature-related terms in a SQLite3 database table named _Photo_Search_Terms_.

![SQLite3 table GUI first ten rows in Photo_Search_Terms](/documentation-images/photo_search_terms.png)

### **Processing results and criteria**

Once the list of images or videos from the API has been fetched, the bot loops through it. For each image or video, it sequentially cycles through criteria to determine if the image or photo meets the requirements to be posted.

Photo processing is accomplished via a method belonging to the **Pexels_Photo_Processing** class in the _Nature_Poster_Photos_ module. Video processing is accomplished via a method belonging to the **Pexels_Video_Posting** class in the _Nature_Poster_Videos_ module.

At the first failed criterion, the bot discards the image or video under consideration, and the loop shifts to the next item.

These criteria include:

- Photo or video description parsed from URL cannot contain a prohibited word, as this would be considered NSFW media.
- Photo itself cannot contain a prohibited word either as a caption or displayed on any object, structure, or item of apparel, as this would be considered NSFW media.
- Photo or video must have an acceptable file extension, i.e., jpg, png, etc., if photo.
- Photo or video cannot be a duplicate post; it must not already be in either the database table _Nature_Bot_Logged_FB_Posts_ or _Nature_Bot_Logged_FB_Posts_Videos_.
- Hash string of downloaded image must not already be in the database. This criterion is necessary because the same photo can be reposted on Pexels with a different ID.
- Video file size must be smaller than 1 GB, and photo file size must be smaller than 4 MB.
- Video duration must be shorter than 20 minutes long, to comply with Facebook post limitations.

An instance of an image with text that would be picked up by OCR:
![Storefront image with neon lettering](/documentation-images/text-in-img.jpg)

### _Optical Character Recognition_

OCR is a process carried out to detect and convert text in an image to an easily usable data type like a string.

The bot integrates the Pytesseract OCR package and the cv2 computer vision package, which in conjunction work to detect characters in our images.

cv2 functions are used to load an image from a file, then convert that image to a different color space. This second step is key.

Lighting conditions are an extremely important factor in computer vision and are usually the difference between OCR algorithms failing or succeeding to detect characters.

Our OCR image processing result is a string whose words are then checked for a bad or prohiibted word.

```python
image_text = Image_Processing.ocr_text("image.jpg")

if Text_Processing.there_are_badwords(image_text, bad_words_list):
      continue
```

### **Posting to Facebook**

If an image or video candidate survives all the foregoing criteria, then the bot attempts to post it to Facebook with a network request to the Facebook API.

If the attempt fails, the bot moves on to the next image or video and processes it through the same sequence of relevant filtering criteria.

The script allows for five attempts before stopping the loop through the media list. Such a decision is a crucial fail-safe meant to ensure the script does not become trapped in an infinite loop if Facebook servers are unresponsive due to an ongoing issue.

### **Creating the caption**

After a successful media post to Facebook, the bot still needs to programmatically construct the post caption, including a description, a Pexels URL, and a P.S. section with a link to the bot's Github repository.

The photo and caption on a Facebook post cannot be created simultaneously with a single POST request. For this reason, the bot must first create the image post, then edit and append the caption.

```python
# edit caption of existing fb post we just made
fb.put_object(parent_object=f'{fb_page_id}_{post_id}', connection_name='',message=f'Description: {photo_description}\n\nPexels image link: {photo_permalink}\n\n'
f'P.S. This Facebook post was created by a bot. To learn more about how it works, '
f'check out the GitHub page here: {GitHub_Link}')
```

Another example caption:
![Example caption for successful photo post](/documentation-images/example-caption.png)

### **Inserting data into sqlite3 db**

Post officially complete, the bot will then insert metadata about the post (media description, media URL, hash string, file size, Facebook post ID, etc.) to the _Nature_Bot_Logged_FB_Posts_ or _Nature_Bot_Logged_FB_Posts_Videos_ table.

Post data recorded in these tables will be checked against in subsequent post attempts to prevent duplicates.

---

## Issues and areas for improvement

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
