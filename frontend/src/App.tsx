import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/auth/LoginPage';
import { NotFoundPage } from './pages/errors/NotFoundPage';
import { UnauthorizedPage } from './pages/errors/UnauthorizedPage';

import { ProtectedRoute } from './routes/ProtectedRoute';
import { RoleRoute } from './routes/RoleRoute';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { ROLE_CONFIG } from './lib/roles';

const StudentDashboard = lazy(() => import('./pages/dashboards/student/StudentDashboard').then((m) => ({ default: m.StudentDashboard })));
const StudentSubjectsPage = lazy(() => import('./pages/dashboards/student/SubjectsPage').then((m) => ({ default: m.SubjectsPage })));
const StudentAssignmentsPage = lazy(() => import('./pages/dashboards/student/AssignmentsPage').then((m) => ({ default: m.AssignmentsPage })));
const StudentAttendancePage = lazy(() => import('./pages/dashboards/student/AttendancePage').then((m) => ({ default: m.AttendancePage })));
const StudentExamsPage = lazy(() => import('./pages/dashboards/student/ExamsPage').then((m) => ({ default: m.ExamsPage })));
const StudentAiMentorPage = lazy(() => import('./pages/dashboards/student/AiMentorPage').then((m) => ({ default: m.AiMentorPage })));
const TeacherDashboard = lazy(() => import('./pages/dashboards/teacher/TeacherDashboard').then((m) => ({ default: m.TeacherDashboard })));
const TeacherClassesPage = lazy(() => import('./pages/dashboards/teacher/ClassesPage').then((m) => ({ default: m.ClassesPage })));
const TeacherStudentsPage = lazy(() => import('./pages/dashboards/teacher/StudentsPage').then((m) => ({ default: m.StudentsPage })));
const TeacherAttendancePage = lazy(() => import('./pages/dashboards/teacher/AttendancePage').then((m) => ({ default: m.AttendancePage })));
const TeacherHomeworkPage = lazy(() => import('./pages/dashboards/teacher/HomeworkPage').then((m) => ({ default: m.HomeworkPage })));
const TeacherCalendarPage = lazy(() => import('./pages/dashboards/teacher/CalendarPage').then((m) => ({ default: m.CalendarPage })));
const ParentDashboard = lazy(() => import('./pages/dashboards/parent/ParentDashboard').then((m) => ({ default: m.ParentDashboard })));
const ParentProgressPage = lazy(() => import('./pages/dashboards/parent/ProgressPage').then((m) => ({ default: m.ProgressPage })));
const ParentAttendancePage = lazy(() => import('./pages/dashboards/parent/AttendancePage').then((m) => ({ default: m.AttendancePage })));
const ParentHomeworkPage = lazy(() => import('./pages/dashboards/parent/HomeworkPage').then((m) => ({ default: m.HomeworkPage })));
const ParentAssignmentsPage = lazy(() => import('./pages/dashboards/parent/AssignmentsPage').then((m) => ({ default: m.AssignmentsPage })));
const ParentExamsPage = lazy(() => import('./pages/dashboards/parent/ExamsPage').then((m) => ({ default: m.ExamsPage })));
const ParentResultsPage = lazy(() => import('./pages/dashboards/parent/ResultsPage').then((m) => ({ default: m.ResultsPage })));
const ParentPerformancePage = lazy(() => import('./pages/dashboards/parent/PerformancePage').then((m) => ({ default: m.PerformancePage })));
const ParentCalendarPage = lazy(() => import('./pages/dashboards/parent/CalendarPage').then((m) => ({ default: m.CalendarPage })));
const ParentAiAssistantPage = lazy(() => import('./pages/dashboards/parent/AiAssistantPage').then((m) => ({ default: m.AiAssistantPage })));
const ParentCommunicationPage = lazy(() => import('./pages/dashboards/parent/CommunicationPage').then((m) => ({ default: m.CommunicationPage })));
const ParentFeesPage = lazy(() => import('./pages/dashboards/parent/FeesPage').then((m) => ({ default: m.FeesPage })));
const ParentNotificationsPage = lazy(() => import('./pages/dashboards/parent/NotificationsPage').then((m) => ({ default: m.NotificationsPage })));
const PrincipalDashboard = lazy(() => import('./pages/dashboards/principal/PrincipalDashboard').then((m) => ({ default: m.PrincipalDashboard })));
const StudentManagementPage = lazy(() => import('./pages/dashboards/principal/StudentManagementPage').then((m) => ({ default: m.StudentManagementPage })));
const TeacherManagementPage = lazy(() => import('./pages/dashboards/principal/TeacherManagementPage').then((m) => ({ default: m.TeacherManagementPage })));
const ClassManagementPage = lazy(() => import('./pages/dashboards/principal/ClassManagementPage').then((m) => ({ default: m.ClassManagementPage })));
const AttendanceAnalyticsPage = lazy(() => import('./pages/dashboards/principal/AttendanceAnalyticsPage').then((m) => ({ default: m.AttendanceAnalyticsPage })));
const HomeworkMonitoringPage = lazy(() => import('./pages/dashboards/principal/HomeworkMonitoringPage').then((m) => ({ default: m.HomeworkMonitoringPage })));
const AssignmentMonitoringPage = lazy(() => import('./pages/dashboards/principal/AssignmentMonitoringPage').then((m) => ({ default: m.AssignmentMonitoringPage })));
const ExamMonitoringPage = lazy(() => import('./pages/dashboards/principal/ExamMonitoringPage').then((m) => ({ default: m.ExamMonitoringPage })));
const ResultsMonitoringPage = lazy(() => import('./pages/dashboards/principal/ResultsMonitoringPage').then((m) => ({ default: m.ResultsMonitoringPage })));
const AcademicAnalyticsPage = lazy(() => import('./pages/dashboards/principal/TeacherAnalyticsPage').then((m) => ({ default: m.TeacherAnalyticsPage })));
const PerformanceAnalyticsPage = lazy(() => import('./pages/dashboards/principal/PerformanceAnalyticsPage').then((m) => ({ default: m.PerformanceAnalyticsPage })));
const PrincipalCalendarPage = lazy(() => import('./pages/dashboards/principal/CalendarPage').then((m) => ({ default: m.CalendarPage })));
const PrincipalAiAssistantPage = lazy(() => import('./pages/dashboards/principal/AiAssistantPage').then((m) => ({ default: m.AiAssistantPage })));
const ReportsOverviewPage = lazy(() => import('./pages/dashboards/principal/ReportsOverviewPage').then((m) => ({ default: m.ReportsOverviewPage })));
const PrincipalSettingsPage = lazy(() => import('./pages/dashboards/principal/SettingsPage').then((m) => ({ default: m.SettingsPage })));
const PrincipalNotificationsPage = lazy(() => import('./pages/dashboards/principal/NotificationsPage').then((m) => ({ default: m.NotificationsPage })));
const FounderDashboard = lazy(() => import('./pages/dashboards/founder/FounderDashboard').then((m) => ({ default: m.FounderDashboard })));
const SchoolsPage = lazy(() => import('./pages/dashboards/founder/SchoolsPage').then((m) => ({ default: m.SchoolsPage })));
const FounderStudentAnalyticsPage = lazy(() => import('./pages/dashboards/founder/StudentAnalyticsPage').then((m) => ({ default: m.StudentAnalyticsPage })));
const FounderTeacherAnalyticsPage = lazy(() => import('./pages/dashboards/founder/TeacherAnalyticsPage').then((m) => ({ default: m.TeacherAnalyticsPage })));
const FounderAttendanceAnalyticsPage = lazy(() => import('./pages/dashboards/founder/AttendanceAnalyticsPage').then((m) => ({ default: m.AttendanceAnalyticsPage })));
const HomeworkAnalyticsPage = lazy(() => import('./pages/dashboards/founder/HomeworkAnalyticsPage').then((m) => ({ default: m.HomeworkAnalyticsPage })));
const ExamAnalyticsPage = lazy(() => import('./pages/dashboards/founder/ExamAnalyticsPage').then((m) => ({ default: m.ExamAnalyticsPage })));
const ResultsAnalyticsPage = lazy(() => import('./pages/dashboards/founder/ResultsAnalyticsPage').then((m) => ({ default: m.ResultsAnalyticsPage })));
const FounderAiAssistantPage = lazy(() => import('./pages/dashboards/founder/AiAssistantPage').then((m) => ({ default: m.AiAssistantPage })));
const FounderCalendarPage = lazy(() => import('./pages/dashboards/founder/CalendarPage').then((m) => ({ default: m.CalendarPage })));
const FounderNotificationsPage = lazy(() => import('./pages/dashboards/founder/NotificationsPage').then((m) => ({ default: m.NotificationsPage })));
const FounderReportsOverviewPage = lazy(() => import('./pages/dashboards/founder/ReportsOverviewPage').then((m) => ({ default: m.ReportsOverviewPage })));
const FounderSettingsPage = lazy(() => import('./pages/dashboards/founder/SettingsPage').then((m) => ({ default: m.SettingsPage })));
const UsersPage = lazy(() => import('./pages/dashboards/founder/UsersPage').then((m) => ({ default: m.UsersPage })));
const RevenuePage = lazy(() => import('./pages/dashboards/founder/RevenuePage').then((m) => ({ default: m.RevenuePage })));
const AiUsagePage = lazy(() => import('./pages/dashboards/founder/AiUsagePage').then((m) => ({ default: m.AiUsagePage })));
const SystemHealthPage = lazy(() => import('./pages/dashboards/founder/SystemHealthPage').then((m) => ({ default: m.SystemHealthPage })));
const LogsPage = lazy(() => import('./pages/dashboards/founder/LogsPage').then((m) => ({ default: m.LogsPage })));
const PlatformAnalyticsPage = lazy(() => import('./pages/dashboards/founder/PlatformAnalyticsPage').then((m) => ({ default: m.PlatformAnalyticsPage })));


