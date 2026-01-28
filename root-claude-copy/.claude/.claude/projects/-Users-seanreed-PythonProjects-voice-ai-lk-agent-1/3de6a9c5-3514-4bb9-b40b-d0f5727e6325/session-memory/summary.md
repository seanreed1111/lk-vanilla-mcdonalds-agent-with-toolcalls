
# Session Title
_A short and distinctive 5-10 word descriptive title for the session. Super info dense, no filler_

McDonald's Drive-Thru Voice Agent Planning with Accuracy Focus

# Current State
_What is actively being worked on right now? Pending tasks not yet completed. Immediate next steps._

All 5 tasks completed. Comprehensive implementation plan created and saved.

Completed:
- All core architecture files examined: session_handler.py, app.py, config.py, factories.py (DI pattern with Pydantic v2 config)
- All LLM wrappers examined: keyword_intercept_llm.py (KeywordInterceptLLM wrapper), mock_llm.py (SimpleMockLLM)
- menus/mcdonalds/models.py (Menu/Item/Modifier Pydantic v2 structure with JSON serialization)
- All test files examined: test_agent.py (LLM-as-judge pattern), test_keyword_intercept.py (exact assertion pattern)
- Menu data fully analyzed: 9 categories, 212 total items, 949 lines of JSON
- Menu content sampled: Breakfast, Beef & Pork, Chicken & Fish categories with variations
- plan/ directory created at /Users/seanreed/PythonProjects/voice-ai/lk-agent-1/plan
- 10 accuracy-boosting strategies designed and documented
- Comprehensive implementation plan written to `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/plan/mcdonalds-drive-thru-agent-plan.md`

No implementation performed - planning phase only as requested.

# Task specification
_What did the user ask to build? Any design decisions or other explanatory context_

Create a plan (not implementation) for a custom LLM-powered McDonald's drive-thru order taker agent.

Requirements:
- Customer can order anything from the menu at `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/menus/mcdonalds/transformed-data`
- After each customer turn, append the ordered item to a file
- When customer says they're done, LLM should:
  - Acknowledge
  - Read back all item names ordered
  - Create final output JSON file with timestamp showing full order
- **Accuracy is key** - plan must explore various experimental approaches to boost LLM accuracy for retrieving correct menu items with modifiers from available items
- Save plan as markdown in `plan/` directory
- DO NOT implement, only plan

# Files and Functions
_What are the important files? In short, what do they contain and why are they relevant?_

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/menus/mcdonalds/models.py` - Pydantic v2 models:
  - `Modifier`: modifier_name, modifier_id (UUID), hashable/comparable
  - `Item`: category_name, item_name, available_as_base, modifiers list, add_modifier(), to_json(), from_json()
  - `Menu`: categories dict, add_item(), get_category(), get_item(), get_all_categories(), load_from_file(), save_to_file()

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json`:
  - 9 categories, 212 items, 949 lines total
  - Categories: Breakfast, Beef & Pork, Chicken & Fish, Salads, Snacks & Sides, Desserts, Beverages, Coffee & Tea, Smoothies & Shakes
  - Key items: Big Mac, Quarter Pounder (variations: Cheese, Bacon & Cheese, Bacon Habanero Ranch), McNuggets (4/10/20/40 piece), Big Breakfast (variations: Egg Whites, Hotcakes)

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/plan/mcdonalds-drive-thru-agent-plan.md` - Complete implementation plan:
  - Architecture: DriveThruLLM wrapper, MenuProvider, OrderStateManager, validation layer
  - 10 accuracy strategies categorized by priority (MVP: function calling, menu context injection, fuzzy matching, validation; Advanced: confirmation loop, semantic search, two-stage parsing, chain-of-thought, constrained decoding, context optimization)
  - Order flow: incremental JSONL logging per turn, final JSON with timestamp on completion
  - 5 implementation phases with time estimates
  - Testing framework using LiveKit judge-based evaluation
  - Success criteria: ≥95% item accuracy, ≥90% modifier accuracy, <2s latency
  - File structure, config additions, risk mitigations, experimentation framework

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/src/session_handler.py`:
  - SessionHandler.__init__(stt, llm, tts, agent, session_config) - all injected
  - handle_session() sets up AgentSession with MultilingualModel turn detection, VAD, preemptive_generation, optional BVC noise cancellation
  - Greets with "Hello! How can I help you today?"

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/src/app.py`:
  - `Assistant(Agent)`: default helpful voice AI persona
  - `VoiceAgentApp`: creates components via factories, wires SessionHandler with DI, sets up AgentServer
  - _prewarm() loads silero.VAD into proc.userdata["vad"]

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/src/config.py`:
  - Pydantic v2: AgentConfig (instructions), PipelineConfig (stt/llm/tts models, keyword intercept settings), SessionConfig (turn detector, preemptive gen, noise cancellation), AppConfig (env-based with .env.local)

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/src/factories.py`:
  - create_stt/llm/tts from config
  - LLM factory: "mock" → SimpleMockLLM, else inference.LLM; wraps with KeywordInterceptLLM if enabled

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/tests/test_agent.py`:
  - LLM-as-judge pattern: _llm() creates inference.LLM("openai/gpt-4.1-mini") for judging
  - Tests: offers_assistance (greeting), grounding (refuses unknown info), refuses_harmful_request
  - Pattern: AgentSession(llm=judge_llm), session.start(agent), session.run(user_input), result.expect.next_event().is_message().judge(llm, intent="...")

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/src/keyword_intercept_llm.py`:
  - `KeywordInterceptLLM(LLM)`: wraps base LLM, intercepts keywords in user messages
  - _get_latest_user_message() extracts from ChatContext, _contains_keyword() does case-insensitive matching
  - chat() returns KeywordInterceptStream (0.05s TTFT, fixed response) if keyword detected, else delegates to wrapped_llm
  - Default: keywords=["cherries", "cherry", "banana", "apple", "fruit"], response="I don't like fruit"

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/src/mock_llm.py`:
  - `SimpleMockLLM`: returns fixed response "You knew the job was dangerous when you took it, Fred." with configurable ttft (0.1s), chunk_size (5)
  - SimpleMockLLMStream streams response in chunks

