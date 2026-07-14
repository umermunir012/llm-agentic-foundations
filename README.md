**llm customization  agentic ai foundations**

this repository contains a local cpuonly implementation of prompt engineering retrievalaugmented generation rag model evaluation and a toolusing ai agent it is built entirely on ollama requiring no api keys no cloud dependencies and zero cost 

the system queries a corpus of aviation safety documents including ntsb accident reports asrs incident reports and faa wildlife strike guidance

** requirements**

 python 311 python 314 works but see limitations below
 ollama installed locally
 internet access only required for the live weather tool api

 **setup  installation**

**1 install ollama and pull the necessary models**
bash
ollama pull llama323b
ollama pull llama321b

**2 install python dependencies**
bash
pip install r requirementstxt

**3 ingest the documents and build the index run this before any other scripts**
bash
python 02ragprototypeingestpy

 note ingestpy chunks the 5 aviation documents and builds the initial search index if you skip this the other scripts will have nothing to search

** running the code**

expect 1020 seconds per query on a cpuonly setup and a few minutes for the full evaluation

**1 rag queries**
bash
python 02ragprototypequerypy what caused the colgan air crash

**2 agentic queries**
bash
 tests rag and calculator tools in sequence
python 04agenticagentpy how many wildlife strikes happen per year and what is that per day

tests live api tool
python 04agenticagentpy what is the current weather at the airport where asiana 214 crashed

**3 evaluations**
bash
python 01promptengineeringevaluatepromptspy
python 03evaluationevalpy

 outputs from recent runs are saved in resultsmd metricsmd and tracesmd see 04agentictracesmd for full agent execution traces

 architecture  insights

 the agent
the agent runs on a handrolled react loop 150 lines rather than a framework like langchain this provides full visibility into the agentic loop and handles parsefailures directly when small models emit malformed action lines 

**tools provided**
1 rag lookup over the aviation documents
2 calculator
3 live metar weather api

 **prompt engineering evaluation**
tested on llama 32 3b rolebased prompting performed best while chainofthought cot doubled latency and token counts for negligible gain

 ** strategy  relevance  latency  tokens **
        
 zeroshot  023  1071s  165 
 fewshot  049  901s  269 
 chainofthought  050  2223s  361 
 rolebased  056  2193s  363 

** model performance comparison**
the 1b model is the most sensible choice for this specific corpus upgrading to 3b yields only a 005 relevance increase while increasing latency by 40 the 1b model utilizes slightly more tokens as it tends to be more verbose

** model  hit rate  relevance  latency  tokens **
          
 llama323b  100  058  135s  479 
 llama321b  100  053  95s  492 

 **configuration**

all tunable parameters are managed via configpy or a env file

** variable  default  purpose **
      
 llmmodel  llama323b  main model used for queriesagent 
 llmmodelalt  llama321b  comparison model for evaluation 
 ollamabaseurl  httplocalhost11434  ollama server address 
 chunksize  512  characters per document chunk 
 chunkoverlap  64  character overlap between chunks 

** known limitations  future work**

 tfidf vs vector db retrieval is currently performed using tfidf keyword matching instead of a vector db this was implemented to avoid dependency conflicts as chromadb lacks python 314 wheels
 artificially high hit rate because the current test questions share obvious keywords with the source documents tfidf achieves a perfect 100 hit rate paraphrased questions would likely fail under this setup
 next steps the upcoming phase will focus on embedding optimization this requires migrating to a python 312 virtual environment swapping tfidf for chromadb and implementing the allminilml6v2 embedding model to capture semantic meaning rather than just keywords it will also involve finetuning the chunksize and chunkoverlap values
