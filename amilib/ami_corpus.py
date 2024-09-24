"""
downstream parser for pygetpapers
"""

class AmiCorpus():
    """

    """
    EUPMC_TRANSFORM = {
        "doi": {
            "url": {
                "prefix": "https://www.doi.org/",
            }
        },
        "authorString": {
            "text": {
                "split": ",",
            }
        },
        "abstractText": {
            "text": {
                "truncate": 200,
            }
        },
        "pmcid": {
            "url": {
                "prefix": "https://europepmc.org/betaSearch?query=",
            }

        }

    }
