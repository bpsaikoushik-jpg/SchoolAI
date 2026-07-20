from app.models.base import Base
from app.models.school import School
from app.models.user import User
from app.models.profiles import StudentProfile, TeacherProfile, ParentProfile
from app.models.family import ParentStudentLink
from app.models.academic import Class, Subject, Enrollment
from app.models.tracking import Attendance, Homework, AssignmentSubmission, Exam, Result
from app.models.memory import (
    StudentMemory,
    ConversationMemory,
    LearningProfile,
    WeaknessProfile,
    QuizAttempt,
    MistakeLog,
    FrequentDoubt,
    DailyProgress,
    WeeklyProgress,
    MonthlyProgress,
    Recommendation,
)
from app.models.communication import Notification
from app.models.calendar import CalendarEvent
