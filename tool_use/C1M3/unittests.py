from dlai_grader.grading import test_case, print_feedback
from types import FunctionType

# ===== Neutral fixtures =====
_PROMPT = "Radio observations of recurrent novae"
_DUMMY_REPORT = (
    "This is a dummy research report about recurrent novae. "
    "It should include claims that would normally require citations."
)
_MESSAGES_STYLE_INPUT = [
    {"role": "system", "content": "policy text..."},
    {"role": "user", "content": _PROMPT},
    {"role": "assistant", "content": _DUMMY_REPORT},
]


# =========================
# Test 1: generate_research_report_with_tools
# =========================
def test_generate_research_report_with_tools(learner_func):
    def g():
        function_name = "generate_research_report_with_tools"
        cases = []

        # 1) type check
        t = test_case()
        if not isinstance(learner_func, FunctionType):
            t.failed = True
            t.msg = f"{function_name} has incorrect type"
            t.want = FunctionType
            t.got = type(learner_func)
            return [t]

        # 2) call and error handling
        try:
            out = learner_func(_PROMPT)
        except Exception as e:
            t = test_case()
            t.failed = True
            t.msg = f"{function_name} raised {type(e).__name__}: {e}"
            t.want = "no exception"
            t.got = str(e)
            return [t]

        # 3) must return str
        t = test_case()
        if not isinstance(out, str):
            t.failed = True
            t.msg = f"{function_name} must return a str"
            t.want = str
            t.got = type(out)
            return [t]
        cases.append(t)

        # 4) non-trivial length
        t = test_case()
        if len((out or "").strip()) <= 50:
            t.failed = True
            t.msg = f"report text should be non-trivial (length > 50). Got {len((out or '').strip())}"
            t.want = "> 50 chars"
            t.got = len((out or "").strip())
        cases.append(t)

        return cases

    cases = g()
    print_feedback(cases)


# =========================
# Test 2: reflection_and_rewrite
# =========================
def test_reflection_and_rewrite(learner_func):
    def g():
        function_name = "reflection_and_rewrite"
        cases = []

        # 1) type check
        t = test_case()
        if not isinstance(learner_func, FunctionType):
            t.failed = True
            t.msg = f"{function_name} has incorrect type"
            t.want = FunctionType
            t.got = type(learner_func)
            return [t]

        # 2) call with raw text
        try:
            out_text = learner_func(_DUMMY_REPORT)
        except Exception as e:
            t = test_case()
            t.failed = True
            t.msg = f"{function_name} raised {type(e).__name__} with raw text: {e}"
            t.want = "no exception"
            t.got = str(e)
            return [t]

        # 3) call with messages list
        try:
            out_msgs = learner_func(_MESSAGES_STYLE_INPUT)
        except Exception as e:
            t = test_case()
            t.failed = True
            t.msg = f"{function_name} raised {type(e).__name__} with messages list: {e}"
            t.want = "no exception"
            t.got = str(e)
            return [t]

        # Validate both outputs
        for out in (out_text, out_msgs):
            # dict type
            t = test_case()
            if not isinstance(out, dict):
                t.failed = True
                t.msg = f"{function_name} must return a dict"
                t.want = dict
                t.got = type(out)
                return [t]
            cases.append(t)

            # required keys
            t = test_case()
            keys = set(out.keys())
            if not {"reflection", "revised_report"} <= keys:
                t.failed = True
                t.msg = "dict must include keys 'reflection' and 'revised_report'"
                t.want = {"reflection", "revised_report"}
                t.got = keys
                return [t]
            cases.append(t)

            # values are strings
            t = test_case()
            if not isinstance(out["reflection"], str) or not isinstance(out["revised_report"], str):
                t.failed = True
                t.msg = "'reflection' and 'revised_report' must be strings"
                t.want = "str, str"
                t.got = (type(out["reflection"]), type(out["revised_report"]))
                return [t]
            cases.append(t)

            # reflection headings
            t = test_case()
            low = out["reflection"].lower()
            expected = ["strengths", "limitations", "suggestions", "opportunities"]
            has_all = all(h in low for h in expected)
            if not has_all:
                t.failed = True
                t.msg = "reflection should mention Strengths, Limitations, Suggestions, Opportunities"
                t.want = expected
                t.got = [h for h in expected if h in low]
            cases.append(t)

            # revised_report length
            t = test_case()
            if len(out["revised_report"].strip()) <= 50:
                t.failed = True
                t.msg = "revised_report should be non-trivial (length > 50)"
                t.want = "> 50 chars"
                t.got = len(out["revised_report"].strip())
            cases.append(t)

        return cases

    cases = g()
    print_feedback(cases)


# =========================
# Test 3: convert_report_to_html
# =========================
def test_convert_report_to_html(learner_func):
    def g():
        function_name = "convert_report_to_html"
        cases = []

        # 1) type check
        t = test_case()
        if not isinstance(learner_func, FunctionType):
            t.failed = True
            t.msg = f"{function_name} has incorrect type"
            t.want = FunctionType
            t.got = type(learner_func)
            return [t]

        # 2) raw text call
        try:
            out_text = learner_func(_DUMMY_REPORT)
        except Exception as e:
            t = test_case()
            t.failed = True
            t.msg = f"{function_name} raised {type(e).__name__} with raw text: {e}"
            t.want = "no exception"
            t.got = str(e)
            return [t]

        # 3) messages list call
        try:
            out_msgs = learner_func(_MESSAGES_STYLE_INPUT)
        except Exception as e:
            t = test_case()
            t.failed = True
            t.msg = f"{function_name} raised {type(e).__name__} with messages list: {e}"
            t.want = "no exception"
            t.got = str(e)
            return [t]

        # Validate both outputs
        for out in (out_text, out_msgs):
            t = test_case()
            if not isinstance(out, str):
                t.failed = True
                t.msg = f"{function_name} must return a str"
                t.want = str
                t.got = type(out)
                return [t]
            cases.append(t)

            t = test_case()
            low = out.lower()
            looks_like_html = ("<html" in low) or ("</" in low) or ("<h1" in low) or ("<p" in low)
            if not looks_like_html:
                t.failed = True
                t.msg = "Output should look like HTML (contain <html>, <h1>, <p>, or closing tags)"
                t.want = "HTML-like string"
                t.got = out[:120]
            cases.append(t)

        return cases

    cases = g()
    print_feedback(cases)
