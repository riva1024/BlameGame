# The Blame Game: CS Group Project Simulator 🎓

> A multi-agent adversarial workflow simulation.

## 📖 Overview
**The Blame Game** simulates the nightmare of every college student: a failed group project. 

It uses **DeepSeek LLM** to model a high-stakes meeting where three students (Agents) must explain to a Professor why their final demo crashed. The goal is to see if an AI Judge can identify the "Slacker" who contributed nothing but uses **technical gaslighting** to shift blame.

## ⚙️ The Workflow
The system operates as a **Finite State Machine**:

1.  **Initialization**: 
    * Creates 3 Agents: **2 Workers** (Honest) and **1 Slacker** (Deceptive).
2.  **Debate Loop (3 Rounds)**: 
    * Agents argue in **Chinese** (simulating local context).
    * Workers use facts; the Slacker uses fake jargon.
3.  **Verdict**: 
    * The Professor Agent analyzes the transcript.
    * The identified saboteur receives a **FAIL** grade.

## 🚀 Quick Start

1.  **Install Dependencies**
    ```bash
    pip install openai colorama
    ```

2.  **Configure API**
    Open `main.py` and set your Key:
    ```python
    DEEPSEEK_KEY = "sk-your-key-here"
    ```

3.  **Run**
    ```bash
    python main.py
    ```

