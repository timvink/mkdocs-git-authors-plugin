from git import Git

class Util:

    def __init__(self):
        self.g = Git()

    def get_authors(self, path: str, type: str = 'authors'):
        """
        Determine git authors for a given file
        
        Args:
            path (str): Location of a file that is part of a GIT repository
            type (str, optional): How to determine authors. Defaults to 'en'.
        
        Returns:
            str: unique authors
        """
        
        authors = self.g.log(path, n=1, date='short', format='%at')
        # authors = "Tim Vink 1, Tim Vink 2"
        return authors