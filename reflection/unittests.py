from dlai_grader.grading import test_case, print_feedback
from types import FunctionType

# Neutral inputs
_DRAFT_IN = "x"  # for generate_draft
_DRAFT_TXT = "A" * 120  # a draft with length > 100
_FEEDBACK = "B" * 60  # arbitrary feedback


# =========================
# Test 1: generate_draft
# =========================
def test_generate_draft(learner_func):
    def g():
        function_name = "generate_draft"
        cases = []
        # Type check
        t = test_case()
        if not isinstance(learner_func, FunctionType):
            t.failed = True
            t.msg = f"{function_name} has incorrect type"
            t.want = FunctionType
            t.got = type(learner_func)
            return [t]
        # Call and error handling
        try:
            out = learner_func(_DRAFT_IN)
        except Exception as e:
            t = test_case()
            t.failed = True
            t.msg = f"{function_name} raised {type(e).__name__}: {e}"
            t.want = "no exception"
            t.got = str(e)
            return [t]
        # Must return str
        t = test_case()
        if not isinstance(out, str):
            t.failed = True
            t.msg = f"{function_name} must return a str"
            t.want = str
            t.got = type(out)
            return [t]

        # Length > 100
        t = test_case()
        if len(out) <= 100:
            t.failed = True
            t.msg = (
                f"{function_name} must return text with length > 100 (got {len(out)})"
            )
            t.want = "> 100 chars"
            t.got = len(out)
        cases.append(t)
        return cases

    cases = g()
    print_feedback(cases)


# =========================
# Test 2: reflect_on_draft
# =========================
def test_reflect_on_draft(learner_func):
    def g():
        function_name = "reflect_on_draft"
        cases = []
        # Type check
        t = test_case()
        if not isinstance(learner_func, FunctionType):
            t.failed = True
            t.msg = f"{function_name} has incorrect type"
            t.want = FunctionType
            t.got = type(learner_func)
            return [t]
        # Call and error handling
        try:
            out = learner_func(_DRAFT_TXT)
        except Exception as e:
            t = test_case()
            t.failed = True
            t.msg = f"{function_name} raised {type(e).__name__}: {e}"
            t.want = "no exception"
            t.got = str(e)
            return [t]
        else:
            cases.append(t)
        # Must return str
        t = test_case()
        if not isinstance(out, str):
            t.failed = True
            t.msg = f"{function_name} must return a str"
            t.want = str
            t.got = type(out)
        else:
            cases.append(t)

        return cases

    cases = g()
    print_feedback(cases)


# =========================
# Test 3: revise_draft
# =========================
def test_revise_draft(learner_func):
    def g():
        function_name = "revise_draft"
        cases = []
        # Type check
        t = test_case()
        if not isinstance(learner_func, FunctionType):
            t.failed = True
            t.msg = f"{function_name} has incorrect type"
            t.want = FunctionType
            t.got = type(learner_func)
            return [t]
        # Call and error handling
        try:
            out = learner_func(_DRAFT_TXT, _FEEDBACK)
        except Exception as e:
            t = test_case()
            t.failed = True
            t.msg = f"{function_name} raised {type(e).__name__}: {e}"
            t.want = "no exception"
            t.got = str(e)
            return [t]
        # Must return str
        t = test_case()
        if not isinstance(out, str):
            t.failed = True
            t.msg = f"{function_name} must return a str"
            t.want = str
            t.got = type(out)
            return [t]
        # Length > 100
        t = test_case()
        if len(out) <= 100:
            t.failed = True
            t.msg = (
                f"{function_name} must return text with length > 100 (got {len(out)})"
            )
            t.want = "> 100 chars"
            t.got = len(out)
        cases.append(t)

        return cases

    cases = g()
    print_feedback(cases)
