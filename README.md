# langcache
LangCache is a semantic caching library developed for Large Language Model (LLM) queries. Its primary purpose is to address the cost concerns associated with LLM API calls and to improve the speed of LLM applications. 

### Installation of langcache for developer setup
To install langcache, we recommend using the pip package manager.

1. Create a new virtual environment called langcache-venv.
```python -m venv langcache-venv```

2. Now, activate the virtual environment:
```source langcache-venv/bin/activate```

3. Install the dependecies
```pip install .```

### OpenAI ChatGPT 3.5 ChatCompletion API usage with langcache enabled

Before running the example, make sure the `OPENAI_API_KEY` environment variable is set by executing `echo $OPENAI_API_KEY`.
If it is not already set, it can be set by using `export OPENAI_API_KEY=YOUR_API_KEY` on Unix/Linux/MacOS systems or `set OPENAI_API_KEY=YOUR_API_KEY` on Windows systems.

#### OpenAI API original usage
```
import openai

question = "What is ChatGPT?"
completion = client.chat.completions.create(
   model="gpt-3.5-turbo",
   messages=[
     {"role": "system", "content":"You are an helpful assistant to answer all my questions within 15 words limit"},
     {"role": "user", "content": question}
   ]
 )
```
#### OpenAI API + LangCache, similar search cache
```
from langcache.adapter.openai import OpenAI
from langcache.core import Cache

cache = Cache(tune_frequency=5, tune_policy="recall")
client = OpenAI(cache)

question = "What is ChatGPT?"
completion = client.chat.completions.create(
   model="gpt-3.5-turbo",
   messages=[
     {"role": "system", "content":"You are an helpful assistant to answer all my questions within 15 words limit"},
     {"role": "user", "content": question}
   ]
 )
```
