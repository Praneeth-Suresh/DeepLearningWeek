import json

# Get the Embedding model

from sentence_transformers import SentenceTransformer, util
import re

# Get the Chroma DB client set up
import chromadb
import os

data_path = os.getcwd()
client = chromadb.PersistentClient(path=data_path)

# Get the Google LLM client set up
from google import genai
from pydantic import BaseModel
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

Gclient = genai.Client(api_key=GEMINI_API_KEY)

# Get the cloudfare API set up

import requests

CLOUDFARE_API_TOKEN = os.environ["CLOUDFARE_API_TOKEN"]

API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/7334438e0dd62f7a7d9989ba0b0b6ee5/ai/run/"
headers = {"Authorization": f"Bearer {CLOUDFARE_API_TOKEN}"}

def run(model, inputs):
    input = { "messages": inputs }
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response.json()


def Validation(text): # Takes in the text and deduces if the post is valid; return FactAnalysis dictionary
    # Extract that facts that are in there; only if there are facts we proceed

    inputs = [
        { "role": "system", "content": "Your job is to separate out the factual statements from the inputted social media prompt. If there are no factual statement just print out 'False'. If there are facts, just lists the factual statements, one on each line, with no extra text. Refrain from using pronouns in your reponse. Repeat the proper noun." },
        { "role": "user", "content": text}
    ]
    output = run("@cf/meta/llama-3-8b-instruct", inputs)

    print(output['result']['response'])

    if output['result']['response'] == 'False':
        print("Opinioned statement")
        return None
    else:
        facts = output['result']['response'].splitlines()

        if "facts" in facts[0]:
            facts.pop(0)

        if facts[0] == "":
            facts.pop(0)

    # Use the Google API using Google Search to deduce the validity 

    Fact_Analysis = [] # Parallel to fact; Store in the following format: Correct. Its backed up by the following: <br></br><a href=uri target="_blank">title</a>
    FactValidity = [] # Parallel to fact

    for fact in facts:
        google_search_tool = Tool(
            google_search = GoogleSearch()
        )


        prompt = f"""Can you verify the following statement:
        {fact}
        """

        response = Gclient.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            )
        )

        srcs = response.candidates[0].grounding_metadata.grounding_chunks

        sources = "" # Contains <br></br><a href=uri target="_blank">title</a>

        for i in range(len(srcs)):
            sources += f"<br><a href='{srcs[i].web.uri}' target='_blank'>{srcs[i].web.title}</a>"

        if "true" in response.text.lower() or "correct" in response.text.lower():
            valid = True
            starter = "Correct. Its backed up by the following: "
        else:
            valid = False
            starter = "Incorrect. Its refuted by the following"

        FactValidity.append(valid)
        Fact_Analysis.append(starter + sources)

    # Here we identify where to insert the highights

    class Overall(BaseModel):
        segments: list[str]
        fact: list[int]

    facts_cont = ' \n'.join(facts)

    prompt = f"""Below is a social media post:
    {text}

    Here are the facts that are contained in the social media post:
    {facts_cont}

    Identify which regions of the social media post talk about which fact.
    Output the entire post, as it is, but broken up into distinct facts and phrases that are not facts. Starting from the beginning of the post, identify contiguous segments of text corresponding to an opinion or one of the facts above. If the segment expresses an opinion, store -1 in the associated integer list. Else store the index of the fact in the list.
    """

    response = Gclient.models.generate_content(
        model="gemini-2.0-pro-exp-02-05",
        contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': list[Overall],
            },
    )

    print(response.text)

    breakup: list[Overall] = response.parsed

    json_results = []

    for i in range(len(breakup)):

        fact_index = breakup[i].fact[0]
        if fact_index < 0: fact = False
        else: fact = True

        json_results.append({
            "text": breakup[i].segments[0],
            "isFactual": FactValidity[fact_index],
            "fact": fact,
            "explanation": Fact_Analysis[fact_index]
        })

    def dict_to_json(dictionary):
        # Custom encoder to remove quotes from keys
        class CustomEncoder(json.JSONEncoder):
            def encode(self, obj):
                if isinstance(obj, dict):
                    return '{' + ', '.join(f"{k}: {self.encode(v)}" for k, v in obj.items()) + '}'
                elif isinstance(obj, str):
                    return f'"{obj}"'
                elif isinstance(obj, list):
                    return '[' + ', '.join(self.encode(item) for item in obj) + ']'
                return json.JSONEncoder.encode(self, obj)
        
        return json.dumps(dictionary, cls=CustomEncoder)
            
    for j in range(len(json_results)):
        json_results[j] = dict_to_json(json_results[j])
        
    return json_results

def VectorSimilarity(paragraph1, paragraph2): # Get the cosine similarity score
    model = SentenceTransformer("all-MiniLM-L6-v2")  # Mid-range embedding model
    
    # Generate embeddings
    embedding1 = model.encode(paragraph1, convert_to_tensor=True)
    embedding2 = model.encode(paragraph2, convert_to_tensor=True)
    
    # Compute cosine similarity
    similarity_score = util.pytorch_cos_sim(embedding1, embedding2).item()
    
    return similarity_score

def CrossRefScore(texts):
    
    n = len(texts)
    if n == 0:
        return []
    
    scores = [0] * n  # Store cumulative scores for each entity
    
    # Compare each pair (i, j) only once
    for i in range(n):
        for j in range(i + 1, n):
            similarity = VectorSimilarity(texts[i], texts[j])  # Get similarity score
            scores[i] += similarity
            scores[j] += similarity  # Since similarity(i, j) == similarity(j, i)
    
    # Compute average similarity for each entity
    averages = [scores[i] / (n - 1) if n > 1 else 0 for i in range(n)]
    
    return averages   

def EggScore(text):

    # Predefined exaggerative words (can be expanded)
    EXAGGERATION_WORDS = {
        "unbelievable", "incredible", "shocking", "mind-blowing", "jaw-dropping",
        "extremely", "absolutely", "utterly", "completely", "insanely",
        "life-changing", "spectacular", "massive", "remarkable", "unprecedented",
        "best", "worst", "amazing", "astounding", "unreal", "gigantic", "enormous"
    }

    if not text:
        return 0.0  # Return 0 for empty texts

    # Tokenize and normalize text (convert to lowercase and remove punctuation)
    words = re.findall(r"\b\w+\b", text.lower())

    # Count total words and occurrences of exaggerative words
    total_words = len(words)
    exaggeration_count = sum(1 for word in words if word in EXAGGERATION_WORDS)

    # Compute exaggeration score as proportion of exaggerative words
    return exaggeration_count / total_words if total_words > 0 else 0.0