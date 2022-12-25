"""
Author: Logan Maupin

The purpose of this module is to create a list of methods that will assist in posting to FB.
"""
import requests
import facebook
import config


class FB_Posting:

    @staticmethod
    def post_photo_to_fb(photo: object):
        """
        This function posts to fb given a specific photo_url that
        you wish to use.
        :param photo: image object from pexels api search
        :returns: response from FB servers with the post id or an error
        """

        fb_page_id = "101111365975816"
        post_url = f'https://graph.facebook.com/{fb_page_id}/photos'
        payload = {
            "url": photo.large2x,
            "access_token": config.config_stuff['FB_Access_Token']
        }

        post_to_fb_request = requests.post(post_url, data=payload)
        return post_to_fb_request.text

    @staticmethod
    def post_video_to_fb(video: object):
        """
        This function posts to fb given a specific video_permalink that you wish to use.

        :param video: video object from pexels API search result
        :returns: response from FB servers with the post id or an error
        """

        fb_page_id = "101111365975816"
        post_url = f'https://graph.facebook.com/{fb_page_id}/videos'
        GitHub_Link = 'https://github.com/Voltaic314/Nature-Poster'
        message = f'Description: {video.description}\n\nPexels link: {video.url}\n\n' \
                  f'P.S. This Facebook post was created by a bot. To learn more about how it works, ' \
                  f'check out the GitHub page here: {GitHub_Link}'

        payload = {
            "file_url": video.link,
            "title": video.description,
            "description": message,
            "access_token": config.config_stuff['FB_Access_Token']
        }

        post_to_fb_request = requests.post(post_url, data=payload)
        return post_to_fb_request.text

    @staticmethod
    def edit_fb_post_caption_for_pexels_photo_posting(post_id, photo_description, photo_permalink):
        """
        This function takes a given FB post and edits a caption to it.

        :param post_id: any FB post you wish to edit.
        :param photo_description: what you wish to edit to it, preferably a str type
        :param photo_permalink: the link of the original pexels photo for credit
        :returns: None
        """

        fb_page_id = "101111365975816"
        GitHub_Link = 'https://github.com/Voltaic314/Nature-Poster'

        # define fb variable for next line with our access info
        fb = facebook.GraphAPI(access_token=config.config_stuff['FB_Access_Token'])

        # edit caption of existing fb post we just made
        fb.put_object(parent_object=f'{fb_page_id}_{post_id}', connection_name='',
                      message=f'Description: {photo_description}\n\nPexels image link: {photo_permalink}\n\n'
                              f'P.S. This Facebook post was created by a bot. To learn more about how it works, '
                              f'check out the GitHub page here: {GitHub_Link}')
