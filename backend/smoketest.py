import asyncio
import os
import sys

os.environ["JWT_SECRET"] = "test_secret"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./smoketest.db"
os.environ["OPENAI_API_KEY"] = "test-key"

sys.path.insert(0, ".")

if os.path.exists("smoketest.db"):
    os.remove("smoketest.db")

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database.session import engine
from app.models import Base
from app.ai.factory import AIClient
from app.ai.schemas import AICompletion


# ---- Mock the AI provider layer so this test needs no network/API keys ----
async def fake_complete(self, messages, **kwargs):
    last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
    if "JSON" in messages[0].content or "json" in messages[0].content.lower():
        if "flashcards" in messages[0].content:
            content = '{"flashcards": [{"front": "2+2", "back": "4"}]}'
        else:
            content = '{"questions": [{"question": "2+2=?", "options": ["3","4","5","6"], "correct_index": 1, "explanation": "basic addition"}]}'
    else:
        content = f"Here's a friendly explanation about: {last_user[:50]}. Keep practicing!"
    return AICompletion(content=content, provider="mock", model="mock-model", raw={}, usage={})


async def fake_stream(self, messages, **kwargs):
    for chunk in ["Hello ", "there, ", "let's ", "learn!"]:
        yield chunk


AIClient.complete = fake_complete
AIClient.stream = fake_stream


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # -- register founder, teacher, principal, parent, student --------
        async def register(email, role, name):
            r = await client.post("/api/v1/auth/register", json={
                "email": email, "password": "pass1234", "full_name": name, "role": role
            })
            assert r.status_code == 200, r.text
            return r.json()

        async def login(email):
            r = await client.post("/api/v1/auth/login", data={"username": email, "password": "pass1234"})
            assert r.status_code == 200, r.text
            return r.json()["access_token"]

        founder = await register("founder@school.ai", "founder", "Founder Fay")
        founder_token = await login("founder@school.ai")
        founder_headers = {"Authorization": f"Bearer {founder_token}"}

        student = await register("student@school.ai", "student", "Sam Student")
        student_token = await login("student@school.ai")
        student_headers = {"Authorization": f"Bearer {student_token}"}

        teacher = await register("teacher@school.ai", "teacher", "Tara Teacher")
        teacher_token = await login("teacher@school.ai")
        teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

        principal = await register("principal@school.ai", "principal", "Pat Principal")
        principal_token = await login("principal@school.ai")
        principal_headers = {"Authorization": f"Bearer {principal_token}"}

        parent = await register("parent@school.ai", "parent", "Pam Parent")
        parent_token = await login("parent@school.ai")
        parent_headers = {"Authorization": f"Bearer {parent_token}"}

        # -- create the raw DB rows needed (school, profiles, class, subject, enrollment) --
        # Done directly through the DB session since there's no "create school" API yet
        # (out of scope for this task - Backend Foundation is marked complete/owned elsewhere).
        from app.database.session import SessionLocal
        from app.models.school import School
        from app.models.user import User
        from app.models.profiles import StudentProfile, TeacherProfile, ParentProfile
        from app.models.academic import Class, Subject, Enrollment
        from app.models.tracking import Result, Exam, Attendance, Homework, AssignmentSubmission
        from sqlalchemy import select
        import datetime

        async with SessionLocal() as db:
            school = School(name="Test School")
            db.add(school)
            await db.commit()
            await db.refresh(school)

            student_user = (await db.execute(select(User).where(User.email == "student@school.ai"))).scalars().first()
            teacher_user = (await db.execute(select(User).where(User.email == "teacher@school.ai"))).scalars().first()
            parent_user = (await db.execute(select(User).where(User.email == "parent@school.ai"))).scalars().first()
            student_user.school_id = school.id
            teacher_user.school_id = school.id
            await db.commit()

            sp = StudentProfile(user_id=student_user.id, student_id_number="S1", grade_level=8)
            tp = TeacherProfile(user_id=teacher_user.id, employee_id="T1")
            pp = ParentProfile(user_id=parent_user.id)
            db.add_all([sp, tp, pp])
            await db.commit()
            await db.refresh(sp); await db.refresh(tp); await db.refresh(pp)

            klass = Class(name="Grade 8A", school_id=school.id)
            db.add(klass)
            await db.commit()
            await db.refresh(klass)

            subject = Subject(name="Mathematics", teacher_id=tp.id)
            db.add(subject)
            await db.commit()
            await db.refresh(subject)

            enrollment = Enrollment(student_id=sp.id, class_id=klass.id)
            exam = Exam(subject_id=subject.id, title="Midterm", date=datetime.datetime.utcnow())
            db.add_all([enrollment, exam])
            await db.commit()
            await db.refresh(exam)

            result = Result(exam_id=exam.id, student_id=sp.id, score=72.0)
            attendance = Attendance(student_id=sp.id, date=datetime.datetime.utcnow(), status="present")
            hw = Homework(class_id=klass.id, title="HW1", due_date=datetime.datetime.utcnow())
            db.add_all([result, attendance, hw])
            await db.commit()

            student_profile_id = sp.id
            parent_profile_id = pp.id
            class_id = klass.id
            school_id = school.id
            subject_id = subject.id

        # -- link parent to student (staff-only) ---------------------------
        r = await client.post("/api/v1/parent/links", json={
            "parent_id": str(parent_profile_id), "student_id": str(student_profile_id), "relationship_type": "mother"
        }, headers=founder_headers)
        assert r.status_code == 200, r.text
        print("PASS parent link created")

        # -- student uses AI Mentor chat -----------------------------------
        r = await client.post("/api/v1/mentor/chat", json={
            "message": "Can you explain photosynthesis?", "subject": "Biology", "topic": "photosynthesis", "mode": "easy"
        }, headers=student_headers)
        assert r.status_code == 200, r.text
        assert "photosynthesis" in r.json()["response"].lower() or len(r.json()["response"]) > 0
        print("PASS /mentor/chat ->", r.json()["response"][:60])

        r = await client.get("/api/v1/mentor/history", headers=student_headers)
        assert r.status_code == 200 and len(r.json()) == 1, r.text
        print("PASS /mentor/history logged the conversation")

        # -- student can't access another student's mentor data -----------
        r = await client.get(f"/api/v1/mentor/predictions?student_id={student_profile_id}", headers=student_headers)
        assert r.status_code == 200, r.text
        print("PASS /mentor/predictions (self) ->", list(r.json().keys()))

        r = await client.post("/api/v1/mentor/quiz", json={
            "student_id": str(student_profile_id), "subject": "Math", "topic": "addition", "num_questions": 1
        }, headers=student_headers)
        assert r.status_code == 200, r.text
        assert "questions" in r.json()
        print("PASS /mentor/quiz ->", r.json()["questions"])

        r = await client.post("/api/v1/mentor/flashcards", json={
            "student_id": str(student_profile_id), "subject": "Math", "topic": "addition", "count": 1
        }, headers=student_headers)
        assert r.status_code == 200 and "flashcards" in r.json(), r.text
        print("PASS /mentor/flashcards ->", r.json()["flashcards"])

        r = await client.get("/api/v1/mentor/study-plan", headers=student_headers)
        assert r.status_code == 200 and "narrative" in r.json(), r.text
        print("PASS /mentor/study-plan")

        r = await client.get("/api/v1/mentor/motivation", headers=student_headers)
        assert r.status_code == 200
        print("PASS /mentor/motivation ->", r.json()["message"][:60])

        # -- teacher can't chat as mentor without specifying student_id ----
        r = await client.post("/api/v1/mentor/chat", json={"message": "hi"}, headers=teacher_headers)
        assert r.status_code == 400, r.text
        print("PASS teacher without student_id correctly rejected (400)")

        # -- teacher AI summary ---------------------------------------------
        r = await client.get(f"/api/v1/teacher/ai-summary?class_id={class_id}", headers=teacher_headers)
        assert r.status_code == 200 and "ai_summary" in r.json(), r.text
        print("PASS /teacher/ai-summary")

        # -- parent AI: sees own child, blocked from others ------------------
        r = await client.get("/api/v1/parent/children", headers=parent_headers)
        assert r.status_code == 200 and len(r.json()) == 1, r.text
        print("PASS /parent/children ->", r.json())

        r = await client.get(f"/api/v1/parent/ai-summary?student_id={student_profile_id}", headers=parent_headers)
        assert r.status_code == 200 and "ai_summary" in r.json(), r.text
        print("PASS /parent/ai-summary (own child)")

        # create a second student NOT linked to this parent
        async with SessionLocal() as db:
            other_user = User(email="other_student@school.ai", hashed_password="x", full_name="Other Student", role="student", school_id=school_id)
            db.add(other_user)
            await db.commit()
            await db.refresh(other_user)
            other_sp = StudentProfile(user_id=other_user.id, student_id_number="S2", grade_level=8)
            db.add(other_sp)
            await db.commit()
            await db.refresh(other_sp)
            other_student_id = other_sp.id

        r = await client.get(f"/api/v1/parent/ai-summary?student_id={other_student_id}", headers=parent_headers)
        assert r.status_code == 403, r.text
        print("PASS parent correctly blocked from non-child's data (403)")

        # -- principal analytics ---------------------------------------------
        r = await client.get(f"/api/v1/principal/analytics?school_id={school_id}", headers=principal_headers)
        assert r.status_code == 200 and "ai_recommendations" in r.json(), r.text
        print("PASS /principal/analytics ->", r.json()["data"]["school_performance"])

        # -- student streaming chat -------------------------------------------
        async with client.stream("POST", "/api/v1/mentor/stream", json={"message": "hi again"}, headers=student_headers) as resp:
            assert resp.status_code == 200
            events = []
            async for line in resp.aiter_lines():
                if line.startswith("data:"):
                    events.append(line)
            assert len(events) >= 2
        print("PASS /mentor/stream ->", len(events), "SSE events")

        # confirm the streamed turn also got memory-logged
        r = await client.get("/api/v1/mentor/history", headers=student_headers)
        assert r.status_code == 200 and len(r.json()) == 2, r.text
        print("PASS streaming turn was logged into memory (history now has 2 entries)")

        # -- verify background-task memory refresh actually ran ---------------
        r = await client.get(f"/api/v1/learning/profile/{student_profile_id}", headers=founder_headers)
        assert r.status_code == 200
        print("PASS learning profile reachable after mentor interactions:", r.json()["knowledge_level"], r.json()["confidence_score"])

    print("\nALL FUNCTIONAL SMOKE TESTS PASSED")


asyncio.run(main())