- `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/tests/test_keyword_intercept.py`:
  - Exact assertion pattern: event._event.item.text_content for accessing response, assert actual_content == "expected"
  - Tests all default keywords, case-insensitive matching, delegation to wrapped LLM, custom keywords
  - Shows two testing patterns: (1) LLM-as-judge for behavior, (2) Exact assertions for deterministic responses

# Workflow
_What bash commands are usually run and in what order? How to interpret their output if not obvious?_

# Errors & Corrections
_Errors encountered and how they were fixed. What did the user correct? What approaches failed and should not be tried again?_

# Codebase and System Documentation
_What are the important system components? How do they work/fit together?_

**Architecture Pattern: Dependency Injection with Config + Factories**

Flow: Configuration → Construction → Wiring → Runtime
1. **Configuration** (`src/config.py`): Pydantic v2 models define all settings (AgentConfig, PipelineConfig, SessionConfig, AppConfig with env support)
2. **Construction** (`src/factories.py`): Factory functions create concrete livekit.agents.inference components (STT, LLM, TTS) from config. LLM factory supports "mock" case and optional KeywordInterceptLLM wrapper
3. **Wiring** (`src/app.py`): VoiceAgentApp.__init__() instantiates config, calls factories, creates Assistant agent, creates SessionHandler with DI (stt, llm, tts, agent, session_config), sets up AgentServer with _prewarm and rtc_session handler
4. **Runtime** (`src/session_handler.py`): SessionHandler.handle_session() creates AgentSession with injected components, configures turn detection/vad/noise cancellation, starts session, connects to room, says greeting

**Key patterns:**
- No Protocol/adapter/mock layer - uses concrete LiveKit inference components directly
- Wrapper pattern for LLM extensions (KeywordInterceptLLM wraps base LLM)
- VAD prewarming via JobProcess.userdata in server setup_fnc
- Multilingual turn detection conditional on config flag

**Testing framework:**
- Uses LiveKit Agents evaluation framework (not pytest mocks/fixtures)
- Pattern: AgentSession(llm=judge_llm), session.start(agent), session.run(user_input=...), result.expect.next_event().is_message().judge(llm, intent=...)
- LLM-as-judge approach for behavior validation (friendliness, grounding, refusals)
- Tests focus on agent behavior, not component mocking

# Learnings
_What has worked well? What has not? What to avoid? Do not duplicate items from other sections_

# Key results
_If the user asked a specific output such as an answer to a question, a table, or other document, repeat the exact result here_

Comprehensive implementation plan created at `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/plan/mcdonalds-drive-thru-agent-plan.md`

