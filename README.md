Readme – AI Agent

AI Agent is small project that provides limited access to an AI with tool use. Built as part of a guided project (boot.dev), extended to include persistent log-based memory through context injection. 

Key skills and knowledge developed: 

•	Working with structured API responses (text vs tool calls) 
•	Designing event-based logging systems (JSONL) 
•	Handling agent control flow loops 
•	Injecting external context into model prompts 
•	Debugging structured output edge cases

Key features:

The base project gave the LLM the following functionality on the local system:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

Personal additions made that enhance the base project:

- Implemented JSONL context injection from external logs, that updates the AI agent on recent actions, providing short-term contextual awareness across interactions.

Known limitations:

•	Context injection is limited to recency: current log injection only relies on the last ‘n’ logs. There is also no filtering or ranking system in place to determine which logs are most relevant.
•	Since logs are compressed as raw strings, ‘noise’ may accumulate over time as logs are added
•	Tool calls function, but there is no retry logic or failure handling in place.
•	There’s an external reliance on API calls, subject to availability, server congestion and delays.

Future improvements:

•	Will investigate a way to better filter and summarise the previous logs.
•	Will also consider a better implementation to handle failure events.
