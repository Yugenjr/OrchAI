import re

with open('tests/test_review.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace TaskAttempt constructions
text = re.sub(r'TaskAttempt\(\s*attempt_number=1,\s*execution_id="exec_1",\s*review_result="CHANGES_REQUESTED"\s*\)', 
              'TaskAttempt(attempt_id="att_1", task_id="t1", session_id="s1", objective="O", attempt_number=1, execution_id="exec_1", review_result="CHANGES_REQUESTED")', text)
text = re.sub(r'TaskAttempt\(\s*attempt_number=2,\s*execution_id="exec_2",\s*review_result="APPROVED"\s*\)',
              'TaskAttempt(attempt_id="att_2", task_id="t1", session_id="s1", objective="O", attempt_number=2, execution_id="exec_2", review_result="APPROVED")', text)
text = text.replace('TaskAttempt(attempt_number=1, execution_id="e1")', 'TaskAttempt(attempt_id="a1", task_id="t1", session_id="s1", objective="O", attempt_number=1, execution_id="e1")')
text = text.replace('TaskAttempt(attempt_number=2, execution_id="e2")', 'TaskAttempt(attempt_id="a2", task_id="t1", session_id="s1", objective="O", attempt_number=2, execution_id="e2")')
text = re.sub(r'TaskAttempt\(\s*attempt_number=1,\s*execution_id="exec_1",\s*verification_result=verification\s*\)',
              'TaskAttempt(attempt_id="att_1", task_id="t1", session_id="s1", objective="O", attempt_number=1, execution_id="exec_1", verification_result=verification)', text)

with open('tests/test_review.py', 'w', encoding='utf-8') as f:
    f.write(text)


with open('tests/test_session.py', 'r', encoding='utf-8') as f:
    text2 = f.read()

dummy = """        class DummyAdapter(AgentAdapter):
            def initialize(self): pass
            def prepare_task(self, req, snap): pass
            def capabilities(self): return []
            def execute(self): pass"""

dummy_new = """        class DummyAdapter(AgentAdapter):
            def initialize(self): pass
            def prepare_task(self, req, snap): pass
            def capabilities(self): return []
            def execute(self): pass
            def cancel(self): pass
            def health_check(self): return True
            def collect_result(self): pass
            def stream_events(self): pass"""

text2 = text2.replace(dummy, dummy_new)
with open('tests/test_session.py', 'w', encoding='utf-8') as f:
    f.write(text2)
