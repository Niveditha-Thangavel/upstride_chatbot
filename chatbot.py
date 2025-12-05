from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
import os, json

os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here" 
os.environ["SERPERAPI_KEY"] = "#"
search_tool = SerperDevTool()

llm = LLM(
    model = "gemini/gemini-2.5-flash",
    api_key = "#"
)

def load_memory():
    if not os.path.exists("msg.json"):
        return []
    try:
        with open("msg.json", "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = [data]
        return data
    except json.JSONDecodeError:
        return []

def create_agent(memory):
    chat_agent = Agent(
        role = "ChatBot",
        goal = "Make an interactive chat session with the user",
        backstory = "You are a chatbot that makes use of search tool to search for content to chat with user and {memory} as previours prompts as memorys",
        tool = [search_tool],
        llm = llm,
        verbose = False,
        allow_delegation = False
    )
    return chat_agent

memory = load_memory()

def create_task(msg):
    chat_agent = create_agent(memory)
    description = f"""The user provides the message: {msg}
                        Respond to the prompt accordingly.
                        If something must be looked up, use the search tool.
                        Make sure to provide accurate results in case of questions.
                        Use {memory} to fetch previous prompts"""

    task = Task(
        description=description,
        expected_output="A friendly chatbot style message",
        agent=chat_agent
    )

    crew = Crew(
        agents = [chat_agent],
        tasks = [task],
        verbose = False
    )

    return crew.kickoff()

print("Hi! Welcome to the chatbot! How can I help you?\n (enter bye to exit)")


while True:
    msg = input()
    if msg.lower().strip()=="bye":
        print("Thank you! Bye!😊")
        break

    result = create_task(msg)
    
    if hasattr(result, "final_output"):
        clean = result.final_output
    elif isinstance(result,dict) and "final_output" in result:
        clean = result["final_output"]
    else:
        clean = str(result)
    
    print(clean)

    with open("msg.json", "r") as f:
        try:
            data = json.load(f)

            if not isinstance(data,list):
                data = [data]
        except json.JSONDecodeError:
            data = []

    data.append(msg)

    with open("msg.json", "w") as f:
        json.dump(data, f, indent=4)