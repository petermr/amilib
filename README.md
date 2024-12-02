# amilib

Library to support downloading and analysis of documents, mainly from Open Access repositories, from 
published scholarly articles, or from authoritative sites such as UN IPCC or UNFCCC. The current version 2024-12-01 includes entry points but the longer term plan is to integrate with [docanalysis](https://github.com/petermr/docanalysis) and [pygetpapers](https://github.com/petermr/pygetpapers). That will give a onestop toolset for downloading Open Access articles/reports in bulk, making them semantic , and analysing them with NLP and AI/ML methods.

# components and tests

`amilib` is written as a set of libraries developed by test-driven-development (TDD). The main strategy is to tackle a real download/transform/analyse problem as a series of tests, and then abstract the tests into the library. The tests therefore act as a guide to functionality and simple how-tos. During development the libraries can be accessed through the command-line (`argparse`) and this is the current normal approach. (However we plan to move the main entry points for most users to `docanalysis`).
