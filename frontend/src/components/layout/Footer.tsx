export function Footer() {
  return (
    <footer className="flex flex-col items-center justify-between gap-2 border-t border-border-subtle px-6 py-4 text-xs text-text-muted sm:flex-row">
      <p>© {new Date().getFullYear()} SchoolAI. All rights reserved.</p>
      <div className="flex items-center gap-4">
        <a href="#" className="hover:text-text-primary">Privacy</a>
        <a href="#" className="hover:text-text-primary">Terms</a>
        <a href="#" className="hover:text-text-primary">Support</a>
      </div>
    </footer>
  );
}
