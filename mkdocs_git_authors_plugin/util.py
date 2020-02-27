from git import Repo
import logging
from pathlib import Path

class Util:

    def __init__(self, path = "."):
        self.repo = Repo(path, search_parent_directories=True)
        # Cache authors entries by path
        self._authors = {}

    def get_authors(self, path):
        """
        Determine git authors for a given file

        Args:
            path (str): Location of a file that is part of a GIT repository

        Returns:
            list (str): unique authors, or empty list
        """

        authors = self._authors.get(path, [])

        if authors == False:
            return []

        if authors:
            return authors

        try:
            blame = self.repo.blame('HEAD',path)
        except:
            logging.warning("%s has no commits" % path)
            self._authors[path] = False
            return []

        if len(Path(path).read_text()) == 0:
            logging.warning("%s has no lines" % path)
            self._authors[path] = False
            return []

        authors = {}
        for commit, lines in blame:
            key = commit.author.email

            # Update existing author
            if authors.get(key):
                authors[key]['lines'] = authors[key]['lines'] + len(lines)
                current_dt = authors.get(key,{}).get('last_datetime')
                if commit.committed_datetime > current_dt:
                    authors[key]['last_datetime'] = commit.committed_datetime
            # Add new author
            else:
                authors[key] = {
                    'name' : commit.author.name,
                    'email' : key,
                    'last_datetime' : commit.committed_datetime,
                    'lines' : len(lines)
                }

        authors = [authors[key] for key in authors]
        authors = sorted(authors, key = lambda i: i['name'])

        total_lines = sum([x.get('lines') for x in authors])
        for author in authors:
            author['contribution'] = self._format_perc(author['lines'] / total_lines)

        self._authors[path] = authors

        return authors

    @staticmethod
    def _format_perc(n, decimals = 2):
        """Formats a decimal as a percentage

        Args:
            n (float): [description]
        """
        assert n >= 0
        assert n <= 1
        return str(round(n * 100, decimals)) + '%'

    @staticmethod
    def summarize(authors, config):
        """
        Summarized list of authors to a HTML string

        Args:
            authors (list): List with author dicts

        Returns:
            str: HTML text with authors
        """

        def format_author(author):
            contrib = (
                ' (%s)' % author['contribution']
                if (
                    config['show_contribution']
                    and len(authors) > 1
                )
                else ''
            )
            return "<a href='mailto:%s'>%s</a>%s" % (
                author['email'],
                author['name'],
                contrib
            )

        authors_summary = [format_author(author) for author in authors]
        authors_summary = ', '.join(authors_summary)
        return "<span class='git-authors'>" + authors_summary + "</span>"
