from __future__ import annotations

import json
import os
import sys
from typing import Any
from math import floor

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.language import correct_essay, translate_text, vocab_train
from src.plan import get_progress_report, log_progress, make_study_plan
from src.practice import (
    generate_questions,
    get_practice_catalog,
    get_wrong_book_summary,
    get_wrong_questions,
    grade_answer,
    retry_wrong_question,
    update_wrong_question,
)
from src.qa import answer_question
from src.summary import generate_mindmap, outline_chapter, summarize_text
from src.tools import tool_query
from src.utils import get_db_connection, init_database


app = Flask(__name__)
CORS(app)


try:
    init_database()
except Exception as exc:
    print(f"数据库初始化失败: {exc}")


def _normalize_half_hour(value: float) -> float:
    if value <= 0:
        return 0.0
    return max(0.5, floor(value * 2 + 0.5) / 2)


def _fetch_latest_plan() -> dict[str, Any] | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM study_plans ORDER BY id DESC LIMIT 1")
    plan = cursor.fetchone()

    if not plan:
        conn.close()
        return None

    cursor.execute(
        "SELECT * FROM tasks WHERE plan_id = ? ORDER BY scheduled_date ASC, id ASC",
        (plan["id"],),
    )
    tasks = cursor.fetchall()
    conn.close()

    task_list: list[dict[str, Any]] = []
    completed_count = 0
    for task in tasks:
        if task["status"] == "completed":
            completed_count += 1
        task_list.append(
            {
                "id": task["id"],
                "task_name": task["task_name"],
                "subject": task["subject"],
                "duration": task["duration"],
                "status": task["status"],
                "scheduled_date": task["scheduled_date"],
                "completed_at": task["completed_at"],
            }
        )

    total_count = len(task_list)
    completion_rate = round((completed_count / total_count) * 100, 1) if total_count else 0.0

    return {
        "id": plan["id"],
        "goal": plan["goal"],
        "start_date": plan["start_date"],
        "end_date": plan["end_date"],
        "subjects": json.loads(plan["subjects"]),
        "created_at": plan["created_at"],
        "study_hours_per_day": plan["study_hours_per_day"] if "study_hours_per_day" in plan.keys() else None,
        "tasks": task_list,
        "stats": {
            "total_tasks": total_count,
            "completed_tasks": completed_count,
            "completion_rate": completion_rate,
        },
    }


def _dashboard_payload() -> dict[str, Any]:
    latest_plan = _fetch_latest_plan()
    wrong_questions = get_wrong_questions(status="active")
    recent_wrong = wrong_questions[:3]

    stats = {
        "wrong_questions_count": len(wrong_questions),
        "total_tasks": 0,
        "completed_tasks": 0,
        "completion_rate": 0.0,
    }
    today_tasks: list[dict[str, Any]] = []

    if latest_plan:
        stats.update(latest_plan["stats"])
        today_tasks = latest_plan["tasks"][:5]

    return {
        "latest_plan": latest_plan,
        "today_tasks": today_tasks,
        "recent_wrong_questions": recent_wrong,
        "stats": stats,
    }


@app.route("/")
def dashboard_page():
    return render_template("dashboard.html", active="dashboard")


@app.route("/qa")
def qa_page():
    return render_template("qa.html", active="qa")


@app.route("/practice")
def practice_page():
    return render_template("practice.html", active="practice")


@app.route("/plan")
def plan_page():
    return render_template("plan.html", active="plan")


@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    try:
        return jsonify(_dashboard_payload())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/plan/latest", methods=["GET"])
def api_latest_plan():
    try:
        latest_plan = _fetch_latest_plan()
        if latest_plan is None:
            return jsonify({"plan": None})
        return jsonify({"plan": latest_plan})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/qa", methods=["POST"])
def api_qa():
    try:
        data = request.get_json(silent=True) or {}
        question = (data.get("question") or "").strip()
        if not question:
            return jsonify({"error": "请输入问题。"}), 400

        return jsonify(answer_question(question))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/practice/metadata", methods=["GET"])
def api_practice_metadata():
    try:
        return jsonify(get_practice_catalog())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/practice/generate", methods=["POST"])
