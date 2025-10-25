import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Home } from './pages/Home';
import { ProteinPage } from './pages/ProteinPage';
import { DiseasePage } from './pages/DiseasePage';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#3498db',
    },
    secondary: {
      main: '#e74c3c',
    },
    background: {
      default: '#f8f9fa',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
        },
      },
    },
  },
});

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/protein/:id" element={<ProteinPage />} />
            <Route path="/disease/:id" element={<DiseasePage />} />
          </Routes>
        </Router>
      </ThemeProvider>
    </ErrorBoundary>
  );
};
