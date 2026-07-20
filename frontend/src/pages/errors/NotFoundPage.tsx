import { Link } from 'react-router-dom';
import { Button } from '../../components/Button';
import { Compass } from 'lucide-react';

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-canvas px-4 text-center">
      <div className="grid h-14 w-14 place-items-center rounded-full bg-sunken text-text-muted">
        <Compass size={26} />
      </div>
      <h1 className="text-3xl font-bold text-text-primary">Page not found</h1>
      <p className="max-w-sm text-text-muted">The page you're looking for doesn't exist or has moved.</p>
      <Link to="/"><Button>Back to home</Button></Link>
    </div>
  );
}
