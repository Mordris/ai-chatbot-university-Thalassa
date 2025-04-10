// frontend/src/components/ChatWindow.jsx
import React, { useEffect, useRef } from "react";
import Message from "./Message"; // <<< Added Import
import TypingIndicator from "./TypingIndicator"; // <<< Added Import
import Box from "@mui/material/Box"; // Use Box for sx prop styling

const ChatWindow = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null); // Create a ref for the bottom element

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Scroll down whenever messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    // Use Box with sx prop for styling
    <Box
      sx={{
        padding: 2, // Use theme spacing
        backgroundColor: "primary.main", // Use theme color - adjust if needed
        opacity: 0.95, // Slight opacity adjustment maybe
        borderRadius: 2, // Use theme spacing
        minHeight: "500px", // Maintain minimum height
        maxHeight: "65vh", // Set a max height relative to viewport
        overflowY: "auto", // Enable vertical scrolling
        display: "flex",
        flexDirection: "column",
      }}
    >
      {messages.map((msg, index) => (
        // Ensure Message component receives props correctly
        <Message key={index} text={msg.text} from={msg.from} />
      ))}
      {/* Ensure TypingIndicator component is rendered correctly */}
      {isLoading && <TypingIndicator />}
      {/* Add an empty div at the end to scroll to */}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default ChatWindow;
