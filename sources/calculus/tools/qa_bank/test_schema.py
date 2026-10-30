# -*- coding: utf-8 -*-
"""schema 模块单测（Task 2）。

运行: python -m unittest tools.qa_bank.test_schema -v
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

from qa_bank import schema  # noqa: E402


def base_exam(**over):
    """一道「合法真题」的基准样本。"""
    q = {
        "id": "ky2024-1-q1",
        "type": "single",
        "typeGroup": "single",
        "difficulty": "medium",
        "chapter": 1,
        "knowledgePoint": "1.6",
        "knowledgePoints": ["1.6"],
        "stem": "$\\lim\\limits_{x\\to 0}\\dfrac{\\sin x}{x}=$",
        "options": ["$1$", "$0$", "$e$", "$+\\infty$"],
        "answer": ["A"],
        "accept": None,
        "answerText": None,
        "points": None,
        "explanation": "**答案依据**：由第一个重要极限得 $1$，故 A 正确。\n"
                       "B 错：与定义矛盾。\nC 错：$e$ 出现在幂指型中。\nD 错：极限存在。",
        "misconception": None,
        "extension": None,
        "tags": ["重要极限"],
        "verify": [],
        "source": {
            "text": "2024 考研数学一 第 1 题",
            "kind": "exam-original",
            "year": 2024,
            "region": "全国",
            "paper": "数学一",
            "number": 1,
            "url": "https://example.org/ky2024-math1",
        },
        "provenance": {
            "level": "original",
            "url": "https://example.org/ky2024-math1",
            "verifiedAt": "2026-10-28",
            "note": "",
        },
    }
    q.update(over)
    return q


class TestValidateQuestion(unittest.TestCase):
    def test_valid_exam_original_passes(self):
        self.assertEqual(schema.validate_question(base_exam()), [])

    def test_exam_original_without_url_is_error(self):
        q = base_exam()
        q["source"]["url"] = ""
        msgs = schema.validate_question(q)
        self.assertTrue(any("source.url" in m for _, m in msgs), msgs)

    def test_exam_original_provenance_url_required(self):
        q = base_exam()
        q["provenance"]["url"] = ""
        msgs = schema.validate_question(q)
        self.assertTrue(any("provenance.url" in m for _, m in msgs), msgs)

    def test_exam_adapted_requires_tag(self):
        q = base_exam()
        q["source"]["kind"] = "exam-adapted"
        q["provenance"]["level"] = "adapted"
        q["tags"] = ["重点"]
        msgs = schema.validate_question(q)
        self.assertTrue(any("真题改编" in m for _, m in msgs), msgs)

    def test_exam_adapted_requires_note(self):
        q = base_exam()
        q["source"]["kind"] = "exam-adapted"
        q["provenance"]["level"] = "adapted"
        q["tags"] = ["真题改编"]
        q["provenance"]["note"] = ""
        msgs = schema.validate_question(q)
        self.assertTrue(any("provenance.note" in m for _, m in msgs), msgs)

    def test_exam_requires_year(self):
        q = base_exam()
        q["source"]["year"] = None
        msgs = schema.validate_question(q)
        self.assertTrue(any("source.year" in m for _, m in msgs), msgs)

    def test_unknown_knowledge_point_is_error(self):
        q = base_exam()
        q["knowledgePoint"] = "99.9"
        msgs = schema.validate_question(q)
        self.assertTrue(any("catalog.SEC" in m for _, m in msgs), msgs)

    def test_unknown_extra_knowledge_point_is_error(self):
        q = base_exam()
        q["knowledgePoints"] = ["1.6", "42.7"]
        msgs = schema.validate_question(q)
        self.assertTrue(any("knowledgePoints" in m for _, m in msgs), msgs)

    def test_unpaired_dollar_is_error(self):
        q = base_exam()
        q["stem"] = "$\\lim x = 1$ 未闭合 $"
        msgs = schema.validate_question(q)
        self.assertTrue(any("不成对" in m for _, m in msgs), msgs)

    def test_subjective_without_points_is_error(self):
        q = base_exam(type="calc", typeGroup="calc", options=[], answer=[],
                      answerText="完整解答", points=None, verify=[])
        msgs = schema.validate_question(q)
        self.assertTrue(any("points" in m for _, m in msgs), msgs)

    def test_calc_without_verify_is_error(self):
        q = base_exam(type="calc", typeGroup="calc", options=[], answer=[],
                      answerText="完整解答",
                      points=[{"text": "a", "partial": 2}], verify=[])
        msgs = schema.validate_question(q)
        self.assertTrue(any("verify" in m for _, m in msgs), msgs)

    def test_answer_outside_options_is_error(self):
        q = base_exam()
        q["answer"] = ["E"]
        msgs = schema.validate_question(q)
        self.assertTrue(any("不在选项字母" in m for _, m in msgs), msgs)

    def test_multi_needs_two_answers(self):
        q = base_exam(type="multi", typeGroup="multi")
        q["answer"] = ["A"]
        msgs = schema.validate_question(q)
        self.assertTrue(any("multi" in m for _, m in msgs), msgs)

    def test_explanation_needs_answer_basis(self):
        q = base_exam()
        q["explanation"] = "这里只有一段普通说明文字，长度足够长以便通过长度检查但缺少标记。"
        msgs = schema.validate_question(q)
        self.assertTrue(any("答案依据" in m for _, m in msgs), msgs)

    def test_textbook_may_have_empty_provenance(self):
        q = base_exam()
        q["source"] = {"text": "同济《高等数学》第七版 §1.6 极限存在准则 两个重要极限",
                       "kind": "textbook"}
        q["provenance"] = {}
        msgs = schema.validate_question(q)
        self.assertEqual([m for lv, m in msgs if lv == "error"], [])


class TestNormalize(unittest.TestCase):
    def test_normalize_fills_defaults(self):
        q = base_exam()
        q.pop("knowledgePoints", None)
        q.pop("provenance", None)
        n = schema.normalize_question(q)
        self.assertEqual(n["knowledgePoints"], ["1.6"])
        self.assertEqual(n["provenance"]["level"], None)
        self.assertEqual(n["source"]["year"], 2024)
        # 原对象不被改
        self.assertNotIn("knowledgePoints", q)

    def test_normalize_keeps_values(self):
        n = schema.normalize_question(base_exam())
        self.assertEqual(n["provenance"]["level"], "original")
        self.assertEqual(n["source"]["paper"], "数学一")


class TestFingerprint(unittest.TestCase):
    def test_same_stem_same_fingerprint(self):
        a = base_exam(stem="$\\lim_{x\\to 0}\\frac{\\sin x}{x}$")
        b = base_exam(id="other", stem="$\\lim_{x\\to 0}\\frac{\\sin x}{x}$")
        self.assertEqual(schema.fingerprint(a), schema.fingerprint(b))

    def test_whitespace_and_fullwidth_differences_collapse(self):
        a = base_exam(stem="求 $\\lim x$ 的值")
        b = base_exam(id="o2", stem="求$\\lim x$的值")
        self.assertEqual(schema.fingerprint(a), schema.fingerprint(b))

    def test_different_stem_different_fingerprint(self):
        a = base_exam(stem="甲")
        b = base_exam(id="o3", stem="乙")
        self.assertNotEqual(schema.fingerprint(a), schema.fingerprint(b))


if __name__ == "__main__":
    unittest.main(verbosity=2)
