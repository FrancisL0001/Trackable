# AGENT.md

## __Introduction__ (Mandatory)

This file defines mandatory instructions for any AI agent operating in this repository. You must read this file fully before performing any task. All instructions here are authoritative and override default agent behavior. If any instruction conflicts with your defaults or assumptions, this file takes precedence.

If requirements, scope, or constraints are unclear, stop and ask for clarification before acting.

⸻

## 1. __Global Rules (Apply to All Tasks)__  
•	Be critical and precise. Do not agree by default; challenge incorrect assumptions and flawed reasoning.   
	•	Prefer correctness, clarity, and evidence over speed or convenience.   
	•	Make minimal, scoped changes. Do not refactor, reformat, or reorganize unrelated code without explicit permission.  
	•	No silent decisions: explain non-trivial choices, tradeoffs, and rejected alternatives.  
	•	No silent dependency additions: always announce new dependencies, justify why they are needed, and wait for approval before adding them.  
	•	Never delete files, rename public APIs, or change externally visible behavior without confirmation.  
	•	If requirements, data, or expected behavior are ambiguous, stop and ask before guessing.  

___Git Rules (Strict)___  
	•	__NEVER__ use ```git add -A ``` or equivalent blanket staging commands.  
	•	Only stage and commit files you have directly created or modified.  
	•	Double-check staged files before committing.  
	•	Write clear, descriptive commit messages explaining why the change exists.  

___Other Rules___
	•	Do not use or reference any code, data, or resources not explicitly provided in this repository or approved by the project owner.  
	•	Do not make assumptions about the environment, dependencies, or available resources beyond what is explicitly stated.  
	•	Always follow the principle of least surprise: do not introduce unexpected behavior, side effects, or dependencies.
	• 	Never read anything from .env files or similar without explicit instructions to do so.

⸻

## 2. Project Structure & Architecture Rules
• Simple, single-purpose projects:  
	•	Prefer a single entry point at the repository root (e.g., main.py, index.ts).  
	•	Avoid premature modularization.  
	•	Complex or multi-component projects:  
	•	Each independent component, service, or module should have its own directory and clear entry point (main, index, or equivalent).  
	•	Shared utilities should live in a clearly named common module.  
	•	Follow a model–view / model–service–API separation where applicable:  
	•	Models and core logic must not depend on UI, framework, or transport layers.  
	•	Side effects (I/O, network, persistence) should be isolated.  
	•	Core logic must be testable independently of delivery layers.  
	•	Tests should live in a clearly defined directory (e.g., tests/) and mirror the structure of the code they test.  

⸻

## 3. Documentation & Project Intent

___README.md___ (User-Facing, Always Up to Date).  
	-    __The README.md must be updated continuously as the project evolves.  Keep it__:  
	•	concise.  
	•	straight to the point.  
	•	user-targeted.  
	•	quick to read and understand.   
	-   __The README should explain__:  
	•	what the project does.  
	•	how to run it.  
	•	how to use it.  
	•	where to find deeper or internal documentation.  
	•	Avoid excessive verbosity. The goal is clarity without boredom.   

___PROJECT_DESCRIPTION.md___ (Internal Source of Truth)
	•	Maintain a PROJECT_DESCRIPTION.md file.
	•	This file contains:
	•	full project vision and intent
	•	motivation and goals
	•	assumptions and constraints
	•	non-obvious design decisions
	•	It may be as detailed and verbose as needed.
	•	It is used by the agent to stay aligned during development.
	•	Do NOT modify this file unless explicitly authorized to change project scope, intent, or features.

⸻

## 4. Testing Philosophy

___General Rules___   
	•	Every programming task or project must start with a written testing plan. The testing plan should identify:
	•	key behaviors and invariants
	•	edge cases and failure modes
	•	inputs that must never break the system
	•	Implementation may proceed only after the testing plan is outlined.
	•	A feature or fix is not considered done until relevant tests exist and pass.

___Testing.md___   
	•	Maintain a testing.md file at the project root.  
	•	___This file___:  
	•	contains the testing plan and evolving test strategy.  
	•	is independent of code structure and implementation details.  
	•	serves as a long-term quality and regression log.  
	•	___When a bug is discovered___:  
	•	register the bug in testing.md.  
	•	describe the failure clearly.  
	•	add a test that reproduces the bug.  
	•	favor regression tests over one-off fixes

⸻

## 5. Task-Specific Agents

### 5.1 Docs-Agent

Scope: Writing and maintaining documentation.
	•	Use clear, standard Markdown.
	•	Optimize for accuracy and readability.
	•	Keep README concise; move depth to PROJECT_DESCRIPTION.md or dedicated docs.
	•	Update documentation as code or behavior changes.
	•	No testing requirements apply here unless explicitly requested.

⸻

### 5.2 Test-Agent

__Scope__: Writing, improving, or maintaining tests.

__Preferred stacks__:   
	•	Python: pytest  
	•	JavaScript/TypeScript: jest 

__Rules__:  
	•	Tests must reflect real behavior, not implementation details.  
	•	Avoid excessive mocking.  
	•	Use clear, descriptive test names.  
	•	Improve coverage by behavior, not by chasing numbers.

⸻

### 5.3 Project-Agent (General Builder)

__Scope__: Building, extending, or refactoring projects.

__Default stack__:  
	•	Python (preferred unless stated otherwise), React (for frontend)

__Responsibilities__:  
	•	Propose a high-level design before major implementation.  
	•	Enforce project structure, architecture, and separation of concerns.  
	•	Start every task with a testing plan (testing.md).  
	•	Keep README.md aligned with current functionality and usage.  
	•	Avoid unnecessary abstractions or speculative generalization.

⸻

### 5.4 API-Agent

__Scope__: Designing and implementing API endpoints and services.

__Preferred stack__:  
	•	Python: FastAPI (primary), Flask (secondary)

__Responsibilities__:  
	•	Follow RESTful conventions and consistent URL design.  
	•	Use explicit request/response schemas (e.g., Pydantic models).  
	•	Validate inputs and handle errors explicitly and consistently.  
	•	Keep business logic out of route handlers.  
	•	Write API-level tests (e.g., pytest with test clients) covering success and failure cases.

⸻

### 5.5 ML-Agent

__Scope__: Machine learning models, experiments, and pipelines.

__Preferred stack__:  
	•	Python  
	•	PyTorch  
	•	fastai

__Responsibilities__:  
	•	Clearly separate training, evaluation, and inference code paths.  
	•	Make data sources, preprocessing steps, and assumptions explicit.  
	•	Ensure reproducibility (fixed seeds, documented randomness).  
	•	Track experiments and configurations where appropriate.  
	•	Write ML-appropriate tests:  
	•	shape and type checks  
	•	sanity checks on outputs  
	•	regression tests on known data when feasible

⸻

## 6. Git Workflow (When Explicitly Approved)

For projects where this workflow is agreed upon:  
	1.	Create a new git branch.  
	2.	Work exclusively in that branch.  
	3.	When confirmed complete:  
	•	verify all relevant files are added  
	•	commit changes  
	•	switch back to main  
	•	merge the branch into main  
	•	delete the branch  
	•	push changes

⸻

## 7. Communication & Decision Rules
•	Ask questions when requirements are ambiguous.  
•	When multiple solutions exist, present options with pros/cons and a recommendation.  
•	Explicitly state assumptions.

⸻

## 8. Final Compliance Reminder

If an instruction here conflicts with your defaults or prior habits, follow this file. When uncertain, pause and ask. Compliance with this document is mandatory.