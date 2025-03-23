import React, { useState } from "react";
import { Container, TextField, Button, Snackbar } from "@mui/material";
import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import WelcomeModal from "./components/WelcomeModal";
import useChat from "./hooks/useChat";
import "./styles/global.css";

const App = () => {
  const [isModalOpen, setModalOpen] = useState(true);
  const { messages, sendMessage, isLoading } = useChat();
  const [input, setInput] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleSendMessage = () => {
    if (input.trim() && input.length <= 100) {
      sendMessage(input); // Send the message
      setInput(""); // Clear the input field
      setErrorMessage(""); // Clear any previous error message
    } else if (input.length > 100) {
      setErrorMessage("Message cannot exceed 100 characters.");
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && input.trim() && input.length <= 200) {
      handleSendMessage();
    }
  };

  return (
    <Container
      maxWidth="md"
      style={{ backgroundColor: "#efeae4", height: "100vh" }}
    >
      <Header />
      <ChatWindow messages={messages} isLoading={isLoading} />
      <WelcomeModal open={isModalOpen} onClose={() => setModalOpen(false)} />
      <div style={{ paddingTop: "20px", textAlign: "center" }}>
        <TextField
          label="Type a message"
          variant="outlined"
          fullWidth
          value={input}
          onChange={(e) => setInput(e.target.value)} // Update input value
          onKeyPress={handleKeyPress} // Trigger sending on Enter key press
          helperText={errorMessage} // Show error message if any
          error={!!errorMessage} // Highlight error in the text field
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleSendMessage} // Handle message send
          style={{ marginTop: "10px" }}
        >
          Send
        </Button>
      </div>
      {/* Snackbar to display the error message */}
      <Snackbar
        open={!!errorMessage}
        autoHideDuration={3000}
        onClose={() => setErrorMessage("")}
        message={errorMessage}
      />
    </Container>
  );
};

export default App;
