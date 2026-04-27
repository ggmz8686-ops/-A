(function () {
  const STORAGE_KEY = "slaPreviewStateV2";
  const seed = window.__SLA_PREVIEW_SEED__ || {};

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return clone(seed);
      const parsed = JSON.parse(raw);
      return Object.assign(clone(seed), parsed);
    } catch (error) {
      return clone(seed);
    }
  }

  function saveState(state) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function nowString() {
    return new Date().toLocaleString("zh-CN", { hour12: false });
  }

  function todayString() {
    return new Date().toISOString().slice(0, 10);
  }

  function parseUrl(input) {
    const raw = typeof input === "string" ? input : input.url;
    return new URL(raw, "https://preview.local");
  }

  function response(payload, ok) {
    return {
      ok: ok !== false,
      json: async function () {
        return clone(payload);
      }
    };
  }

  function getPlanStats(plan) {
    if (!plan) {
      return { total_tasks: 0, completed_tasks: 0, completion_rate: 0 };
    }
    const total = plan.tasks.length;
    const completed = plan.tasks.filter(function (task) {
      return task.status === "completed";
    }).length;
    return {
      total_tasks: total,
      completed_tasks: completed,
      completion_rate: total ? Math.round((completed / total) * 1000) / 10 : 0
    };
  }

  function getWrongSummary(state) {
    const active = state.wrongQuestions.filter(function (item) {
      return item.notebook_status === "active";
    });
    const mastered = state.wrongQuestions.filter(function (item) {
      return item.notebook_status === "mastered";
    });
    const subjectMap = new Map();
    state.wrongQuestions.forEach(function (item) {
      const count = subjectMap.get(item.subject) || 0;
      subjectMap.set(item.subject, count + 1);
    });
    const topSubjects = Array.from(subjectMap.entries())
      .map(function (entry) {
        return { subject: entry[0], count: entry[1] };
      })
      .sort(function (a, b) {
        return b.count - a.count;
      })
      .slice(0, 3);

    return {
      total: state.wrongQuestions.length,
      active: active.length,
      mastered: mastered.length,
      total_reviews: state.wrongQuestions.reduce(function (sum, item) {
        return sum + (item.review_count || 0);
      }, 0),
      top_subjects: topSubjects
    };
  }

  function getDashboardPayload(state) {
    const latestPlan = state.latestPlan ? clone(state.latestPlan) : null;
    if (latestPlan) {
      latestPlan.stats = getPlanStats(latestPlan);
    }
    return {
      latest_plan: latestPlan,
      today_tasks: latestPlan ? latestPlan.tasks.slice(0, 5) : [],
      recent_wrong_questions: state.wrongQuestions
        .filter(function (item) {
          return item.notebook_status === "active";
        })
        .slice(0, 3),
      stats: Object.assign(
        {
          wrong_questions_count: state.wrongQuestions.filter(function (item) {
            return item.notebook_status === "active";
          }).length
        },
        getPlanStats(latestPlan)
      )
    };
  }

  function buildPracticeRecommendation(question) {
    const lower = question.toLowerCase();
    if (lower.indexOf("python") !== -1) {
      return { subject: "Python", grade: "高一", question_types: ["判断", "简答"], count: 3, concept: "Python" };
    }
    if (question.indexOf("质数") !== -1) {
      return { subject: "数学", grade: "小学五年级", question_types: ["判断"], count: 3, concept: "质数" };
    }
    if (question.indexOf("牛顿") !== -1) {
      return { subject: "物理", grade: "高一", question_types: ["简答"], count: 3, concept: "牛顿第二定律" };
    }
    return { subject: "高等数学", grade: "大学", question_types: ["单选", "简答"], count: 3, concept: "核心概念" };
  }

  function buildQuestions(body, state) {
    const subject = body.subject || "高等数学";
    const grade = body.grade || "大学";
    const count = Math.max(1, Math.min(20, Number(body.count || 4)));
    const questionTypes = Array.isArray(body.question_types) && body.question_types.length
      ? body.question_types
      : ["单选", "多选", "判断", "简答"];
    const concept = body.concept || "";
    const questions = [];

    function makeQuestion(index, type) {
      const base = {
        id: "preview-" + Date.now() + "-" + index,
        subject: subject,
        grade: grade,
        difficulty: grade,
        type: type,
        question_type: type,
        concept: concept,
        practice_round: 1
      };

      if (type === "判断") {
        return Object.assign(base, {
          question: concept ? "“" + concept + "”相关判断题 " + (index + 1) : subject + " 判断题 " + (index + 1),
          options: ["对", "错"],
          correct_answer: "对",
          explanation: "判断题预览会根据关键词给出基础反馈。"
        });
      }

      if (type === "多选") {
        return Object.assign(base, {
          question: concept ? "“" + concept + "”相关多选题 " + (index + 1) : subject + " 多选题 " + (index + 1),
          options: ["核心概念", "关键步骤", "无关信息", "常见误区"],
          correct_answer: "核心概念、关键步骤",
          explanation: "多选题会重点考查知识点覆盖和判断准确度。"
        });
      }

      if (type === "简答") {
        return Object.assign(base, {
          question: concept ? "请简要说明“" + concept + "”的核心内容。" : "请简要说明这道 " + subject + " 题的思路。",
          options: [],
          correct_answer: "围绕定义、关键步骤和结论进行简要说明。",
          explanation: "简答题预览支持宽松判分和改进建议。"
        });
      }

      return Object.assign(base, {
        question: concept ? "“" + concept + "”相关单选题 " + (index + 1) : subject + " 单选题 " + (index + 1),
        options: ["核心概念", "错误概念", "无关概念", "反向结论"],
        correct_answer: "核心概念",
        explanation: "单选题预览主要模拟题目生成和答题反馈。"
      });
    }

    for (let i = 0; i < count; i += 1) {
      questions.push(makeQuestion(i, questionTypes[i % questionTypes.length]));
    }

    return {
      questions: questions,
      meta: {
        requested_count: count,
        generated_count: questions.length,
        requested_question_types: questionTypes,
        actual_question_types: questionTypes,
        used_type_fallback: false,
        concept: concept
      }
    };
  }

  function normalizeAnswer(userAnswer) {
    if (Array.isArray(userAnswer)) {
      return userAnswer.map(String).map(function (item) { return item.trim(); }).filter(Boolean);
    }
    return String(userAnswer || "").trim();
  }

  function isCorrectAnswer(question, userAnswer) {
    const type = question.type || question.question_type || "简答";
    const correct = question.correct_answer || "";

    if (type === "多选") {
      const correctList = String(correct).split("、").map(function (item) { return item.trim(); }).filter(Boolean);
      const userList = Array.isArray(userAnswer) ? userAnswer.slice().sort() : [];
      return JSON.stringify(correctList.sort()) === JSON.stringify(userList);
    }

    if (type === "判断" || type === "单选") {
      return String(userAnswer) === String(correct);
    }

    const normalized = String(userAnswer).replace(/\s+/g, "");
    return normalized.length >= 8;
  }

  function addWrongQuestion(state, question, userAnswer) {
    state.nextWrongId += 1;
    const now = nowString();
    const record = {
      id: state.nextWrongId,
      question: question.question,
      correct_answer: question.correct_answer,
      user_answer: Array.isArray(userAnswer) ? userAnswer.join("、") : userAnswer,
      explanation: question.explanation || "建议回到知识点，再做一轮针对性练习。",
      improvement: "下一次作答时先抓住定义、条件和结论。",
      question_type: question.question_type || question.type || "简答",
      type: question.type || question.question_type || "简答",
      subject: question.subject || "未知",
      grade: question.grade || question.difficulty || "未知",
      difficulty: question.difficulty || question.grade || "未知",
      options: question.options || [],
      notebook_status: "active",
      review_count: 0,
      timestamp: now,
      last_reviewed_at: null,
      mastered_at: null
    };
    state.wrongQuestions.unshift(record);
    return record;
  }

  function createPlan(body, state) {
    const goal = String(body.goal || "").trim();
    const rawSubjects = body.subjects;
    const subjectList = Array.isArray(rawSubjects)
      ? rawSubjects.map(String).map(function (item) { return item.trim(); }).filter(Boolean)
      : String(rawSubjects || "").split(/[,，]/).map(function (item) { return item.trim(); }).filter(Boolean);
    const days = Math.max(1, Number(body.days || 7));
    const studyHoursPerDay = Math.max(0.5, Number(body.study_hours_per_day || 2));

    if (!goal || !subjectList.length) {
      return { error: "请先填写目标、学习时间和科目。" };
    }

    const planId = state.nextPlanId;
    state.nextPlanId += 1;
    let taskCursor = state.nextTaskId;
    state.nextTaskId += days;

    const start = new Date();
    const tasks = [];
    const dailyPlans = [];
    const subjectHours = {};
    subjectList.forEach(function (subject) {
      subjectHours[subject] = 0;
    });

    for (let index = 0; index < days; index += 1) {
      const taskDate = new Date(start);
      taskDate.setDate(start.getDate() + index);
      const subject = subjectList[index % subjectList.length];
      const date = taskDate.toISOString().slice(0, 10);
      subjectHours[subject] += studyHoursPerDay;
      dailyPlans.push({
        date: date,
        subjects: subject,
        hours: studyHoursPerDay
      });
      tasks.push({
        id: taskCursor + index,
        task_name: "学习" + subject,
        subject: subject,
        duration: Math.round(studyHoursPerDay * 60),
        status: index === 0 ? "in_progress" : "pending",
        scheduled_date: date,
        completed_at: null
      });
    }

    const plan = {
      id: planId,
      goal: goal,
      start_date: dailyPlans[0].date,
      end_date: dailyPlans[dailyPlans.length - 1].date,
      created_at: nowString(),
      study_hours_per_day: studyHoursPerDay,
      subjects: subjectList,
      tasks: tasks
    };
    state.latestPlan = plan;
    saveState(state);

    const examPlan = {
      sprint_plan: dailyPlans.map(function (item) {
        return {
          date: item.date,
          subject: item.subjects,
          hours: item.hours,
          focus: "重点复习" + item.subjects + "的核心知识点"
        };
      }),
      key_points: subjectList.reduce(function (acc, subject) {
        acc[subject] = subject === "英语"
          ? ["词汇", "语法", "阅读", "写作"]
          : ["核心概念", "重点原理", "典型例题", "常见错误"];
        return acc;
      }, {})
    };

    return {
      plan_id: planId,
      goal: goal,
      start_date: plan.start_date,
      end_date: plan.end_date,
      total_days: days,
      study_hours_per_day: studyHoursPerDay,
      total_hours: Math.round(days * studyHoursPerDay * 10) / 10,
      subject_hours: subjectHours,
      daily_plans: dailyPlans,
      tasks: tasks.map(function (task) {
        return {
          id: task.id,
          name: task.task_name,
          subject: task.subject,
          duration: studyHoursPerDay,
          status: task.status,
          scheduled_date: task.scheduled_date
        };
      }),
      exam_plan: examPlan
    };
  }

  function logPlanProgress(body, state) {
    if (!state.latestPlan) return { error: "当前没有学习计划。" };
    const taskId = Number(body.task_id);
    const status = String(body.status || "").trim();
    const task = state.latestPlan.tasks.find(function (item) {
      return item.id === taskId;
    });
    if (!task) return { error: "任务不存在。" };
    task.status = status || "pending";
    task.completed_at = task.status === "completed" ? nowString() : null;
    saveState(state);
    return { success: true };
  }

  function updateWrongQuestion(state, id, action) {
    const item = state.wrongQuestions.find(function (entry) {
      return entry.id === id;
    });
    if (!item) return { error: "操作失败，请检查题目是否存在。" };
    if (action === "delete") {
      state.wrongQuestions = state.wrongQuestions.filter(function (entry) {
        return entry.id !== id;
      });
    } else if (action === "reactivate") {
      item.notebook_status = "active";
      item.mastered_at = null;
    } else {
      return { error: "缺少操作类型。" };
    }
    saveState(state);
    return {
      success: true,
      summary: getWrongSummary(state),
      wrong_questions: state.wrongQuestions
    };
  }

  function retryWrongQuestion(state, id, userAnswer) {
    const item = state.wrongQuestions.find(function (entry) {
      return entry.id === id;
    });
    if (!item) return { error: "这道错题不存在，可能已经被删除。" };

    const normalizedAnswer = normalizeAnswer(userAnswer);
    const correct = isCorrectAnswer(item, normalizedAnswer);
    item.review_count = (item.review_count || 0) + 1;
    item.last_reviewed_at = nowString();
    if (correct) {
      item.notebook_status = "mastered";
      item.mastered_at = nowString();
    }
    saveState(state);
    return {
      result: {
        is_correct: correct,
        score: correct ? 100 : 60,
        user_answer: Array.isArray(normalizedAnswer) ? normalizedAnswer.join("、") : normalizedAnswer,
        correct_answer: item.correct_answer,
        explanation: item.explanation,
        improvement: correct ? "" : item.improvement
      },
      summary: getWrongSummary(state),
      wrong_questions: state.wrongQuestions
    };
  }

  function handleRoute(url, method, body) {
    const state = loadState();

    if (url.pathname === "/api/dashboard" && method === "GET") {
      return response(getDashboardPayload(state));
    }

    if (url.pathname === "/api/plan/latest" && method === "GET") {
      const plan = state.latestPlan ? clone(state.latestPlan) : null;
      if (plan) plan.stats = getPlanStats(plan);
      return response({ plan: plan });
    }

    if (url.pathname === "/api/plan/make" && method === "POST") {
      const payload = createPlan(body, state);
      return response(payload, !payload.error);
    }

    if (url.pathname === "/api/plan/log" && method === "POST") {
      const payload = logPlanProgress(body, state);
      return response(payload, !payload.error);
    }

    if (url.pathname === "/api/qa" && method === "POST") {
      const question = String(body.question || "").trim();
      if (!question) return response({ error: "请输入问题。" }, false);
      return response({
        answer: "这是静态预览里的回答示例。我会先解释“" + question + "”的核心概念，再给你一个下一步练习建议。",
        practice_recommendation: buildPracticeRecommendation(question)
      });
    }

    if (url.pathname === "/api/practice/metadata" && method === "GET") {
      return response(clone(state.catalog));
    }

    if (url.pathname === "/api/practice/generate" && method === "POST") {
      return response(buildQuestions(body, state));
    }

    if (url.pathname === "/api/practice/grade" && method === "POST") {
      const question = body.question || {};
      const userAnswer = normalizeAnswer(body.user_answer);
      const correct = isCorrectAnswer(question, userAnswer);
      if (!correct) {
        addWrongQuestion(state, question, userAnswer);
        saveState(state);
      }
      return response({
        score: correct ? 100 : 60,
        is_correct: correct,
        correct_answer: question.correct_answer || "",
        explanation: question.explanation || "可以回到知识点后再做一轮。",
        improvement: correct ? "" : "建议先抓住定义、条件和结论，再组织答案。"
      });
    }

    if (url.pathname === "/api/practice/wrong" && method === "GET") {
      const status = url.searchParams.get("status");
      const wrongQuestions = status
        ? state.wrongQuestions.filter(function (item) { return item.notebook_status === status; })
        : state.wrongQuestions;
      return response({
        summary: getWrongSummary(state),
        wrong_questions: clone(wrongQuestions)
      });
    }

    if (/^\/api\/practice\/wrong\/\d+$/.test(url.pathname) && method === "POST") {
      const id = Number(url.pathname.split("/").pop());
      const payload = updateWrongQuestion(state, id, String(body.action || "").trim());
      return response(payload, !payload.error);
    }

    if (/^\/api\/practice\/wrong\/\d+\/retry$/.test(url.pathname) && method === "POST") {
      const id = Number(url.pathname.split("/")[4]);
      const payload = retryWrongQuestion(state, id, body.user_answer);
      return response(payload, !payload.error);
    }

    return response({ error: "静态预览暂不支持该交互，请在本地后端环境体验。" }, false);
  }

  const nativeFetch = window.fetch ? window.fetch.bind(window) : null;
  window.__resetSmartLearningPreview = function () {
    localStorage.removeItem(STORAGE_KEY);
  };
  window.fetch = async function (input, init) {
    const url = parseUrl(input);
    const method = String((init && init.method) || (typeof input !== "string" && input.method) || "GET").toUpperCase();
    let body = {};
    if (init && init.body) {
      try {
        body = JSON.parse(init.body);
      } catch (error) {
        body = {};
      }
    }

    if (url.pathname.indexOf("/api/") === 0) {
      return handleRoute(url, method, body);
    }

    if (nativeFetch) {
      return nativeFetch(input, init);
    }

    throw new Error("Fetch unavailable");
  };
})();
