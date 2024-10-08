import os
import sys
from groq import Groq
from dotenv import load_dotenv
import re

from agent import Agent
from tools import *

# Load environment variables from .env file
load_dotenv()

prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE(These tree steps should be together unless you get the answer!).
Observation will be the result of running those actions.

Your available actions are:

wikipedia:
e.g. wikipedia: Django
Returns a summary from searching Wikipedia

google:
e.g. google: France
Returns the information of France from searching google

news:
e.g. news: France
Returns the latest of news about the France from NEWSDATA.IO. Use it when trying to get the realtime information!

Always look things up on google if you have the opportunity to do so.

Example session 1:

Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: wikipedia: France
PAUSE

You will be called again with this:

Observation: France is a country. The capital is Paris.

You then output:

Answer: The capital of France is Paris

Example session 2:

Question: What is the capital of China?
Thought: I should look up France on Wikipedia
Action: wikipedia: China
PAUSE

You will be called again with this:

Observation: China, officially the People's Republic of China (PRC), is a country in East Asia. With a population exceeding 1.4 billion, it is the world's second-most

Thought: I didn't get the Capital of China from Wikipedia, I'm trying to find the answer in NEWSDATA.IO
Action: news: China
PAUSE

You will be called again with this:

Observation: Zheng Qinwen summons inner strength to claim China’s first Olympic singles gold medal with victory against Donna Vekić

Thought: I didn't get the Capital of China from NEWSDATA.IO, Let me try it with google
Action: google: China
PAUSE

You will be called again with this:

Observation: officially the People's Republic of China (PRC), is a country in East Asia. With a population exceeding 1.4 billion, it is the world's second-most ...

Thought: I still didn't get the Capital of China, it seems like I got a lot of extra information instead
Action: google: capital of China
PAUSE

You will be called again with this:

Observation: Beijing, previously romanized as Peking, is the capital of China. With more than 22 million residents, Beijing is the world's most populous national capital ...; The modern day capital of China is Beijing (literally "Northern Capital"), which first served as China's capital city in 1261, when the Mongol ruler Kublai ...; Beijing, city, province-level shi (municipality), and capital of the People's Republic of China. Few cities in the world have served for so long as the ...

Thought: Okay, I finally got the capital of China!

Answer: The capital of China is Beijing
""".strip()

action_re = re.compile('^Action: (\w+): (.*)$')

client = Groq(
    api_key=os.getenv('GROQ_API_KEY'),
)

def query(question, max_turns=10):
    i = 0
    bot = Agent(client, prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        print(f"======================================== Iterations {i} =============================================")
        result = bot(next_prompt)
        print(">> Reasoning with the prompt/observation:")
        print(result)
          
        actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        if actions:
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(">> Acting: {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print(">> Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        elif "Answer" in result:
            return 
        else:
            print(f"## Not found the related action and answer for the agent!")
            return 
          
if __name__ == "__main__":
    if len(sys.argv) > 1:
        query(sys.argv[1])