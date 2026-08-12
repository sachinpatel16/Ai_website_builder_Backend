import os
import dspy  # type: ignore
from dotenv import load_dotenv # type: ignore
from langchain_ollama import ChatOllama


load_dotenv()

# LangChain LLM for business gathering node (supports .ainvoke)


# DSPy LM for planning/update modules
# llm = dspy.LM(
#     # model="ollama_chat/deepseek-v3.1:671b-cloud",
#     # model="ollama_chat/kimi-k2.5:cloud",
#     model="ollama_chat/gpt-oss:120b-cloud",
#     api_base="http://localhost:11434",
#     # api_key="697e15001d72400ca9368a233a74e6eb.CT6FTd5rHltSc8wtEtIJd-UE"
# )
# planning_llm = llm
# update_llm = llm

# OpenRouter DSPy LM Configuration (Auto Mode)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")

llm = dspy.LM(
    model=OPENROUTER_MODEL,
    api_key=OPENROUTER_API_KEY,
    api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
    max_tokens=16000,
    cache=True,
)
planning_llm = llm
update_llm = llm



# API_KEY = os.getenv("API_KEY")
# print(API_KEY)
# LLM_MODEL = os.getenv("LLM_MODEL")
# print(LLM_MODEL)


# llm = dspy.LM(
#     model=f"{LLM_MODEL}",
#     api_key=API_KEY,
#     temperature=0.6,
#     max_tokens=13000,
#     cache=True,
# )

# # Separate LLM for planning phase - lower token limit for efficiency
# PLANNING_API_KEY = os.getenv("PLANNING_API_KEY")
# PLANNING_MODEL = os.getenv("PLANNING_MODEL")
# planning_llm = dspy.LM(
#     model=f"{PLANNING_MODEL}",
#     api_key=PLANNING_API_KEY,
#     temperature=0.6,
#     max_tokens=2000,  # Planning outputs are much smaller (JSON only)
#     cache=True,
# )

# # Separate LLM for update/edit operations - moderate token limit for efficiency
# UPDATE_API_KEY = os.getenv("UPDATE_API_KEY")
# UPDATE_MODEL = os.getenv("UPDATE_MODEL")
# update_llm = dspy.LM(
#     model=f"{UPDATE_MODEL}",
#     api_key=UPDATE_API_KEY,
#     temperature=0.6,
#     max_tokens=8000,  # Planning outputs are much smaller (JSON only)
#     cache=True,
# )

# Use Azure model for full generation 

# API_KEY = os.getenv("AZURE_AI_TOKEN")
# print(API_KEY)
# API_BASE = os.getenv("AZURE_AI_ENDPOINT_URL")
# print(API_BASE)
# LLM_MODEL = os.getenv("AZURE_AI_DEPLOYMENT_NAME")
# print(LLM_MODEL)

# API_VERSION = os.getenv("AZURE_AI_APP_VERSION")
# print(API_VERSION)

# llm = dspy.LM(
#     f'azure/{LLM_MODEL}',
#     api_key=API_KEY,
#     api_base=API_BASE,
#     api_version=API_VERSION,
#     temperature=1.0,
#     max_tokens=16000,
#     cache=True
# )

# planning_llm = llm
# update_llm = llm


# llm = dspy.LM(
#     # model="openai/mistralai/Mixtral-8x7B-Instruct-v0.1:novita",
#     model="openai/Qwen/Qwen2.5-72B-Instruct:novita",
#     # model="openai/meta-llama/Llama-3.3-70B-Instruct:novita",
#     api_base="https://router.huggingface.co/v1",
#     api_key=os.getenv("HUGGINGFACE_API_KEY"),
#     temperature=0.7,
#     max_tokens=7500,
#     cache=True,
# )
# planning_llm = dspy.LM(
#     f'azure/{LLM_MODEL}',
#     api_key=API_KEY,
#     api_base=API_BASE,
#     api_version=API_VERSION,
#     temperature=1.0,
#     max_tokens=16000,
#     cache=True
# )
# update_llm = dspy.LM(
#     f'azure/{LLM_MODEL}',
#     api_key=API_KEY,
#     api_base=API_BASE,
#     api_version=API_VERSION,
#     temperature=1.0,
#     max_tokens=16000,
#     cache=True
# )

dspy.settings.configure(lm=llm)
