import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom'; // Importa MemoryRouter
import Players from '../pages/Players';

test('Players component renders heading', () => {
    render(
        <MemoryRouter>
            <Players />
        </MemoryRouter>,
    );

    expect(screen.getByText(/Players/i)).toBeInTheDocument();
});
