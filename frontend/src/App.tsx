import { Routes, Route, Link } from 'react-router-dom';
import Players from './pages/Players';
import Tournaments from './pages/Tournaments';
import Login from './components/Login';
import Logout from './components/Logout';

import ProtectedRoute from './components/ProtectedRoute';

function Home() {
    return <h2>Home</h2>;
}

function App() {
    return (
        <div>
            <nav>
                <Link to="/">Home</Link> | <Link to="/tournaments">Tournaments</Link> |{' '}
                <Link to="/players">Players</Link>
            </nav>

            <Routes>
                <Route path="/login" element={<Login />} />

                {/* Proteggi questa rotta */}
                <Route element={<ProtectedRoute />}>
                    <Route path="/" element={<Home />} />
                    <Route path="/tournaments" element={<Tournaments />} />
                    <Route path="/players" element={<Players />} />
                    <Route path="/logout" element={<Logout />} />
                </Route>
            </Routes>
        </div>
    );
}

export default App;
