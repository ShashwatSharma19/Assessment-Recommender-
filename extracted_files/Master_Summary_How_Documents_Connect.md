# SHL Assessment Recommender - Master Project Summary
## How PRD + TDD + Roadmap Connect

**Date Created:** May 15, 2026  
**Project Lead:** Shashwat  
**Status:** Documentation Complete → Ready for Claude Code Implementation  

---

## 1. Document Hierarchy

```
┌─────────────────────────────────────────────────────┐
│   1. PRD (Requirements & Success Criteria)          │
│      - What we're building (14 sections)            │
│      - Success metrics (scoring breakdown)          │
│      - All constraints & scope                      │
└────────────────────┬────────────────────────────────┘
                     │
                     │ "What should we test?"
                     ▼
┌─────────────────────────────────────────────────────┐
│   2. TDD Plan (Test Specifications)                 │
│      - Unit tests (5 modules)                       │
│      - Integration tests (3 modules)                │
│      - E2E tests (2 modules)                        │
│      - 120+ specific test cases                     │
└────────────────────┬────────────────────────────────┘
                     │
                     │ "How do we implement?"
                     ▼
┌─────────────────────────────────────────────────────┐
│   3. Roadmap (Implementation Order)                 │
│      - Phase-by-phase breakdown                     │
│      - Code examples & patterns                     │
│      - Quick reference guide                        │
└─────────────────────────────────────────────────────┘
```

---

## 2. The Three Documents Explained

### Document 1: PRD (Product Requirements Document)
**Purpose:** Define WHAT and WHY  
**Read this when:** You need to understand requirements, acceptance criteria, constraints  
**Key sections:**
- Executive summary (1 page)
- Success criteria (Recall@10 target, hard evals, behavior probes)
- Functional requirements (4 core agent behaviors)
- Technical stack (LangChain, Gemini, FAISS+BM25)
- Constraints & limits (8 turns, 30s timeout, <5% hallucination)

**Use PRD to:**
- Understand scoring rubric (60% Recall@10, 20% hard evals, 20% behavior probes)
- Verify all functional requirements are met
- Check constraints are honored (turn cap, URL validation, schema)

---

### Document 2: TDD Plan (Test-Driven Development)
**Purpose:** Define HOW we verify WHAT we build  
**Read this when:** You're writing tests or debugging failures  
**Key sections:**
- Test folder structure (unit / integration / e2e)
- 50+ unit tests (catalog, retrieval, state, validation, prompts)
- 30+ integration tests (flow, behavior probes, edge cases)
- 20+ E2E tests (public traces, Recall@10 measurement)
- Pytest fixtures and CI/CD setup

**Use TDD to:**
- Write tests FIRST (red), then implement code (green)
- Know exactly what each module should do
- Catch bugs early and systematically
- Measure Recall@10 scientifically

---

### Document 3: Roadmap (Implementation Guide)
**Purpose:** Step-by-step implementation with code examples  
**Read this when:** You're writing code or need code patterns  
**Key sections:**
- Architecture diagram (FastAPI → LangChain → Catalog)
- File structure (what goes where)
- 4 implementation phases (Days 1–6)
- Code patterns (catalog scraping, FAISS, BM25, LangChain agent, state machine)
- Commands for testing and deployment

**Use Roadmap to:**
- Know the order to build things (phase 1 → 4)
- See code examples for each component
- Copy-paste templates (prompts, schema, search functions)
- Understand deployment (Docker, Render)

---

## 3. Information Flow (How They Connect)

```
PRD says:
  "Agent must clarify vague queries (Clarify behavior)"
  "Mean Recall@10 must be >0.75"
  "No turn-1 recommend for vague query (behavior probe)"

↓ TDD Plan specifies:
  test_no_turn_1_recommendation_for_vague_query()
  test_mean_recall_at_10() > 0.75
  test_agent_does_not_recommend_on_turn_1()

↓ Roadmap tells you:
  // Implement StateMachine to track state
  if state == GATHERING_CONTEXT:
      agent.clarify()  // Ask questions, no recommendations
  
  // This passes the test:
  ✅ test_no_turn_1_recommendation_for_vague_query passes
  ✅ PRD requirement met
```

---

## 4. How to Use All Three Together