**Plan Structure:**
- Executive summary and system architecture (DriveThruLLM wrapper, MenuProvider, OrderStateManager, validation layer)
- 10 accuracy-boosting strategies with pros/cons/impact ratings (Priority 1 MVP: function calling, menu context injection, fuzzy matching, post-processing validation; Priority 2: confirmation loop, semantic search; Priority 3: two-stage parsing, chain-of-thought, constrained decoding, context optimization)
- Recommended strategy combination for 3 phases
- Order state management (OrderItem/OrderSession models, incremental JSONL logging per turn, final JSON with timestamp)
- Agent instructions and conversation flow examples
- Testing strategy with 5 categories and accuracy metrics (target: ≥95% item accuracy, ≥90% modifier accuracy)
- 5 implementation phases with time estimates (Phase 1: Core Infrastructure 2-3 days, Phase 2: MVP Accuracy Strategies 3-4 days, Phase 3: Agent Integration 2 days, Phase 4: Testing & Refinement 2-3 days, Phase 5: Advanced Strategies optional 2-3 days)
- File structure, configuration additions (DriveThruConfig), risks & mitigations
- Success criteria, future enhancements, key design decisions
- Experimentation framework for A/B testing strategies, monitoring & observability

# Worklog
_Step by step, what was attempted, done? Very terse summary for each step_

1. User requested plan for McDonald's drive-thru order taker agent with accuracy focus
2. Created 5-item todo list: (1) research architecture, (2) examine menu models, (3) research testing framework, (4) design accuracy strategies, (5) create plan
3. Started parallel reads: attempted src/agent.py (doesn't exist), read session_handler.py successfully, read models.py successfully
4. Read `src/session_handler.py` - understood SessionHandler with DI pattern (stt, llm, tts, agent, config injected), AgentSession setup with multilingual turn detection
5. Read `menus/mcdonalds/models.py` - understood 3-class structure (Menu, Item, Modifier), JSON serialization, load_from_file() method
6. Globbed `src/*.py` - discovered actual files: app.py, config.py, factories.py, keyword_intercept_llm.py, mock_llm.py (agent.py doesn't exist)
7. Read first 50 lines of `menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json` - saw Breakfast category structure with items and variations
8. Globbed `tests/*.py` - found test_agent.py, test_keyword_intercept.py, test_menu_models.py
9. Read `src/app.py` - understood Assistant agent class and VoiceAgentApp with DI wiring, VAD prewarming, server setup
10. Read `src/config.py` - understood Pydantic v2 config structure (AgentConfig, PipelineConfig, SessionConfig, AppConfig with env support)
11. Read `src/factories.py` - understood factory pattern for creating STT/LLM/TTS, LLM wrapper pattern for KeywordInterceptLLM
12. Read `tests/test_agent.py` - understood LiveKit Agents evaluation framework with LLM-as-judge pattern (session.run, result.expect, judge)
13. Marked task 1 complete, moved to task 2 (examine menu models)
14. Ran `wc -l` on menu JSON - 949 lines total
15. Ran Python analysis of menu structure - discovered 9 categories, 212 total items, extracted all category names: Breakfast, Beef & Pork, Chicken & Fish, Salads, Snacks & Sides, Desserts, Beverages, Coffee & Tea, Smoothies & Shakes
16. Read lines 100-199 of menu JSON - examined Beef & Pork category (14 items including Big Mac, Quarter Pounder variants with modifiers like "Bacon & Cheese", "Bacon Habanero Ranch") and start of Chicken & Fish category (McNuggets 4/10/20/40 piece, various McChicken variants)
17. Read `src/keyword_intercept_llm.py` - understood KeywordInterceptLLM wrapper pattern: intercepts keywords in user messages, returns fixed response or delegates to wrapped LLM, KeywordInterceptStream simulates streaming with 0.05s TTFT
18. Read `src/mock_llm.py` - understood SimpleMockLLM for testing: returns fixed response "You knew the job was dangerous when you took it, Fred." with configurable TTFT (0.1s) and chunk_size (5 chars), SimpleMockLLMStream streams response in chunks
19. Marked task 2 complete (menu models examined)
20. Read `tests/test_keyword_intercept.py` - understood exact assertion testing pattern: event._event.item.text_content for accessing actual response text, assert actual_content == "expected string" for deterministic validation (vs LLM-as-judge in test_agent.py)
21. Marked task 3 complete (testing framework researched), marked task 4 as in_progress (designing accuracy strategies)
22. Created `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/plan` directory with mkdir -p
23. Marked task 4 complete (accuracy strategies designed), moved to task 5 (create plan markdown)
24. Wrote comprehensive implementation plan to `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/plan/mcdonalds-drive-thru-agent-plan.md` covering: system architecture, 10 accuracy strategies with pros/cons/impact ratings, order state management, agent instructions, testing strategy, 5 implementation phases, file structure, config, risks, success criteria, experimentation framework
25. Marked task 5 complete - all 5 tasks completed successfully
