import { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
    const [todos, setTodos] = useState([]);

    useEffect(() => {
        axios
            .get('http://localhost:8000/api/todos/')
            .then((res) => setTodos(res.data))
            .catch((err) => console.error(err));
    }, []);

    return (
        <div>
            <h1>Todo List</h1>
            <ul>
                {todos.map((todo) => (
                    <li key={todo.id}>
                        {todo.title} - {todo.completed ? '✅' : '❌'}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default App;
