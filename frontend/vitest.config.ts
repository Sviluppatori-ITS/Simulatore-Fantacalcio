import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: './src/setupTests.ts',
        reporters: ['default', ['junit', { outputFile: 'test-results/results.xml' }]],
        coverage: {
            provider: 'v8',
            reporter: ['text', 'lcov', 'json', 'html'],
            reportsDirectory: 'coverage',
        },
    },
});
