// frontend/src/App.jsx
import React, { useState, useEffect } from "react";
import {
  Container,
  TextField,
  Button,
  Snackbar,
  Box,
  Stack,
  CssBaseline,
  ThemeProvider,
} from "@mui/material"; // Ensure all MUI components are imported

// Import local components
import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import WelcomeModal from "./components/WelcomeModal";

// Import custom hook and theme
import useChat from "./hooks/useChat";
import theme from "./styles/theme"; // Assuming theme.js is in styles folder

// Removed global.css import as CssBaseline and ThemeProvider handle base styles

const App = () => {
  // State for modal visibility
  const [isModalOpen, setModalOpen] = useState(true);

  // State hooks for input and error messages (These were likely missing in the version ESLint saw)
  const [input, setInput] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // Custom hook for chat logic (Provides messages, sendMessage, isLoading)
  const { messages, sendMessage, isLoading } = useChat();

  // Auto-close modal effect
  useEffect(() => {
    const timer = setTimeout(() => {
      setModalOpen(false);
    }, 3000); // Close after 3 seconds
    return () => clearTimeout(timer); // Cleanup timer on unmount
  }, []); // Run only once on mount

  // Handler for sending messages
  const handleSendMessage = () => {
    const MAX_LENGTH = 200; // Consistent max length
    if (input.trim() && input.length <= MAX_LENGTH) {
      sendMessage(input); // Call function from useChat hook
      setInput(""); // Clear input field
      setErrorMessage(""); // Clear any previous error
    } else if (!input.trim()) {
      // Optionally provide feedback for empty input attempt
      // setErrorMessage("Please type a message.");
    } else {
      // Exceeds max length
      setErrorMessage(`Message cannot exceed ${MAX_LENGTH} characters.`);
    }
  };

  // Handler for Enter key press
  const handleKeyPress = (event) => {
    // Send on Enter press, but allow Shift+Enter for newlines
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault(); // Prevent default newline behavior in TextField
      handleSendMessage();
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Apply baseline styles and background from theme */}
      <Container
        maxWidth="md"
        sx={{
          display: "flex",
          flexDirection: "column",
          height: "100vh", // Full viewport height
          pt: 2, // Padding top
          pb: 2, // Padding bottom
        }}
      >
        <Header />

        {/* Chat window takes up available space */}
        <Box
          sx={{
            flexGrow: 1,
            overflow: "hidden",
            mb: 2,
            display: "flex",
            flexDirection: "column",
          }}
        >
          <ChatWindow messages={messages} isLoading={isLoading} />
        </Box>

        {/* Welcome modal */}
        <WelcomeModal open={isModalOpen} onClose={() => setModalOpen(false)} />

        {/* Input area using Stack for better layout */}
        <Stack direction="row" spacing={1} alignItems="flex-start">
          {" "}
          {/* Align items start for multiline */}
          <TextField
            label="Type a message"
            variant="outlined"
            fullWidth
            multiline // Enable multiline input
            maxRows={4} // Limit vertical expansion
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            helperText={errorMessage}
            error={!!errorMessage}
            sx={{ flexGrow: 1 }} // TextField grows to fill space
            disabled={isLoading} // Optionally disable input while loading
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSendMessage}
            disabled={isLoading || !input.trim()} // Disable if loading or input is empty/whitespace
            sx={{
              height: "fit-content",
              alignSelf: "flex-end",
              mb: errorMessage ? 2.5 : 0,
            }} // Align button nicely with multiline textfield
          >
            Send
          </Button>
        </Stack>

        {/* Snackbar for error display */}
        <Snackbar
          open={!!errorMessage}
          autoHideDuration={4000}
          onClose={() => setErrorMessage("")}
          message={errorMessage}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        />
      </Container>
    </ThemeProvider>
  );
};

export default App;
