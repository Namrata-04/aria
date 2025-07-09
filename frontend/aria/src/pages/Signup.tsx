import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Brain } from 'lucide-react';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!name || !email || !password || !confirm) {
      setError('Please fill in all fields.');
      return;
    }
    if (!/^[^@\s]+@((gmail|yahoo|outlook|hotmail|icloud|protonmail|zoho)\.com|[^@\s]+\.(edu|org))$/.test(email)) {
      setError('Please enter a valid email address (gmail, yahoo, outlook, hotmail, icloud, protonmail, zoho, .edu, or .org).');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }
    localStorage.setItem('aria_logged_in', 'true');
    setSuccess('Signup successful! Redirecting to home...');
    setTimeout(() => navigate('/home'), 1200);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-amber-50 via-white to-teal-50">
      <div className="flex w-full max-w-4xl min-h-[600px] bg-white/80 rounded-2xl shadow-xl overflow-hidden border border-amber-100">
        {/* Left: Signup Card */}
        <div className="flex-1 flex flex-col justify-center px-10 py-12 relative">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-teal-600 rounded-full flex items-center justify-center shadow">
              <Brain className="w-7 h-7 text-white" />
            </div>
          </div>
          {/* Login button */}
          <div className="absolute top-6 right-10">
            <Link to="/login">
              <button className="px-4 py-1 rounded-full border border-teal-200 text-teal-700 font-semibold hover:bg-teal-50 transition text-sm">Login</button>
            </Link>
          </div>
          {/* Welcome */}
          <h2 className="text-3xl font-bold text-teal-700 mb-2 text-center tracking-wide">CREATE ACCOUNT</h2>
          <p className="text-gray-600 text-center mb-8 max-w-xs mx-auto">
            
          </p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Name"
              className="w-full border border-teal-200 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-400 bg-white"
              value={name}
              onChange={e => setName(e.target.value)}
              required
            />
            <input
              type="email"
              placeholder="Email"
              className="w-full border border-teal-200 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-400 bg-white"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              className="w-full border border-teal-200 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-400 bg-white"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Confirm Password"
              className="w-full border border-teal-200 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-400 bg-white"
              value={confirm}
              onChange={e => setConfirm(e.target.value)}
              required
            />
            {error && <div className="text-red-500 text-sm text-center">{error}</div>}
            {success && <div className="text-green-600 text-sm text-center">{success}</div>}
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-teal-500 to-teal-600 text-white py-2 rounded font-semibold hover:from-teal-600 hover:to-teal-700 transition text-lg mt-2"
            >
              Continue
            </button>
          </form>
          {/* Divider */}
          <div className="flex items-center my-6">
            <div className="flex-1 h-px bg-teal-100" />
            <span className="mx-3 text-gray-400 text-sm">OR</span>
            <div className="flex-1 h-px bg-teal-100" />
          </div>
          {/* Social signup buttons (Google, Apple only) */}
          <div className="flex justify-center gap-3 mb-4">
            <button className="w-10 h-10 rounded-full border border-gray-200 flex items-center justify-center hover:bg-gray-50 transition" title="Google">
              <span className="text-lg">G</span>
            </button>
            <button className="w-10 h-10 rounded-full border border-gray-200 flex items-center justify-center hover:bg-gray-50 transition" title="Apple">
              <span className="text-lg"></span>
            </button>
          </div>
          {/* Terms */}
          <div className="text-xs text-gray-400 text-center mt-2">
            By proceeding, you agree to our <a href="#" className="underline hover:text-teal-600">Terms of use</a>.<br />
            Read our <a href="#" className="underline hover:text-teal-600">Privacy Policy</a>
          </div>
        </div>
        {/* Right: Abstract/Gradient Background */}
        <div className="hidden md:block flex-1 bg-gradient-to-br from-teal-100 via-amber-50 to-white relative">
          <div className="absolute inset-0">
            <svg width="100%" height="100%" viewBox="0 0 600 600" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="400" cy="200" r="200" fill="#99f6e4" fillOpacity="0.25" />
              <circle cx="200" cy="400" r="180" fill="#fde68a" fillOpacity="0.18" />
              <circle cx="300" cy="300" r="120" fill="#5eead4" fillOpacity="0.12" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
} 