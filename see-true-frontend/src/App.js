// src/App.js
import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import CsvUpload from './components/CsvUpload';

// Create a custom theme (optional)
const theme = createTheme({
    palette: {
        mode: 'light',
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <CsvUpload />
        </ThemeProvider>
    );
}

export default App;
