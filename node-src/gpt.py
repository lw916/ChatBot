class Prompt:
    movie_comment = str('generate me 2 comment about movie "{}", without any external content, only the comment, '
                        'perform as one single python list.')

    down_prompt = str('I\'m now upset that a randomly generated quote encourages me, without any external content, '
                      'to behave as a string without quotation marks.')

    recommend_prompt = str('I\'m {} now, randomly recommend me two movies, without any external content, only the '
                           'movie name, and perform as one single python list.')

    recommend_prompt_none = str('Randomly recommend me two movies, without any external content, only the '
                                'movie name, and perform as one single python list.')

    def comment(self, movie_name: str):
        return self.movie_comment.format(movie_name)

    def down(self):
        return self.down_prompt

    def recommend(self, mood):
        if mood is None:
            return self.recommend_prompt_none

        return self.recommend_prompt.format(str(mood))
