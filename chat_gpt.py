'''
Author: Logan Maupin

This module handles the ChatGPT class object. Specifically, ChatGPT 
is used primarily for photo filtering to make sure photos are on 
topic for the page. 
'''
import g4f


class ChatGPT:

    def __init__(self, caption_text: str, img_text: str) -> None:
        self.caption_text = caption_text
        self.prompt = ''
        self.discord_char_limit = 2_000

    def set_char_limit(self, char_limit: int):
        self.prompt += f"Please respond with a message that is less than or equal to {char_limit} characters long. "

    def setup_initial_prompt(self):
        initial_prompt_str = ''
        initial_prompt_str += 'Hello ChatGPT. I have some text that is a caption of a photo.\n'
        initial_prompt_str += 'Based on this text, I need to make your best guess as to whether or not the image is a nature photo or not.\n'
        initial_prompt_str += 'In order for the photo to be a nature photo, the subject of the photo should be about some geographical landscape feature. \n'
        initial_prompt_str += 'Examples include: Pictures of a mountain, sunset, lake, ocean, coral reef, forest... things like that. \n'
        initial_prompt_str += 'People are generally not allowed in the photos because I do not want the image to be centered around a person, they need to be a background character. \n'
        initial_prompt_str += 'However, seeing as how you can not see the image, I am going to say as a general rule of thumb, if you see a trigger word in the caption that identifies a person in the image, just say it\'s not a nature photo.\n'
        initial_prompt_str += 'I am also trying to avoid images where it\'s just a flower on a desk or something of that nature. \n'
        initial_prompt_str += 'If you are unsure, err on the side of the photo being on topic, we can always filter it later, but do your best to try to make your best possible guess. \n'
        initial_prompt_str += 'Please just respond with "True" or "False, do not say anything else in your response for now. \n'

        self.prompt += initial_prompt_str

    def add_caption_and_ocr_text(self):
        self.prompt += f"Okay here is the caption text: {self.caption_text}\n"
        self.prompt += "Based on that text, do you think this is a nature photo? True or False only."

    def setup_prompt(self):
        self.set_char_limit(self.discord_char_limit)
        self.setup_initial_prompt()
        self.add_caption_and_ocr_text()

    @property
    def response(self) -> str:
        '''
        This will return a response from the GPT 3.5 Turbo model based on whatever your input was.
        Specifically this uses text completion. 

        Parameters: 
        message: str - string of the message you want the model to complete

        Returns: str - string response of what the AI said back in return.
        '''
        self.setup_prompt()

        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": self.prompt}],
        )

        return response