def api_generate_questions():
    try:
        data = request.get_json(silent=True) or {}
        subject = (data.get("subject") or "").strip()
        grade = (data.get("grade") or data.get("difficulty") or "").strip()
        count = int(data.get("count", 5))
        concept = (data.get("concept") or "").strip()
        raw_question_types = data.get("question_types") or data.get("question_type") or []

        if isinstance(raw_question_types, str):
            question_types = [item.strip() for item in raw_question_types.split(",") if item.strip()]
        else:
            question_types = [str(item).strip() for item in raw_question_types if str(item).strip()]

        if not subject or not grade:
            return jsonify({"error": "请选择年级和学科。"}), 400

        questions = generate_questions(subject, grade, count, question_types=question_types, concept=concept)
        actual_question_types = list(dict.fromkeys(question.get("type", "") for question in questions if question.get("type")))
        used_type_fallback = any(question.get("used_type_fallback") for question in questions)
        return jsonify(
            {
                "questions": questions,
                "meta": {
                    "requested_count": count,
                    "generated_count": len(questions),
                    "requested_question_types": question_types,
                    "actual_question_types": actual_question_types,
                    "used_type_fallback": used_type_fallback,
                    "concept": concept,
                },
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/practice/grade", methods=["POST"])
def api_grade_answer():
    try:
        data = request.get_json(silent=True) or {}
        question = data.get("question")
        raw_user_answer = data.get("user_answer")

        if isinstance(raw_user_answer, list):
            user_answer: Any = [str(item).strip() for item in raw_user_answer if str(item).strip()]
        else:
            user_answer = str(raw_user_answer or "").strip()

        if not question or (isinstance(user_answer, list) and not user_answer) or (not isinstance(user_answer, list) and not user_answer):
            return jsonify({"error": "请输入题目和答案。"}), 400

        if isinstance(question, dict):
            question_payload = question
        else:
            question_payload = {
                "question": str(question),
                "correct_answer": data.get("correct_answer", "标准答案"),
                "type": data.get("type", "简答题"),
                "subject": data.get("subject", "未知"),
                "grade": data.get("grade", data.get("difficulty", "未知")),
                "difficulty": data.get("difficulty", data.get("grade", "未知")),
            }

        result = grade_answer(question_payload, user_answer)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/practice/wrong", methods=["GET"])
def api_get_wrong_questions():
    try:
        status = request.args.get("status")
        return jsonify(
            {
                "wrong_questions": get_wrong_questions(status=status),
                "summary": get_wrong_book_summary(),
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/practice/wrong/<int:question_id>", methods=["POST"])
def api_update_wrong_question(question_id: int):
    try:
        data = request.get_json(silent=True) or {}
        action = (data.get("action") or "").strip()
        if not action:
            return jsonify({"error": "缺少操作类型。"}), 400

        success = update_wrong_question(question_id, action)
        if not success:
            return jsonify({"error": "操作失败，请检查题目是否存在。"}), 400

        return jsonify(
            {
                "success": True,
                "summary": get_wrong_book_summary(),
                "wrong_questions": get_wrong_questions(),
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/practice/wrong/<int:question_id>/retry", methods=["POST"])
def api_retry_wrong_question(question_id: int):
    try:
        data = request.get_json(silent=True) or {}
        raw_user_answer = data.get("user_answer")
        if isinstance(raw_user_answer, list):
            user_answer: Any = [str(item).strip() for item in raw_user_answer if str(item).strip()]
        else:
            user_answer = str(raw_user_answer or "").strip()

        if (isinstance(user_answer, list) and not user_answer) or (not isinstance(user_answer, list) and not user_answer):
            return jsonify({"error": "请先完成这道错题的重新作答。"}), 400

        result = retry_wrong_question(question_id, user_answer)
        if result is None:
            return jsonify({"error": "这道错题不存在，可能已经被删除。"}), 404

        return jsonify(
            {
                "result": result,
                "summary": get_wrong_book_summary(),
                "wrong_questions": get_wrong_questions(),
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/plan/make", methods=["POST"])
def api_make_study_plan():
    try:
        data = request.get_json(silent=True) or {}
        goal = (data.get("goal") or "").strip()
        days = data.get("days")
        subjects = data.get("subjects")
        study_hours_per_day = _normalize_half_hour(float(data.get("study_hours_per_day") or 2))

        if not goal or not days or not subjects or study_hours_per_day <= 0:
            return jsonify({"error": "请填写完整的计划信息。"}), 400

        if isinstance(subjects, str):
            subject_list = [item.strip() for item in subjects.split(",") if item.strip()]
        else:
            subject_list = [str(item).strip() for item in subjects if str(item).strip()]

        plan = make_study_plan(goal, int(days), subject_list, study_hours_per_day)
        return jsonify(plan)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/plan/log", methods=["POST"])
def api_log_progress():
    try:
        data = request.get_json(silent=True) or {}
        task_id = data.get("task_id")
        status = data.get("status")

        if not task_id or not status:
            return jsonify({"error": "请输入任务 ID 和状态。"}), 400

        success = log_progress(int(task_id), status)
        return jsonify({"success": success})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/plan/report", methods=["GET"])
def api_get_progress_report():
    try:
        return jsonify({"report": get_progress_report()})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/summary/text", methods=["POST"])
def api_summarize_text():
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text")
        max_length = data.get("max_length", 500)
        if not text:
            return jsonify({"error": "请输入文本。"}), 400
        return jsonify({"summary": summarize_text(text, max_length)})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/summary/mindmap", methods=["POST"])
def api_generate_mindmap():
    try:
        data = request.get_json(silent=True) or {}
        topic = data.get("topic")
        content = data.get("content")
        if not topic or not content:
            return jsonify({"error": "请输入主题和内容。"}), 400
        return jsonify({"mindmap": generate_mindmap(topic, content)})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/summary/outline", methods=["POST"])
def api_outline_chapter():
    try:
        data = request.get_json(silent=True) or {}
        chapter = data.get("chapter")
        content = data.get("content")
        if not chapter or not content:
            return jsonify({"error": "请输入章节名称和内容。"}), 400
        return jsonify({"outline": outline_chapter(chapter, content)})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/language/vocab", methods=["POST"])
def api_vocab_train():
    try:
        data = request.get_json(silent=True) or {}
        words = data.get("words")
        mode = data.get("mode", "review")
        if not words:
            return jsonify({"error": "请输入单词。"}), 400
        word_list = [item.strip() for item in words.split(",") if item.strip()]
        return jsonify(vocab_train(word_list, mode))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/language/essay", methods=["POST"])
def api_correct_essay():
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text")
        if not text:
            return jsonify({"error": "请输入作文内容。"}), 400
        return jsonify(correct_essay(text))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/language/translate", methods=["POST"])
def api_translate_text():
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text")
        src = data.get("src")
        tgt = data.get("tgt")
        if not text or not src or not tgt:
            return jsonify({"error": "请输入完整的翻译信息。"}), 400
        return jsonify({"translation": translate_text(text, src, tgt)})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/tools/query", methods=["POST"])
def api_tool_query():
    try:
        data = request.get_json(silent=True) or {}
        tool_type = data.get("tool_type")
        params = data.get("params", {})
        if not tool_type:
            return jsonify({"error": "请指定工具类型。"}), 400
        return jsonify({"result": tool_query(tool_type, params)})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
