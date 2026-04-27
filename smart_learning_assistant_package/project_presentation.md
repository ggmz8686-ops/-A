# Smart Learning Assistant

## Slide 1. Project Title

**Smart Learning Assistant**

- A local Python-based intelligent learning assistant
- Covers Q&A, practice, study planning, summarization, language learning, and study tools
- Suitable for classroom demos, course projects, and prototype presentations

Speaker notes:
This project is a local intelligent learning assistant built with Python. Our goal was to create one unified tool that supports several common student learning tasks instead of solving only a single problem.

---

## Slide 2. Project Background

**Why did we build this project?**

- Students often switch between many separate tools while studying
- Common needs include asking questions, doing exercises, making plans, and reviewing materials
- Many solutions rely on cloud services, but local tools are simpler to deploy and easier to demonstrate

Speaker notes:
We observed that study workflows are fragmented. A student may need one tool for notes, one for practice, one for scheduling, and another for translation. So we designed a lightweight local assistant that combines these needs into one command-line system.

---

## Slide 3. Project Goal

**What problem are we solving?**

- Integrate multiple study functions into one system
- Run fully offline without external APIs
- Provide a simple command-line interface for interaction
- Store learning records locally for later review

Speaker notes:
Our focus is practicality and completeness. We wanted the system to be usable on a local machine, easy to test, and able to show the full learning loop: ask, practice, plan, review, and improve.

---

## Slide 4. Overall Architecture

**Project structure**

- `main.py`: program entry and menu interaction
- `src/qa.py`: knowledge Q&A
- `src/practice.py`: question generation and grading
- `src/plan.py`: study plan and progress tracking
- `src/summary.py`: summarization and outline generation
- `src/language.py`: vocabulary, essay correction, translation
- `src/tools.py`: calculator, unit conversion, schedule, todo, countdown
- `src/utils.py`: database and shared utilities

Speaker notes:
The project uses a modular structure. Each major learning scenario is placed in an independent module, while shared logic such as database initialization and file reading is placed in `utils.py`.

---

## Slide 5. Core Function 1: Knowledge Q&A

**Q&A module**

- Supports common questions in math, English, physics, and programming
- Combines built-in knowledge with local data files
- Uses keyword matching to identify subject and concept
- Returns explanation, solving steps, and common mistakes

Example:
- Input: "What is a prime number?"
- Output: concept explanation + steps + common errors

Speaker notes:
This module is not based on online search or a large language model. Instead, it uses built-in structured knowledge and local matching rules, which makes it easier to control and demonstrate.

---

## Slide 6. Core Function 2: Practice and Wrong-Question Book

**Practice module**

- Generates questions by subject and difficulty
- Supports multiple-choice, fill-in-the-blank, and short-answer questions
- Grades objective questions directly
- Uses text similarity for short-answer grading
- Stores wrong answers in SQLite as a wrong-question notebook

Speaker notes:
This part simulates the full exercise workflow. The student can generate questions, submit answers, get feedback, and review mistakes later. That gives the project stronger educational value than a simple static demo.

---

## Slide 7. Core Function 3: Study Planning

**Planning and progress tracking**

- Creates study plans based on goal, days, and subjects
- Automatically splits study hours across subjects
- Generates daily tasks
- Tracks task status: `pending`, `in_progress`, `completed`
- Produces a progress report from database records

Speaker notes:
This module turns abstract goals into concrete daily tasks. It also keeps progress in the database, so the system is not only answering questions but also supporting long-term learning management.

---

## Slide 8. Core Function 4: Summary, Language, and Tools

**Other useful modules**

- Summary:
  - text summarization
  - chapter outline generation
  - Markdown mind map generation
- Language learning:
  - vocabulary review
  - essay correction
  - Chinese-English translation
- Tools:
  - formula lookup
  - calculator
  - unit conversion
  - base conversion
  - todo list
  - course schedule
  - countdown

Speaker notes:
These modules make the project feel like a complete assistant instead of a single-purpose script. They support review, language practice, and everyday study utilities.

---

## Slide 9. Data Storage and Local Design

**How data is managed**

- `data/qa_data.jsonl`: question-answer data
- `data/questions.csv`: practice questions
- `data/vocab.csv`: vocabulary data
- `data/learning_assistant.db`: SQLite database

Database stores:

- study plans
- tasks
- wrong questions
- vocabulary learning records

Speaker notes:
One important design choice is that the whole system runs locally. This means no external dependency is required, and all records stay on the user's machine, which is good for portability and privacy.

---

## Slide 10. Typical User Flow

**How a student uses the system**

1. Start the program from the command line
2. Choose a module from the main menu
3. Ask a question, practice exercises, or create a plan
4. Save progress and wrong answers automatically
5. Return later to review reports and continue learning

Speaker notes:
This slide is useful before a demo. It shows that our system is organized around the student's workflow, not just around code modules.

---

## Slide 11. Project Highlights

**Strengths of the project**

- Clear modular structure
- Fully local and easy to deploy
- Covers multiple learning scenarios
- Includes persistent storage with SQLite
- Suitable as a teaching demo or prototype system

Speaker notes:
From an engineering point of view, the project is easy to read and extend. From a product point of view, it already covers several real student use cases in one place.

---

## Slide 12. Current Limitations

**What can still be improved**

- Rule-based Q&A is limited compared with real AI systems
- Translation and essay correction are relatively simple
- Question bank size is still small
- Tool state like todo list and schedule is not permanently stored across fresh object instances
- Some text encoding and test consistency issues still need cleanup

Speaker notes:
This is an honest and important slide for presentations. It shows that we understand the current boundary of the system and can clearly identify the next engineering steps.

---

## Slide 13. Future Work

**Next steps**

- Expand the local knowledge base and question bank
- Improve answer matching and grading logic
- Add a GUI or web interface
- Introduce smarter NLP or model-based capabilities
- Improve persistence for all user tools
- Optimize tests and fix encoding problems

Speaker notes:
The project already works as a functional prototype, but there is a clear path toward a more intelligent and user-friendly product.

---

## Slide 14. Closing

**Summary**

- Our project builds a local intelligent learning assistant
- It supports questioning, practicing, planning, reviewing, and utility tools
- It demonstrates both educational value and software modularity

**Thank you**

Speaker notes:
If needed, we can now move into a live demo by showing the command-line menu and briefly using two or three representative functions such as Q&A, practice, and study plan generation.
