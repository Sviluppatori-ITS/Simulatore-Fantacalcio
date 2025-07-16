import { Routes, Route, Link } from 'react-router-dom';
import Players from './pages/Players'; // importa il componente vero

function Home() {
    return <h2>Home</h2>;
}

function Tournaments() {
    return <h2>Tournaments</h2>;
}

function App() {
    return (
        <div>
            <nav>
                <Link to="/">Home</Link> | <Link to="/tournaments">Tournaments</Link> |{' '}
                <Link to="/players">Players</Link>
            </nav>

            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/tournaments" element={<Tournaments />} />
                <Route path="/players" element={<Players />} /> {/* usa il componente importato */}
            </Routes>
        </div>
    );
}

export default App;