### Scenario 1: Starting a new feature (e.g., "Refine recommendations on edits")

```
Step 1: Check PRD
  → Section 4.2: "REFINE behavior"
  → Says: "User changes constraints mid-conversation → update shortlist"

Step 2: Check TDD
  → test_agent_honors_mid_conversation_edit()
  → Tells you: Assert recommendations change when context updates

Step 3: Check Roadmap
  → Phase 2: test_agent_honors_mid_conversation_edit implementation
  → Shows: How to update state.context + re-rank recommendations

Step 4: Code
  → Implement state.update_context()
  → Run test (RED)
  → Add retrieval call when context changes
  → Run test again (GREEN)
  → Refactor
```

### Scenario 2: Debugging low Recall@10

```
Step 1: Check Roadmap
  → Phase 3: "If Recall@10 low, improve retrieval/prompt"
  → Suggests: Improve FAISS+BM25 ranking, tune prompt

Step 2: Check TDD
  → test_recall_at_10()
  → Shows: Which specific traces have low recall
  → Example output: "Trace 5 (senior Java dev): Recall@10 = 0.6"

Step 3: Debug
  → Trace 5 expects: [Java 8, OPQ32r, SHL Reasoning, ...]
  → Your agent returns: [OPQ32r, Java 8, Leadership, ...]
  → Problem: Not ranking Java assessments high enough

Step 4: Fix
  → Check Roadmap: hybrid_search() function
  → Adjust FAISS weight vs. BM25 weight (increase FAISS for semantic)
  → Re-run test (Recall@10 improves to 0.75)

Step 5: Verify PRD
  → PRD says: "Mean Recall@10 > 0.75"
  → Your test shows: Mean = 0.76 ✓
```

### Scenario 3: Handling edge case (e.g., user asks about non-existent test)

```
Step 1: Check TDD
  → test_unknown_test_name()
  → Says: Agent should gracefully say test not in catalog

Step 2: Check PRD
  → Section 5.2: "Prevent hallucination"
  → Says: "All URLs validated against catalog"

Step 3: Check Roadmap
  → Validation section: is_valid_catalog_url()
  → Shows: Check URL against catalog before returning

Step 4: Code
  → Agent tries to mention "FakeTest"
  → Validation layer catches: Not in catalog
  → Return: "I don't have a test by that name in SHL catalog"

Step 5: Test passes
  → test_unknown_test_name() passes ✓
  → PRD hallucination prevention met ✓
```

---

## 5. Document Reference Matrix

| Question | Answer | Document | Section |
|----------|--------|----------|---------|
| What's the target Recall@10? | >0.75 | PRD | 3.2 |
| How do I test Recall@10? | test_recall_at_10() | TDD | 5.2 |
| How to improve Recall@10? | Tune retrieval | Roadmap | Phase 3 |
| What are the 4 agent behaviors? | Clarify, Recommend, Refine, Compare | PRD | 4.2 |
| How to test each behavior? | test_agent_* probes | TDD | 4.2 |
| How to implement state machine? | StateMachine class | Roadmap | 6.6 |
| What's in scope? | SHL assessments only | PRD | 4.3 |
| How to test off-topic refusal? | test_agent_refuses_off_topic() | TDD | 4.2 |
| How to implement refusal? | Refusal prompt in agent | Roadmap | 6.7 |
| What's the deployment target? | Render | PRD | 9 |
| How to deploy? | Docker + Render steps | Roadmap | Phase 4 |
| What's turn cap? | 8 turns max | PRD | 5.4 |
| How to enforce turn cap? | Turn counter in StateMachine | Roadmap | 6.6 |

---

## 6. Daily Workflow (How to Read Documents)

### Day 1 Morning: Setup & Understanding
1. **Read:** Roadmap "Architecture at a Glance" (5 min)
2. **Read:** PRD "Problem Statement + Success Criteria" (10 min)
3. **Read:** TDD "Testing Philosophy" (5 min)
4. **Task:** Scrape SHL catalog, save to `data/catalog.json`

### Day 1 Afternoon: Unit Tests
1. **Read:** TDD "Unit Tests: Catalog" (10 min)
2. **Read:** Roadmap "Phase 1: Catalog loading" (5 min)
3. **Code:** Write unit tests for catalog (RED phase)
4. **Code:** Implement `app/catalog.py` to pass tests (GREEN phase)

