# semanticClimate : 
A global citizen science movement using open notebook science. 
We believe in Fairification of data or Fair data principles which are absolutely required and necessary today to transform information into structured, filtered and actionable knowledge.

# semanticClimate toolkit
![Our tools](https://imgur.com/tqB6IOu.jpg)




## amilib
Amilib is a Python library designed for document processing, and dictionary creation. It has tools for finding, cleaning, converting, searching, republishing legacy documents (PDF, PNG, etc.).
![Our tools](https://imgur.com/henOojC.jpg)


We can also annotate HTML IPCC chapters with the dictionary.

![Annotated chapters](https://imgur.com/AlwIsCk.jpg)

[Demo](https://colab.research.google.com/drive/1Lb_s2eyKiT1GeWdNZEXpGWPxSIidPpy8?usp=sharing) to collab of dictionary and annotated  chapters 


## pygetpapers
pygetpapers is a tool to assist text miners. It makes requests to open access scientific text repositories, analyses the hits, and systematically downloads the articles without further interaction. 

![downloaded papers](https://imgur.com/RKAZZhe.jpg)

The data table is created by using `amilib` which summarizes all the important metadata of the corpus.

![pygetpapers](https://imgur.com/JneWwyu.jpg)


## docanalysis


It extracts meaningful data and insights by carrying out text analysis of documents including

1. sectioning
2. NLP/text-mining
3. dictionary generation

![docanalysis](https://imgur.com/B48wht0.jpg)

`docanalysis` can analyse the literature corpus retrieved by `pygetpapers` and extract seperate entities such as all the countries mentioned in the corpus

![wordcloud](https://imgur.com/0rPqfCg.jpg)




