function App() {
  return (
    <div className="min-h-screen bg-canvas text-text-primary font-sans">
      <AnimatePresence mode="wait">
        <Suspense fallback={<div className="flex min-h-screen items-center justify-center text-sm text-text-muted">Loading…</div>}>
        <Routes>
          {/* Public */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />

          {/* Authenticated */}
          <Route element={<ProtectedRoute />}>
            <Route path="/unauthorized" element={<UnauthorizedPage />} />

            {/* Student portal */}
            <Route element={<RoleRoute allowed={['student']} />}>
              <Route element={<DashboardLayout config={ROLE_CONFIG.student} />}>
                <Route path="/student" element={<StudentDashboard />} />
                <Route path="/student/subjects" element={<StudentSubjectsPage />} />
                <Route path="/student/assignments" element={<StudentAssignmentsPage />} />
                <Route path="/student/attendance" element={<StudentAttendancePage />} />
                <Route path="/student/exams" element={<StudentExamsPage />} />
                <Route path="/student/ai-mentor" element={<StudentAiMentorPage />} />
              </Route>
            </Route>

            {/* Teacher portal */}
            <Route element={<RoleRoute allowed={['teacher', 'principal', 'admin', 'founder']} />}>
              <Route element={<DashboardLayout config={ROLE_CONFIG.teacher} />}>
                <Route path="/teacher" element={<TeacherDashboard />} />
                <Route path="/teacher/classes" element={<TeacherClassesPage />} />
                <Route path="/teacher/students" element={<TeacherStudentsPage />} />
                <Route path="/teacher/attendance" element={<TeacherAttendancePage />} />
                <Route path="/teacher/homework" element={<TeacherHomeworkPage />} />
                <Route path="/teacher/calendar" element={<TeacherCalendarPage />} />
              </Route>
            </Route>

            {/* Parent portal */}
            <Route element={<RoleRoute allowed={['parent']} />}>
              <Route element={<DashboardLayout config={ROLE_CONFIG.parent} />}>
                <Route path="/parent" element={<ParentDashboard />} />
                <Route path="/parent/progress" element={<ParentProgressPage />} />
                <Route path="/parent/attendance" element={<ParentAttendancePage />} />
                <Route path="/parent/homework" element={<ParentHomeworkPage />} />
                <Route path="/parent/assignments" element={<ParentAssignmentsPage />} />
                <Route path="/parent/exams" element={<ParentExamsPage />} />
                <Route path="/parent/results" element={<ParentResultsPage />} />
                <Route path="/parent/performance" element={<ParentPerformancePage />} />
                <Route path="/parent/calendar" element={<ParentCalendarPage />} />
                <Route path="/parent/ai-assistant" element={<ParentAiAssistantPage />} />
                <Route path="/parent/communication" element={<ParentCommunicationPage />} />
                <Route path="/parent/fees" element={<ParentFeesPage />} />
                <Route path="/parent/notifications" element={<ParentNotificationsPage />} />
              </Route>
            </Route>

            {/* Principal portal (also reachable by admin/founder for oversight) */}
            <Route element={<RoleRoute allowed={['principal', 'admin', 'founder']} />}>
              <Route element={<DashboardLayout config={ROLE_CONFIG.principal} />}>
                <Route path="/principal" element={<PrincipalDashboard />} />
                <Route path="/principal/students" element={<StudentManagementPage />} />
                <Route path="/principal/teachers" element={<TeacherManagementPage />} />
                <Route path="/principal/classes" element={<ClassManagementPage />} />
                <Route path="/principal/attendance" element={<AttendanceAnalyticsPage />} />
                <Route path="/principal/homework" element={<HomeworkMonitoringPage />} />
                <Route path="/principal/assignments" element={<AssignmentMonitoringPage />} />
                <Route path="/principal/exams" element={<ExamMonitoringPage />} />
                <Route path="/principal/results" element={<ResultsMonitoringPage />} />
                <Route path="/principal/academic-analytics" element={<AcademicAnalyticsPage />} />
                <Route path="/principal/performance" element={<PerformanceAnalyticsPage />} />
                <Route path="/principal/calendar" element={<PrincipalCalendarPage />} />
                <Route path="/principal/ai-assistant" element={<PrincipalAiAssistantPage />} />
                <Route path="/principal/reports" element={<ReportsOverviewPage />} />
                <Route path="/principal/notifications" element={<PrincipalNotificationsPage />} />
                <Route path="/principal/settings" element={<PrincipalSettingsPage />} />
              </Route>
            </Route>

            {/* Founder / super-admin portal */}
            <Route element={<RoleRoute allowed={['founder']} />}>
              <Route element={<DashboardLayout config={ROLE_CONFIG.founder} />}>
                <Route path="/founder" element={<FounderDashboard />} />
                <Route path="/founder/schools" element={<SchoolsPage />} />
                <Route path="/founder/student-analytics" element={<FounderStudentAnalyticsPage />} />
                <Route path="/founder/teacher-analytics" element={<FounderTeacherAnalyticsPage />} />
                <Route path="/founder/attendance" element={<FounderAttendanceAnalyticsPage />} />
                <Route path="/founder/homework" element={<HomeworkAnalyticsPage />} />
                <Route path="/founder/exams" element={<ExamAnalyticsPage />} />
                <Route path="/founder/results" element={<ResultsAnalyticsPage />} />
                <Route path="/founder/ai-assistant" element={<FounderAiAssistantPage />} />
                <Route path="/founder/calendar" element={<FounderCalendarPage />} />
                <Route path="/founder/notifications" element={<FounderNotificationsPage />} />
                <Route path="/founder/reports" element={<FounderReportsOverviewPage />} />
                <Route path="/founder/settings" element={<FounderSettingsPage />} />
                <Route path="/founder/users" element={<UsersPage />} />
                <Route path="/founder/revenue" element={<RevenuePage />} />
                <Route path="/founder/ai-usage" element={<AiUsagePage />} />
                <Route path="/founder/system" element={<SystemHealthPage />} />
                <Route path="/founder/logs" element={<LogsPage />} />
                <Route path="/founder/analytics" element={<PlatformAnalyticsPage />} />
              </Route>
            </Route>
          </Route>

          <Route path="*" element={<NotFoundPage />} />
        </Routes>
        </Suspense>
      </AnimatePresence>
    </div>
  );
}

export default App;
