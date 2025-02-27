# Ainara - Open Source AI Assistant Framework
# Copyright (C) 2025 Rubén Gómez http://www.khromalabs.org

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, see
# <https://www.gnu.org/licenses/>.

import logging
import os

from newsapi import NewsApiClient

from ainara.framework.config import config
from ainara.framework.skill import Skill

SUPPORTED_LANGUAGES = {
    "ar",
    "de",
    "en",
    "es",
    "fr",
    "he",
    "it",
    "nl",
    "no",
    "pt",
    "ru",
    "sv",
    "zh",
}


class SearchNews(Skill):
    """Search news articles using NewsAPI"""

    def __init__(self):
        super().__init__()
        # logging.getLogger().setLevel(logging.DEBUG)
        api_key = os.getenv("NEWSAPI_KEY") or config.get(
            "apis.news.api_key", {}
        )
        if not api_key:
            raise ValueError("NEWSAPI_KEY environment variable is required")
        self.newsapi = NewsApiClient(api_key=api_key)

    async def run(
        self,
        query: str,
        language: str = "en",
        sort_by: str = "popularity",
        from_date: str = None,
        to_date: str = None,
    ):
        """
        Search for news articles matching the query using NewsAPI

        Args:
            query: Search query string
            language: Language code (default: 'en'). Must be one of:
            ar, de, en, es, fr, he, it, nl, no, pt, ru, sv, zh
            sort_by: Sort order ('relevancy', 'popularity', 'publishedAt')

        Returns:
            Dict containing search results
        """

        logging.debug(
            f"NewsSearch.run() called with parameters: query='{query}',"
            f" language='{language}' ({type(language)}), sort_by='{sort_by}',"
            f" from_date='{from_date}', to_date='{to_date}',"
        )

        # Validate query
        if not isinstance(query, str):
            return {
                "status": "error",
                "message": f"Query must be a string, got {type(query)}",
            }

        if not query or query.strip() == "" or query == "query":
            return {
                "status": "error",
                "message": "Query parameter cannot be empty or invalid",
            }

        # Validate language code
        if not isinstance(language, str):
            return {
                "status": "error",
                "message": f"Language must be a string, got {type(language)}",
            }

        # Check for unprocessed template variables
        if "{{" in language or "}}" in language:
            return {
                "status": "error",
                "message": (
                    "Invalid language parameter: contains template markers"
                ),
            }

        language = language.lower().strip()
        logging.debug(
            f"After cleaning, language code: '{language}', type:"
            f" {type(language)}"
        )
        logging.debug(f"Supported languages: {sorted(SUPPORTED_LANGUAGES)}")
        if language not in SUPPORTED_LANGUAGES:
            return {
                "status": "error",
                "message": (
                    "Invalid language code. Must be one of:"
                    f" {', '.join(sorted(SUPPORTED_LANGUAGES))}"
                ),
            }
        try:
            logging.info(
                f"Searching news with query='{query}' language='{language}'"
                f" sort_by='{sort_by}'"
            )
            # Build parameters dict
            params = {
                "qintitle": query,
                "language": language,
                "sort_by": sort_by,
            }

            # Add optional parameters if provided
            if from_date:
                params["from_param"] = from_date
            if to_date:
                params["to"] = to_date

            logging.debug(f"Calling NewsAPI with parameters: {params}")
            response = self.newsapi.get_everything(**params)
            logging.info(f"Got {len(response['articles'])} results")

            # Format the results
            articles = []
            for article in response["articles"][:5]:  # Limit to top 5 results
                articles.append(
                    {
                        "title": article["title"],
                        "description": article["description"],
                        "url": article["url"],
                        "source": article["source"]["name"],
                        "published": article["publishedAt"],
                    }
                )

            return {
                "status": "success",
                "total_results": len(articles),
                "articles": articles,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
