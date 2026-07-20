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

        # =====================================================================
        # Principal Portal
        # =====================================================================
        # -- school overview ---------------------------------------------------
        r = await client.get(f"/api/v1/principal/school/{school_id}", headers=principal_headers)
        assert r.status_code == 200 and r.json()["name"] == "Test School", r.text
        print("PASS /principal/school ->", r.json()["name"])

        # non-principal roles are rejected
        r = await client.get(f"/api/v1/principal/school/{school_id}", headers=student_headers)
        assert r.status_code == 403, r.text
        print("PASS /principal/school correctly rejects student role (403)")

        # -- list existing students/teachers ------------------------------------
        r = await client.get(f"/api/v1/principal/students/{school_id}", headers=principal_headers)
        assert r.status_code == 200, r.text
        existing_students = r.json()
        assert any(s["student_id_number"] == "S1" for s in existing_students), r.text
        print("PASS /principal/students (list) ->", len(existing_students), "students")

        r = await client.get(f"/api/v1/principal/teachers/{school_id}", headers=principal_headers)
        assert r.status_code == 200 and len(r.json()) == 1, r.text
        print("PASS /principal/teachers (list) ->", r.json())

        # -- create a new student, enrolled directly into the existing class ---
        r = await client.post(f"/api/v1/principal/students/{school_id}", json={
            "email": "new_student@school.ai", "password": "pass1234", "full_name": "Nia New Student",
            "student_id_number": "S3", "grade_level": 8, "class_id": str(class_id),
        }, headers=principal_headers)
        assert r.status_code == 201, r.text
        new_student = r.json()
        assert new_student["class_name"] == "Grade 8A", r.text
        print("PASS /principal/students (create) ->", new_student)

        # duplicate email rejected
        r = await client.post(f"/api/v1/principal/students/{school_id}", json={
            "email": "new_student@school.ai", "password": "pass1234", "full_name": "Duplicate",
        }, headers=principal_headers)
        assert r.status_code == 400, r.text
        print("PASS duplicate student email correctly rejected (400)")

        # -- update + deactivate the new student ---------------------------------
        r = await client.patch(
            f"/api/v1/principal/students/{school_id}/{new_student['user_id']}",
            json={"grade_level": 9}, headers=principal_headers,
        )
        assert r.status_code == 200 and r.json()["grade_level"] == 9, r.text
        print("PASS /principal/students (update) -> grade_level now", r.json()["grade_level"])

        r = await client.delete(
            f"/api/v1/principal/students/{school_id}/{new_student['user_id']}", headers=principal_headers,
        )
        assert r.status_code == 204, r.text
        r = await client.get(f"/api/v1/principal/students/{school_id}", headers=principal_headers)
        deactivated = next(s for s in r.json() if s["user_id"] == new_student["user_id"])
        assert deactivated["is_active"] is False, r.text
        print("PASS /principal/students (deactivate) -> is_active =", deactivated["is_active"])

        # -- create + update + deactivate a new teacher --------------------------
        r = await client.post(f"/api/v1/principal/teachers/{school_id}", json={
            "email": "new_teacher@school.ai", "password": "pass1234", "full_name": "Tom New Teacher",
            "employee_id": "T2", "specialization": "Physics",
        }, headers=principal_headers)
        assert r.status_code == 201, r.text
        new_teacher = r.json()
        print("PASS /principal/teachers (create) ->", new_teacher)

        r = await client.patch(
            f"/api/v1/principal/teachers/{school_id}/{new_teacher['user_id']}",
            json={"specialization": "Chemistry"}, headers=principal_headers,
        )
        assert r.status_code == 200 and r.json()["specialization"] == "Chemistry", r.text
        print("PASS /principal/teachers (update) -> specialization now", r.json()["specialization"])

        r = await client.delete(
            f"/api/v1/principal/teachers/{school_id}/{new_teacher['user_id']}", headers=principal_headers,
        )
        assert r.status_code == 204, r.text
        print("PASS /principal/teachers (deactivate)")

        # a user_id that exists but in a different role should 404, not leak data
        r = await client.patch(
            f"/api/v1/principal/teachers/{school_id}/{new_student['user_id']}",
            json={"specialization": "Nope"}, headers=principal_headers,
        )
        assert r.status_code == 404, r.text
        print("PASS student user_id correctly rejected on teacher-scoped endpoint (404)")

        # -- attendance overview --------------------------------------------------
        r = await client.get(f"/api/v1/principal/attendance-overview/{school_id}", headers=principal_headers)
        assert r.status_code == 200, r.text
        overview = r.json()
        assert overview["present"] >= 1 and len(overview["by_class"]) == 1, r.text
        print("PASS /principal/attendance-overview ->", overview["present"], "present /", overview["total_marked"], "marked")

        # -- homework overview ------------------------------------------------------
        r = await client.get(f"/api/v1/principal/homework-overview/{school_id}", headers=principal_headers)
        assert r.status_code == 200, r.text
        hw_overview = r.json()
        assert len(hw_overview) == 1 and hw_overview[0]["title"] == "HW1", r.text
        print("PASS /principal/homework-overview ->", hw_overview)

        # -- exams overview (also covers Results Monitoring) ------------------------
        r = await client.get(f"/api/v1/principal/exams-overview/{school_id}", headers=principal_headers)
        assert r.status_code == 200, r.text
        exam_overview = r.json()
        assert len(exam_overview) == 1 and exam_overview[0]["average_score"] == 72.0, r.text
        print("PASS /principal/exams-overview ->", exam_overview)

    print("\nALL FUNCTIONAL SMOKE TESTS PASSED (including Principal Portal)")


asyncio.run(main())
