import { Link } from 'react-router-dom';
import { Button } from '../components/Button';
import { motion } from 'framer-motion';

export const LandingPage = () => {
  return (
    <div className="relative overflow-hidden bg-slate-950 text-white">
      {/* Background Orbs */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob" />
      <div className="absolute top-0 -right-4 w-72 h-72 bg-emerald-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000" />
      
      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
        <div className="text-center">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8"
          >
            Empowering Every Student with <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
              Personalized AI Mentorship
            </span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-slate-400 max-w-3xl mx-auto mb-12"
          >
            SchoolAI is the first platform that adapts to every student's unique learning style, emotional intelligence, and academic goals.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex flex-col sm:flex-row justify-center gap-6"
          >
            <Link to="/login">
              <Button size="lg" className="w-full sm:w-auto">Enter Platform</Button>
            </Link>
            <Button size="lg" variant="outline" className="w-full sm:w-auto">Watch Demo</Button>
          </motion.div>
        </div>

        {/* Features Grid */}
        <div className="mt-32 grid md:grid-cols-3 gap-8">
          {[
            { title: 'Individual Understanding', desc: 'AI that builds a deep cognitive profile for every student.' },
            { title: 'Real-time Guidance', desc: '24/7 support for academic and emotional growth.' },
            { title: 'Teacher Insights', desc: 'Powerful analytics that help teachers focus where it matters most.' }
          ].map((feature, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6 + i * 0.1 }}
              className="p-8 bg-slate-900/50 border border-slate-800 rounded-3xl hover:border-blue-500/50 transition-colors"
            >
              <h3 className="text-2xl font-bold mb-4">{feature.title}</h3>
              <p className="text-slate-400 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
};
