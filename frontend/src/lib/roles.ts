import type { Role } from '../types/auth';
import {
  LayoutDashboard, BookOpen, CalendarCheck, ClipboardList, GraduationCap,
  Users, LineChart, Sparkles, CalendarDays, Baby, Receipt, Bell,
  Building2, School, ShieldCheck, Server, ScrollText, Wallet, Radio,
  FileCheck2, MessageCircle, BarChart3, FileBarChart2, Settings as SettingsIcon,
  TrendingUp as TrendingUpIcon,
  type LucideIcon,
} from 'lucide-react';

export interface NavItem {
  label: string;
  path: string;
  icon: LucideIcon;
}

export interface RoleConfig {
  role: Role;
  label: string;
  basePath: string;
  accentVar: string; // CSS var name defined in index.css theme
  nav: NavItem[];
}

export const ROLE_CONFIG: Record<Role, RoleConfig> = {
  student: {
    role: 'student',
    label: 'Student',
    basePath: '/student',
    accentVar: '--color-role-student',
    nav: [
      { label: 'Overview', path: '/student', icon: LayoutDashboard },
      { label: 'Subjects', path: '/student/subjects', icon: BookOpen },
      { label: 'Assignments', path: '/student/assignments', icon: ClipboardList },
      { label: 'Attendance', path: '/student/attendance', icon: CalendarCheck },
      { label: 'Exams', path: '/student/exams', icon: GraduationCap },
      { label: 'AI Mentor', path: '/student/ai-mentor', icon: Sparkles },
    ],
  },
  teacher: {
    role: 'teacher',
    label: 'Teacher',
    basePath: '/teacher',
    accentVar: '--color-role-teacher',
    nav: [
      { label: 'Overview', path: '/teacher', icon: LayoutDashboard },
      { label: 'My Classes', path: '/teacher/classes', icon: School },
      { label: 'Students', path: '/teacher/students', icon: Users },
      { label: 'Attendance', path: '/teacher/attendance', icon: CalendarCheck },
      { label: 'Homework', path: '/teacher/homework', icon: ClipboardList },
      { label: 'Calendar', path: '/teacher/calendar', icon: CalendarDays },
    ],
  },
  parent: {
    role: 'parent',
    label: 'Parent',
    basePath: '/parent',
    accentVar: '--color-role-parent',
    nav: [
      { label: 'Overview', path: '/parent', icon: LayoutDashboard },
      { label: 'Academic Progress', path: '/parent/progress', icon: Baby },
      { label: 'Attendance', path: '/parent/attendance', icon: CalendarCheck },
      { label: 'Homework', path: '/parent/homework', icon: ClipboardList },
      { label: 'Assignments', path: '/parent/assignments', icon: FileCheck2 },
      { label: 'Exams', path: '/parent/exams', icon: GraduationCap },
      { label: 'Results', path: '/parent/results', icon: BarChart3 },
      { label: 'Performance', path: '/parent/performance', icon: LineChart },
      { label: 'Calendar', path: '/parent/calendar', icon: CalendarDays },
      { label: 'AI Assistant', path: '/parent/ai-assistant', icon: Sparkles },
      { label: 'Communication', path: '/parent/communication', icon: MessageCircle },
      { label: 'Fee Status', path: '/parent/fees', icon: Receipt },
      { label: 'Notifications', path: '/parent/notifications', icon: Bell },
    ],
  },
  principal: {
    role: 'principal',
    label: 'Principal',
    basePath: '/principal',
    accentVar: '--color-role-principal',
    nav: [
      { label: 'School Overview', path: '/principal', icon: Building2 },
      { label: 'Students', path: '/principal/students', icon: Users },
      { label: 'Teachers', path: '/principal/teachers', icon: GraduationCap },
      { label: 'Classes', path: '/principal/classes', icon: School },
      { label: 'Attendance', path: '/principal/attendance', icon: CalendarCheck },
      { label: 'Homework', path: '/principal/homework', icon: ClipboardList },
      { label: 'Assignments', path: '/principal/assignments', icon: FileCheck2 },
      { label: 'Exams', path: '/principal/exams', icon: GraduationCap },
      { label: 'Results', path: '/principal/results', icon: BarChart3 },
      { label: 'Academic Analytics', path: '/principal/academic-analytics', icon: LineChart },
      { label: 'Performance', path: '/principal/performance', icon: TrendingUpIcon },
      { label: 'Calendar', path: '/principal/calendar', icon: CalendarDays },
      { label: 'AI Assistant', path: '/principal/ai-assistant', icon: Sparkles },
      { label: 'Reports', path: '/principal/reports', icon: FileBarChart2 },
      { label: 'Notifications', path: '/principal/notifications', icon: Bell },
      { label: 'Settings', path: '/principal/settings', icon: SettingsIcon },
    ],
  },
  admin: {
    // No dedicated brief for ADMIN — routed alongside Principal's analytics view.
    role: 'admin',
    label: 'Admin',
    basePath: '/principal',
    accentVar: '--color-role-principal',
    nav: [],
  },
  founder: {
    role: 'founder',
    label: 'Founder',
    basePath: '/founder',
    accentVar: '--color-role-founder',
    nav: [
      { label: 'Overview', path: '/founder', icon: LayoutDashboard },
      { label: 'Schools', path: '/founder/schools', icon: Building2 },
      { label: 'Student Analytics', path: '/founder/student-analytics', icon: BookOpen },
      { label: 'Teacher Analytics', path: '/founder/teacher-analytics', icon: GraduationCap },
      { label: 'Attendance Analytics', path: '/founder/attendance', icon: CalendarCheck },
      { label: 'Homework Analytics', path: '/founder/homework', icon: ClipboardList },
      { label: 'Exam Analytics', path: '/founder/exams', icon: FileCheck2 },
      { label: 'Results Analytics', path: '/founder/results', icon: BarChart3 },
      { label: 'Organization Performance', path: '/founder/analytics', icon: LineChart },
      { label: 'AI Assistant', path: '/founder/ai-assistant', icon: Sparkles },
      { label: 'Calendar', path: '/founder/calendar', icon: CalendarDays },
      { label: 'Notifications', path: '/founder/notifications', icon: Bell },
      { label: 'Reports', path: '/founder/reports', icon: FileBarChart2 },
      { label: 'Users', path: '/founder/users', icon: Users },
      { label: 'Revenue', path: '/founder/revenue', icon: Wallet },
      { label: 'AI Usage', path: '/founder/ai-usage', icon: Radio },
      { label: 'System Health', path: '/founder/system', icon: Server },
      { label: 'Logs', path: '/founder/logs', icon: ScrollText },
      { label: 'Settings', path: '/founder/settings', icon: SettingsIcon },
    ],
  },
};

export function dashboardPathForRole(role: Role): string {
  return ROLE_CONFIG[role]?.basePath ?? '/login';
}

export const ALL_ROLES: Role[] = ['student', 'teacher', 'parent', 'principal', 'admin', 'founder'];

export const ShieldCheckIcon = ShieldCheck;