### Day 2: Retrieval & State
1. **Read:** TDD "Unit Tests: Retrieval & State Machine" (15 min)
2. **Read:** Roadmap "6.4 Hybrid Search & 6.6 State Machine" (10 min)
3. **Code:** Tests → Implementation (TDD cycle)

### Day 3: Integration Tests
1. **Read:** TDD "Integration Tests" (15 min)
2. **Read:** PRD "4 Conversational Behaviors" (10 min)
3. **Code:** Implement LangChain agent + FastAPI endpoints

### Day 4: E2E Testing
1. **Read:** TDD "E2E Tests: Public Traces" (10 min)
2. **Task:** Run all 10 public traces, measure Recall@10
3. **Debug:** If Recall@10 low, use Roadmap "Phase 3" guidance

### Day 5: Refinement
1. **Read:** Roadmap "Common Gotchas" (5 min)
2. **Task:** Fix failing probes, improve Recall@10
3. **Verify:** Check against PRD success criteria

### Day 6: Deployment & Submission
1. **Read:** Roadmap "Phase 4: Deployment" (10 min)
2. **Task:** Deploy to Render, test live endpoints
3. **Write:** 2-page approach document
4. **Submit:** API URL + approach doc

---

## 7. Testing Verification Checklist

Use this checklist to verify you've met all requirements:

### PRD Checklist (What)
- [ ] Have you read PRD Section 3 (Success Criteria)?
  - [ ] Hard evals: Schema compliance, catalog-only URLs, turn cap?
  - [ ] Recall@10: Target >0.75?
  - [ ] Behavior probes: Off-topic, no turn-1 vague, edits, hallucination <5%?
- [ ] Have you understood all 4 agent behaviors (Section 4.2)?
  - [ ] Clarify: Ask questions for vague queries?
  - [ ] Recommend: Return 1–10 assessments?
  - [ ] Refine: Update on mid-conversation edits?
  - [ ] Compare: Ground in catalog data?
- [ ] Have you understood scope (Section 4.3)?
  - [ ] Only SHL Individual Test Solutions?
  - [ ] Refuse general HR advice, legal, competitors?

### TDD Checklist (How)
- [ ] Have you written and passed unit tests?
  - [ ] Catalog tests (5 tests)?
  - [ ] Retrieval tests (7 tests)?
  - [ ] State machine tests (8 tests)?
  - [ ] Validation tests (6 tests)?
  - [ ] Prompt tests (4 tests)?
- [ ] Have you written and passed integration tests?
  - [ ] Full conversation flow (1 test)?
  - [ ] Behavior probes (4 tests)?
  - [ ] Edge cases (4 tests)?
- [ ] Have you written and run E2E tests?
  - [ ] All 10 public traces run?
  - [ ] Mean Recall@10 >0.75?

### Roadmap Checklist (Code)
- [ ] Have you followed phase order?
  - [ ] Phase 1: Unit tests + catalog, retrieval, state, validation, prompts?
  - [ ] Phase 2: Integration tests + agent + FastAPI?
  - [ ] Phase 3: E2E testing + tuning?
  - [ ] Phase 4: Deployment + approach doc?
- [ ] Have you implemented all key components?
  - [ ] Catalog loading (catalog.py)?
  - [ ] FAISS + BM25 search (retrieval.py)?
  - [ ] State machine (state.py)?
  - [ ] LangChain agent (agent.py)?
  - [ ] FastAPI endpoints (main.py)?
  - [ ] Validation (validation.py)?
- [ ] Have you deployed?
  - [ ] Docker image?
  - [ ] Render deployment?
  - [ ] Both /health and /chat live?

---

## 8. Key Numbers to Remember

| Number | What | Why |
|--------|------|-----|
| **>0.75** | Mean Recall@10 target | Scoring metric (60% of grade) |
| **8** | Max turns | Hard eval constraint |
| **30s** | Max timeout | Per-call limit |
| **<5%** | Max hallucination rate | Behavior probe |
| **100%** | Schema compliance | Hard eval |
| **1–10** | Recommendations range | Functional requirement |
| **2** | Pages for approach doc | Submission requirement |
| **50+** | Assessments in catalog | Minimum data size |

---

