from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from .config import DEFAULT_STUDY_HOURS_PER_DAY
from .utils import get_current_date, get_current_datetime, get_db_connection


class StudyPlanSystem:
    def make_study_plan(
        self,
        goal: str,
        days: int,
        subjects: list[str],
        study_hours_per_day: float = DEFAULT_STUDY_HOURS_PER_DAY,
    ) -> dict[str, Any]:
        start_date = get_current_date()
        end_date = (
            datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=days - 1)
        ).strftime("%Y-%m-%d")

        total_hours = round(days * study_hours_per_day, 1)
        subject_hours = self._allocate_subject_hours(subjects, total_hours)

        daily_plans: list[dict[str, Any]] = []
        current_date = start_date
        for day in range(days):
            subject = subjects[day % len(subjects)]
            daily_plans.append(
                {
                    "date": current_date,
                    "subjects": subject,
                    "hours": study_hours_per_day,
                }
            )
            current_date = (
                datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=1)
            ).strftime("%Y-%m-%d")

        plan_id = self.save_plan(
            goal=goal,
            start_date=start_date,
            end_date=end_date,
            subjects=subjects,
            study_hours_per_day=study_hours_per_day,
        )

        tasks: list[dict[str, Any]] = []
        for daily_plan in daily_plans:
            task_id = self.save_task(
                plan_id=plan_id,
                task_name=f"学习{daily_plan['subjects']}",
                subject=daily_plan["subjects"],
                duration=int(round(daily_plan["hours"] * 60)),
                status="pending",
                scheduled_date=daily_plan["date"],
            )
            tasks.append(
                {
                    "id": task_id,
                    "name": f"学习{daily_plan['subjects']}",
                    "subject": daily_plan["subjects"],
                    "duration": daily_plan["hours"],
                    "status": "pending",
                    "scheduled_date": daily_plan["date"],
                }
            )

        exam_plan = self.generate_exam_plan(subjects, days, study_hours_per_day)

        return {
            "plan_id": plan_id,
            "goal": goal,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": days,
            "study_hours_per_day": study_hours_per_day,
            "total_hours": total_hours,
            "subject_hours": subject_hours,
            "daily_plans": daily_plans,
            "tasks": tasks,
            "exam_plan": exam_plan,
        }

    def _allocate_subject_hours(self, subjects: list[str], total_hours: float) -> dict[str, float]:
        if not subjects:
            return {}

        base = round(total_hours / len(subjects), 1)
        allocated: dict[str, float] = {subject: base for subject in subjects}
        diff = round(total_hours - sum(allocated.values()), 1)
        if diff:
            allocated[subjects[0]] = round(allocated[subjects[0]] + diff, 1)
        return allocated

    def save_plan(
        self,
        goal: str,
        start_date: str,
        end_date: str,
        subjects: list[str],
        study_hours_per_day: float,
    ) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO study_plans (goal, start_date, end_date, subjects, created_at, study_hours_per_day)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                goal,
                start_date,
                end_date,
                json.dumps(subjects, ensure_ascii=False),
                get_current_datetime(),
                study_hours_per_day,
            ),
        )
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return int(plan_id)

    def save_task(
        self,
        plan_id: int,
        task_name: str,
        subject: str,
        duration: int,
        status: str,
        scheduled_date: str,
    ) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (plan_id, task_name, subject, duration, status, scheduled_date, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (plan_id, task_name, subject, duration, status, scheduled_date, None),
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return int(task_id)

    def log_progress(self, task_id: int, status: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        completed_at = get_current_datetime() if status == "completed" else None
        cursor.execute(
            """
            UPDATE tasks
            SET status = ?, completed_at = ?
            WHERE id = ?
            """,
            (status, completed_at, task_id),
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_progress_report(self) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_plans ORDER BY created_at DESC")
        plans = cursor.fetchall()

        report: list[str] = ["=== 学习进度报告 ===", ""]
        if not plans:
            report.append("暂无学习计划")
            conn.close()
            return "\n".join(report)

        for plan in plans:
            report.append(f"计划ID: {plan['id']}")
            report.append(f"目标: {plan['goal']}")
            report.append(f"时间范围: {plan['start_date']} 至 {plan['end_date']}")
            report.append(f"科目: {', '.join(json.loads(plan['subjects']))}")
            if "study_hours_per_day" in plan.keys() and plan["study_hours_per_day"] is not None:
                report.append(f"每日学习时间: {plan['study_hours_per_day']} 小时")
            report.append("")

            cursor.execute("SELECT * FROM tasks WHERE plan_id = ?", (plan["id"],))
            tasks = cursor.fetchall()
            if tasks:
                report.append("任务进度:")
                completed_count = 0
                total_count = len(tasks)
                for task in tasks:
                    if task["status"] == "completed":
                        marker = "✓ 已完成"
                        completed_count += 1
                    elif task["status"] == "in_progress":
                        marker = "◐ 进行中"
                    else:
                        marker = "○ 未完成"
                    report.append(f"  - {task['task_name']}（{task['scheduled_date']}）：{marker}")
                completion_rate = (completed_count / total_count) * 100 if total_count else 0
                report.append(f"\n完成率: {completion_rate:.1f}% ({completed_count}/{total_count})")
            else:
                report.append("暂无任务")

            report.append("-" * 50)

        conn.close()
        return "\n".join(report)

    def generate_exam_plan(
        self,
        subjects: list[str],
        days: int,
        study_hours_per_day: float,
    ) -> dict[str, Any]:
        sprint_plan: list[dict[str, Any]] = []
        current_date = get_current_date()

        for day in range(min(days, 7)):
            subject = subjects[day % len(subjects)]
            sprint_plan.append(
                {
                    "date": current_date,
                    "subject": subject,
                    "hours": study_hours_per_day,
                    "focus": f"重点复习{subject}的核心知识点",
                }
            )
            current_date = (
                datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=1)
            ).strftime("%Y-%m-%d")

        key_points: dict[str, list[str]] = {}
        for subject in subjects:
            if subject == "数学":
                key_points[subject] = ["函数", "方程", "几何", "概率统计"]
            elif subject == "英语":
                key_points[subject] = ["词汇", "语法", "阅读", "写作"]
            elif subject == "物理":
                key_points[subject] = ["力学", "电磁学", "光学", "热学"]
            elif subject == "编程":
                key_points[subject] = ["数据结构", "算法", "语言基础", "项目实践"]
            else:
                key_points[subject] = ["核心概念", "重点原理", "典型例题", "常见错误"]

        return {"sprint_plan": sprint_plan, "key_points": key_points}

    def get_plan_by_id(self, plan_id: int) -> dict[str, Any] | None:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_plans WHERE id = ?", (plan_id,))
        plan = cursor.fetchone()
        if not plan:
            conn.close()
            return None

        cursor.execute("SELECT * FROM tasks WHERE plan_id = ?", (plan_id,))
        tasks = cursor.fetchall()
        conn.close()

        task_list = [
            {
                "id": task["id"],
                "name": task["task_name"],
                "subject": task["subject"],
                "duration": task["duration"],
                "status": task["status"],
                "scheduled_date": task["scheduled_date"],
                "completed_at": task["completed_at"],
            }
            for task in tasks
        ]

        return {
            "id": plan["id"],
            "goal": plan["goal"],
            "start_date": plan["start_date"],
            "end_date": plan["end_date"],
            "subjects": json.loads(plan["subjects"]),
            "created_at": plan["created_at"],
            "study_hours_per_day": plan["study_hours_per_day"] if "study_hours_per_day" in plan.keys() else None,
            "tasks": task_list,
        }


def make_study_plan(
    goal: str,
    days: int,
    subjects: list[str],
    study_hours_per_day: float = DEFAULT_STUDY_HOURS_PER_DAY,
) -> dict[str, Any]:
    plan_system = StudyPlanSystem()
    return plan_system.make_study_plan(goal, days, subjects, study_hours_per_day)


def log_progress(task_id: int, status: str) -> bool:
    plan_system = StudyPlanSystem()
    return plan_system.log_progress(task_id, status)


def get_progress_report() -> str:
    plan_system = StudyPlanSystem()
    return plan_system.get_progress_report()
