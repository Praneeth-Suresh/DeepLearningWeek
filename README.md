# 'Truthflow' - A Multi-Source News Verification Framework
 
## What is Truthflow
 
Truthflow is an app *designed for users to assess the accuracy of a news piece by comparing it with multiple other reliable* sources of information (such as news articles, governmental websites and peer-reviewed academic journals). The system would return the facts rewritten accurately, as well as the other sources of information used in the verification process.
 
## How does truth flow through Truthflow
To understand how our model works, understand what our goal is:

> Social media verification based on cross reference with established media outlets and government databases

Start at building our fortée; the datastore:
We use Chroma DB to handle our files since it is a lightweight yet powerful Vector DB manager. It is populated with the following data:
1. Trendy news collected through the scraper. Our scraper is built with `urlib` and `BeautifulSoup` and can extract text from around the web. This is incidentally also what supplies our social media data extraction.
2. Processing to extract Exaggeration score and Cross Reference score. The biceps of our model can be found in `Analyser.py`. These serve as proxies for validity:
	*Cross reference score* : (measures reliability)
    Convert all into vector embeddings and find similarity scores. The one with the highest average is the best endorsed by the others.
    *Exaggeration score*: (measures accuracy)
    Exaggeration is a specific way in which documents potentially overstate certain aspects of their actual topic.
3. Storing in Vector DB (of course after chunking and embedding)

Now we are good to go for the day: we can easily retrieve info of the current days.

Then, when we come to the user level there can be two scenarios:
1. A user wants to input a link to a social media site
    In this case our scraper will obtain the text for us. 
2. The user inputs a picture
    We take the picture, squeeze it across the REST API to our Django backend server. Here, `easyocr` takes care of the rest.

All our powerful scrapers can be found in `ScraperModels.py`.

Text is processed by a series of Foundation Models from a collection of Open Source Generative AI APIs:
- Put simply facts are extracted, verified and then the text is deconstructed to see how the logic fits in.
- Again, go see how `Analyser.py` does this.

Image is processed by two image to text foundation models
- First extracts the fact that this image expresses; then it is added as a fact to the text model chain
- Second analyses the image based on whether it has been doctored; look for signs that it is a deepfake

The output gives sources that talk about the same topic, so inherently we have built a *recommender system*. It is able to suggest reading based on vector similarity so the texts found are generally strongly tied not just in meaning but also form to the original source in question.
 
 
## How Truthflow is maintained

The frontend is run on a React server, allowing flexibility while enabling a sophisticated, versatile user interface. On the other hand, Python is used for the backend as the most powerful tool for handling AI applications. It is used to create a REST-API using Django to supply content to the front-end.

## The future of Truthflow
Our aim in the foreseeable future is to make Truthflow a chrome extension which runs with your permission, detecting public content on your social media sites simultaneously as you scroll. Thus, protecting you from unknowingly falling face first into any traps lurking online by alerting you when you come across harmful misinformation.