## 9. When to Reference Each Document

| Situation | Go to | Why |
|-----------|-------|-----|
| "I don't understand what we're building" | PRD | Overview of problem, solution, requirements |
| "What should I test?" | TDD | Specific test cases for each component |
| "How do I implement X?" | Roadmap | Code examples and patterns |
| "Did I meet the requirements?" | PRD + Checklist | Verify against success criteria |
| "Why is my Recall@10 low?" | Roadmap + TDD | Debug guidance + test output |
| "Is my code schema-compliant?" | PRD + Roadmap | Schema definition + validation code |
| "What's the evaluation flow?" | PRD 8 | Evaluation approach explained |
| "How long should this take?" | Roadmap | Timeline (6 days) |

---

## 10. Success Criteria Summary (One Page)

### If all these are true, you'll likely score high:

✅ **Hard Evals (MUST PASS)**
- [ ] Every response matches JSON schema exactly
- [ ] All recommendation URLs exist in scraped catalog
- [ ] Conversation never exceeds 8 turns

✅ **Recall@10 (60% of score)**
- [ ] Mean Recall@10 > 0.75 across all traces
- [ ] Validated using test_recall_at_10() function

✅ **Behavior Probes (20% of score)**
- [ ] Agent refuses off-topic questions ✓
- [ ] Agent doesn't recommend on turn 1 for vague queries ✓
- [ ] Agent honors mid-conversation edits ✓
- [ ] Hallucination rate <5% ✓

✅ **Code Quality**
- [ ] Modular, well-commented code ✓
- [ ] All unit + integration + E2E tests pass ✓
- [ ] Follows TDD approach (tests first) ✓

✅ **Deployment**
- [ ] Live on Render (/health + /chat endpoints) ✓
- [ ] <30s per call ✓
- [ ] <2 min cold start ✓

✅ **Documentation**
- [ ] 2-page approach document ✓
- [ ] Explains design choices defensibly ✓

---

## 11. Common Questions

**Q: Which document should I read first?**  
A: Roadmap (quick overview), then PRD (requirements), then TDD (tests).

**Q: Do I need to read all three in full?**  
A: No. Use the reference matrix (Section 5) to jump to relevant sections.

**Q: What if PRD and Roadmap disagree?**  
A: PRD is source of truth (requirements). Roadmap is guidance (implementation).

**Q: Can I skip the TDD phase?**  
A: No. TDD is essential for passing behavior probes and Recall@10 measurement.

**Q: How do I measure Recall@10?**  
A: Use test_recall_at_10() in TDD plan (Section 5.2).

**Q: What if I can't hit >0.75 Recall@10?**  
A: Improve retrieval (hybrid search tuning) or prompts (better system prompt). Roadmap Phase 3 has debugging guidance.

---

## 12. File Sizes & Read Times

| Document | Sections | Read Time | Use Case |
|----------|----------|-----------|----------|
| PRD | 15 | 20–30 min | Understanding requirements |
| TDD | 12 | 30–45 min | Writing tests |
| Roadmap | 13 | 20–30 min | Implementation code |
| This Summary | 12 | 10–15 min | Getting oriented |

**Total read time: ~60–90 minutes (one afternoon)**

---

## 13. Next Steps (Start Here!)

1. **Read this summary** (you're doing it now) ✓
2. **Read Roadmap "Quick Reference"** (5 min)
3. **Read PRD "Success Criteria"** (10 min)
4. **Run Phase 1 of Roadmap:** Scrape catalog + write unit tests
5. **Watch tests go RED** → Write implementation → Watch go GREEN
6. **Repeat for phases 2–4**

---

## 14. Sign-Off

**Documentation Status:** Complete  
**Ready for:** Claude Code Implementation  
**Estimated Duration:** 6 days (Days 1–6 in timeline)  
**Target Submission:** Date TBD (within 6 days)  

All three documents (PRD, TDD, Roadmap) are:
- ✅ Complete
- ✅ Internally consistent
- ✅ Ready for Claude Code to implement
- ✅ Designed for TDD (tests first)

---

**Start coding now. Good luck! 🚀**

For any questions, refer to:
1. This summary (quick overview)
2. Relevant PRD section (requirements)
3. Relevant TDD section (tests)
4. Relevant Roadmap section (implementation)
