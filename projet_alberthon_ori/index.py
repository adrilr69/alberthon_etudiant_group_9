import vertexai
from vertexai.preview import reasoning_engines

PROJECT_ID = "letudiant-data-prod"
reasoning_engine_id = "7428309353347678208"

vertexai.init(project=PROJECT_ID, location="europe-west1")
reasoning_engine = reasoning_engines.ReasoningEngine(reasoning_engine_id)

response = reasoning_engine.query(config={"thread_id": "1"}, message="Bonjour")

print(response)