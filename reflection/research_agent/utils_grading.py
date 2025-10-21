# utils_grading.py

def test_generate_draft(generate_draft_fn):
    try:
        output = generate_draft_fn("What are the benefits of exercise?")
        assert isinstance(output, str) and len(output) > 100, "Output is too short or not a string."
        return True, "✅ test_generate_draft passed"
    except Exception as e:
        return False, f"❌ test_generate_draft failed: {e}"

def test_reflect_on_draft(reflect_on_draft_fn, draft_text):
    try:
        output = reflect_on_draft_fn(draft_text)
        assert isinstance(output, str), "Reflection doesn't look like feedback."
        return True, "✅ test_reflect_on_draft passed"
    except Exception as e:
        return False, f"❌ test_reflect_on_draft failed: {e}"

def test_revise_draft(revise_draft_fn, draft_text, feedback_text):
    try:
        output = revise_draft_fn(draft_text, feedback_text)
        assert isinstance(output, str) and len(output) > 100, "Revision too short or not string."
        return True, "✅ test_revise_draft passed"
    except Exception as e:
        return False, f"❌ test_revise_draft failed: {e}"

def run_all_tests(generate_draft_fn, reflect_on_draft_fn, revise_draft_fn):
    sample_prompt = "What are the benefits of exercise?"
    draft = generate_draft_fn(sample_prompt)
    feedback = reflect_on_draft_fn(draft)

    results = []
    results.append(test_generate_draft(generate_draft_fn))
    results.append(test_reflect_on_draft(reflect_on_draft_fn, draft))
    results.append(test_revise_draft(revise_draft_fn, draft, feedback))

    for success, msg in results:
        print(msg)

    passed = sum(1 for x, _ in results if x)
    total = len(results)
    print(f"\n✅ {passed}/{total} tests passed.")
