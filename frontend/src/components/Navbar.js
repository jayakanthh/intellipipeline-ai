import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar bg-base-100 shadow-lg">
      <div className="container mx-auto">
        <div className="flex-none">
          <Link to="/" className="btn btn-ghost normal-case text-xl">
            🧠 AI Data Engineer
          </Link>
        </div>
        <div className="flex-1">
          <ul className="menu menu-horizontal px-1">
            <li><Link to="/">Upload</Link></li>
            <li><Link to="/analysis">Analysis</Link></li>
            <li><Link to="/pipeline">Pipeline</Link></li>
            <li><Link to="/model">Model</Link></li>
            <li><Link to="/deploy">Deploy</Link></li>
            <li><Link to="/dashboard">Dashboard</Link></li>
          </ul>
        </div>
        <div className="flex-none">
          <button className="btn btn-primary">New Project</button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;